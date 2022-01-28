import backtrader as bt
import datetime as dt

class TestStrategy(bt.Strategy):
  params = (
    ('maperiod', 21),
  )


  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print(f'{dt.isoformat()}, {txt}')

  def __init__(self):
    self.dataclose = self.datas[0].close
    
    self.sma = bt.indicators.MovingAverageSimple(
      self.datas[0], 
      period=self.p.maperiod
      )
    
    self.sma_slow = bt.indicators.MovingAverageSimple(
      self.datas[0], 
      period=50,
      plot=False
      )

    self.crossup = bt.indicators.CrossUp(self.sma, self.sma_slow, plot=False)

    self.rsi = bt.indicators.RSI_EMA(period = 14)

    self.boll = bt.indicators.BollingerBands(
      period=21,
      devfactor=2,
      plot=False
    )
    self.order = None

  def notify_order(self, order):
    # If order is submitted or accepted to/by broker 
    if order.status in [order.Submitted, order.Accepted]:
      return
    
    
    # If order has been completed
    if order.status in [order.Completed]:
      if order.isbuy():
        self.log('EXECUTED BUY of %.2f at PRICE: %.2f' % (order.executed.size, order.executed.price))
        self.price_position = order.executed.price
        
      
      elif order.issell():
        self.log('EXECUTED SELL of %.2f at PRICE: %.2f' % (order.executed.size, order.executed.price))
        self.price_position = None
      

    elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired, order.Partial]:
      self.log('ORDER CANCELED/MARGIN/REJECTED')
     

    
    # No pending order
    self.order = None
      

  def next(self):
    self.log(f'Close, {self.dataclose[0]}')

    # If order is pending:
    if self.order:
      print(self.order)
      print(self.price_position)
      return

    # Check if position is...
    # Close. 
    if not self.position:
      #So we buy if RSI < 30 & Price is at lower boll band
      if (self.dataclose[0] <= self.boll.bot[0]) & (self.rsi.rsi <= 30):
        self.log(f'BUY ORDER ISSUED (RSI BOLL) at, {self.dataclose[0]} \n')
        self.order = self.buy()
        return
      # Buy also if the simple MA(fast) cross up to simple MA(slow)
      elif (self.crossup == True):
        self.log(f'BUY ORDER ISSUED (CrossOver) at, {self.dataclose[0]} \n')
        self.order = self.buy()
        return
        
    # Open.
    else:
      #  So we sell if RSI > 70 & Price is at higher boll band
      if (self.dataclose[0] >= self.boll.top[0]) & (self.rsi.rsi >= 70) :
        self.log(f'SELL ORDER ISSUED (RSI BOLL) at, {self.dataclose[0]} \n')
        self.order = self.sell()
        return
      # Sell once price is over the 1.02% of SMA's prices
      elif (self.dataclose[0] > self.sma[0]) :
        self.log(f'SELL ORDER ISSUED (Take Profit) at, {self.dataclose[0]} \n')
        self.order = self.sell(exectype=bt.Order.Limit, price=(self.dataclose[0] * 1.02), valid=(self.datas[0].datetime.date(0) + dt.timedelta(days=5)))
        return
      # Stop Loss. No more than 10% decrease at a time.
      elif (self.dataclose[0] < (self.price_position * 0.90)):
        self.log(f'SELL ORDER ISSUED (Stop Loss?) at, {self.dataclose[0]} \n')
        self.order = self.sell()
        return


      
      
    

      
      
        



