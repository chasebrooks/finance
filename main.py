import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
import pandas_datareader.data as web
import os.path
import bs4 as bs
import pickle
import requests
import time
from random import randint

style.use('ggplot')

class Stock(object):

    def __init__(self):
        self.tickers = []
        self.start = dt.datetime.strptime('2000-01-01', '%Y-%m-%d')
        self.end = dt.datetime.strptime('2016-12-31', '%Y-%m-%d')

    def get_stocks(self, ticker, start='2000-01-01', end='2016-12-31'):
        '''
        :param ticker: the NYSE ticker of a company
        :param start: start date
        :param end: end date
        :return: date, open price, high price, low price, close price, adjusted close, and volume
        '''

        ticker = ticker.lower()
        start = dt.datetime.strptime(start, '%Y-%m-%d')
        end = dt.datetime.strptime(end, '%Y-%m-%d')

        file_name = 'resources/'+ticker+'.csv'
        API_KEY = 'HSDHL36UBPVS41O8'
        r = requests.get(
            'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=' + API_KEY)
        if (r.status_code == 200):
            df = pd.DataFrame.from_dict((r.json()['Time Series (Daily)'])).T
            df.columns = ['open', 'high', 'low', 'close', 'adjusted close', 'volume', 'dividend amount',
                          'split coefficient']
            return df
        else:
            return 'bad request'

    def graph_stock(self, ticker, start='2000-01-01', end='2016-12-31'):
        df = self.get_stocks(ticker, start, end)

        df_ohlc = df['close'].resample('10D').ohlc()
        df_volume = df['volume'].resample('10D').sum()

        #resets the index to be numerical instead of the dates
        df_ohlc.reset_index(inplace=True)
        df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)

        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
        ax1.xaxis_date()

        candlestick_ohlc(ax1, df_ohlc.values, width=2, colorup='g')
        ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)

        plt.show()


    def get_sp500(self):
        headers = {'User-Agent': 'Chrome) ',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Accept-Language': 'en-US,en;q=0.8'}
        resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=headers)
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text
            self.tickers.append(ticker)
        with open('resources/sp500tickers.pickle', 'wb') as f:
            pickle.dump(self.tickers, f)
        return self.tickers

    def get_data_from_alpha(self, reload_sp500=False, start='2000-01-01', end='2016-12-31'):
        if reload_sp500:
            tickers = self.get_sp500()
        else:
            with open('resources/sp500tickers.pickle', 'rb') as f:
                tickers = pickle.load(f)
        if not os.path.exists('resources/stock_dfs'):
            os.makedirs('resources/stock_dfs')

        for ticker in tickers[20:]:
            print(ticker)
            if not os.path.exists('resources/stock_dfs/{}.csv'.format(ticker)):
                df = self.get_stocks(ticker.replace('.', ''))
                df.to_csv('resources/stock_dfs/{}.csv'.format(ticker))
            else:
                print('Already have {}'.format(ticker))


    def compile_data(self):
        with open('sp500tickers.pickle', 'rb') as f:
            tickers = pickle.load(f)
        main_df = pd.DataFrame()

        for count, ticker in enumerate(tickers):
            df = pd.read_csv('resources/stock_dfs/{}.csv'.format(ticker))

            df.rename(columns={'adjusted close', ticker})
            df.drop(['open', 'high', 'low', 'close', 'volume', 'dividend amount', 'split coefficient'], 1, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')

            if count % 10 == 0:
                print(count)
        print(main_df.head())
        main_df.to_csv('sp500_joined_closes.csv')








cls = Stock()
print(cls.get_data_from_alpha())
#graph_stock('tsla', '2013-12-05', '2016-12-15')
#df = get_stocks('tsla', '2016-11-30', '2016-12-05')




