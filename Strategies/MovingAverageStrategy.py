import backtrader as bt
import math

class MovingAverageStrategy(bt.Strategy):
    def __init__(self):
        # Create fast and slow moving averages
        self.fast_ma = bt.ind.SMA(period=9)
        self.slow_ma = bt.ind.SMA(period=50)
        self.order_pct = 0.50

    # Generate trading signals
    def next(self):

        # Buy when fast MA crosses over slow MA
        if self.fast_ma > self.slow_ma:
            # Use 50% of account value to enter trade
            amount_to_invest = (self.order_pct * self.broker.cash)
            self.size = math.floor(amount_to_invest / self.data.close)

            print("Buy {} shares at {}".format(self.size,  self.data.close[0]))
            self.buy(size=self.size)

        # Sell when slow MA crosses over fast MA
        elif self.fast_ma < self.slow_ma:
            self.sell()