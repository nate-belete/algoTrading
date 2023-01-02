import datetime as dt 
import yfinance as yf
import backtrader as bt 
import numpy as np
from Strategies.MovingAverageStrategy import MovingAverageStrategy

# get data
df = yf.download('SPY','2022-01-01', '2022-12-31', interval='1d')

# establish an instance
cerebro = bt.Cerebro()

# create a data feed
feed = bt.feeds.PandasData(dataname = df)

# add feed to instance
cerebro.adddata(feed)

# add strategy
cerebro.addstrategy(MovingAverageStrategy)

# Set initial account value
cerebro.broker.setcash(100000)


# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Return if buy and hold 
hold = df['Close'][-1]/df['Close'][0]*100000
print("Return if you just held position {}".format(hold))

cerebro.plot()