
import backtrader as bt 
import numpy as np

# establish an instance
cerebro = bt.Cerebro()


class InsideBar(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast = 50,  # period for the fast moving average
        pslow = 200,   # period for the slow moving average
        ratio = 0.20
    )

    def log(self, txt):
        ''' Logging function fot this strategy'''
        dt = self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def orderInfo(self, total_shares):

        # number of shares purchased
        self.shares = total_shares

        # transaction value
        self.transaction_value = round(self.dataclose[0] * self.shares)

        print("Transaction Amount {}, Number of Shares {}".format(self.transaction_value, self.shares))


    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataopen = self.datas[0].open

        # To keep track of pending orders
        self.order = None

        # list to store variance between price and sma
        self.sma_spread = []

        # # To Keep track of account value
        # self.balance = None

        # Balance before transaction
        self.account_Value = [ self.broker.get_cash() ]

        # total shares
        self.total_shares_holding = []

        # total holds
        self.holdings = 0


        self.fast_SMA = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        self.slow_SMA = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        

        self.crossover = bt.ind.CrossOver(self.fast_SMA, self.slow_SMA)  # crossover signal


    def notify_order(self, order):
        # If Buy/Sell order was  submitted/accepted to/by broker
        if order.status in [order.Submitted, order.Accepted]:
            # Then Do Nothing
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            # if buy was completed
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            
            # if sell was completed
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            # count of ?
            self.bar_executed = len(self)

        # if order was canceled/redjected or a margin call
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None


    def next(self):

        # # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # # Check if we are in the market
        # if not self.position:

        # check if you have funds to trade
        self.sma_spread.append( self.dataclose[0] - self.fast_SMA )

        if (self.dataclose[0] < self.datahigh[-2]) & (self.dataclose[-1] < self.datahigh[-2]) :
            
            if (self.datalow[0] > self.datalow[-2]) & (self.datalow[-1] > self.datalow[-2])  :
                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATED, %.2f' % self.dataclose[0])

                # the currenr account value
                account_value = self.broker.get_cash() 

                # the number of shares I can buy
                total_shares = round(account_value * self.p.ratio / self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(size=total_shares)

                if total_shares >= 1:
                    self.holdings += 1
                    self.total_shares_holding.append(total_shares)

                            # print order info
                self.orderInfo(total_shares)

                            # keep track of account value
                self.account_Value.append(cerebro.broker.getvalue())

        if (self.holdings >= 10):
            if (self.holdings >= 10):

        # if 
                self.log('SELL CREATED, %.2f' % self.dataclose[0])

                    # place sell order
                self.order = self.sell(size = self.total_shares_holding[0]) 

                    # print info
                self.orderInfo(self.total_shares_holding[0])

                    # reduce holding position
                self.holdings -= 1

                    # update remaining positions
                self.total_shares_holding = self.total_shares_holding[1:]


        # if self.dataclose[0] > self.fast_SMA:
        #     if self.broker.get_cash()  > 0:
        #         if self.dataclose[0] < self.dataclose[-1] :
        #             # current close less than previous close

        #             if self.dataclose[-1] < self.dataclose[-2]:
        #                 # previous close less than the previous close
        #                 if self.dataclose[-2] < self.dataclose[-3]:

        #                     # # BUY, BUY, BUY!!! (with default parameters)
                            # self.log('BUY CREATED, %.2f' % self.dataclose[0])

                            # # the currenr account value
                            # account_value = self.broker.get_cash() 

                            # # the number of shares I can buy
                            # total_shares = round(account_value * self.p.ratio / self.dataclose[0])

                            # # Keep track of the created order to avoid a 2nd order
                            # self.order = self.buy(size=total_shares)


                            # if total_shares >= 1:
                            #     self.holdings += 1
                            #     self.total_shares_holding.append(total_shares)

                            # # print order info
                            # self.orderInfo(total_shares)

                            # # keep track of account value
                            # self.account_Value.append(cerebro.broker.getvalue())

        # if self.holdings >= 15:
        #     self.log('SELL CREATED, %.2f' % self.dataclose[0])

        #         # place sell order
        #     self.order = self.sell(size = self.total_shares_holding[0]) 

        #         # print info
        #     self.orderInfo(self.total_shares_holding[0])

        #         # reduce holding position
        #     self.holdings -= 1

        #         # update remaining positions
        #     self.total_shares_holding = self.total_shares_holding[1:]
