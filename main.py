import backtrader as bt
import datetime as dt

from strategy import TestStrategy


class MyBuySell(bt.observers.BuySell):
  plotlines = dict(
    buy=dict(marker='^', markersize=8.0, color='lime', fillstyle='full'),
    sell=dict(marker='v', markersize=8.0, color='maroon', fillstyle='full')
  )


if __name__ == "__main__":

  cerebro = bt.Cerebro()

  cerebro.addstrategy(TestStrategy)

  btc_data = bt.feeds.YahooFinanceCSVData(
    dataname="./data/BTC-USD.csv",
    reverse=False
  )

  cerebro.adddata(btc_data)

  cerebro.broker.setcash(100000)

  print(f'Starting Portfolio Value: {cerebro.broker.getvalue()}')

  bt.observers.BuySell = MyBuySell
  cerebro.run()

  print(f'Final Portfolio Value: {cerebro.broker.getvalue()}')

  cerebro.plot(style='candlestick')
