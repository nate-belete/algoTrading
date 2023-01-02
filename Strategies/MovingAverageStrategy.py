import backtrader as bt
import math

class MovingAverageStrategy(bt.Strategy):
    def __init__(self):
        # Create fast and slow moving averages
        self.fast_ma = bt.ind.SMA(period=5)
        self.slow_ma = bt.ind.SMA(period=20)
        self.order_pct = 0.50

    # Generate trading signals
    def next(self):

        # Buy when fast MA crosses over slow MA
        if self.fast_ma > self.slow_ma:
            # if we have an open position already, pass
            if self.position:
                pass
            else:
                # Use 50% of account value to enter trade
                amount_to_invest = (self.order_pct * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close)
                self.date = self.data.datetime.date(0)

                print("{}: Buy {} shares at {}".format(self.date, self.size,  round(self.data.close[0])))
                self.buy(size=self.size)


        # Sell when slow MA crosses over fast MA
        elif self.fast_ma < self.slow_ma:
            # if we have an open position, sell
            if self.position:
                self.num_shares = self.position.size
                self.date = self.data.datetime.date(0)
                print("{}: Sell {} shares at {}".format(self.date, self.num_shares,  round(self.data.close[0])))
                self.sell(size=self.num_shares)