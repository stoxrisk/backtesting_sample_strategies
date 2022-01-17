from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import yfinance as yf
import os
import time
import json
from calendar import timegm

from tdameritradeapi import TDAmeritradeAPI
api_key = os.getenv('td_api_key')
td_api = TDAmeritradeAPI(api_key)

def strToEpoch(datestr):
    utc_time = time.strptime(datestr, "%Y-%m-%d")
    epoch_time = timegm(utc_time)
    return epoch_time*1000

def adjustDataframe(td_df):
    td_df = td_df.rename(columns={
                        'open': 'Open', 
                        'close': 'Close',
                        'high': "High",
                        'volume': 'Volume',
                        'low': 'Low'})
    return td_df

# from yahoofinancials import YahooFinancials
# symbol_yahoo_finance_interactor = YahooFinancials("SPY")
# earnings_days_data = symbol_yahoo_finance_interactor.get_historical_price_data("2018-01-01", "2022-01-01", '30m')
# import nasdaqdatalink as nq
# Yahoo Data
# data = yf.download("SPY", start="2021-12-01", end="2022-01-01",
#     interval="30m")
# print(data)

# Using TDA API
response = td_api.getPrices("SPY", 
                              "minute", 
                              "30", 
                              endDate=strToEpoch("2022-01-01"), 
                              startDate=strToEpoch("2021-12-01")).content

json_data = json.loads(response)
SPY = pd.DataFrame.from_records(json_data["candles"])
SPY = adjustDataframe(SPY)




from backtesting.test import SMA, GOOG

class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


bt = Backtest(SPY, SmaCross,
              cash=10000, commission=0,
              exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()

