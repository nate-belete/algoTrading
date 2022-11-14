import datetime as dt 
import yfinance as yf
import backtrader as bt 
import numpy as np
from Strategies.smaCross import SmaCross

# get data
df = yf.download('SPY', '2015-01-01', '2022-12-31')

# establish an instance
cerebro = bt.Cerebro()

# create a data feed
feed = bt.feeds.PandasData(dataname = df)

# add feed to instance
cerebro.adddata(feed)

# add strategy
cerebro.addstrategy(SmaCross)

# Set initial account value
cerebro.broker.setcash(10000)


# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Return if buy and hold 
hold = df['Close'][-1]/df['Close'][0]*10000
print("Return if you just held position {}".format(hold))

cerebro.plot()