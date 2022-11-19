
import backtrader as bt
import numpy as np
import pandas as pd

# establish an instance
cerebro = bt.Cerebro()


class roiBands(bt.Strategy):

    def __init__(self):

        # number of datapoints needed to build strategy
        self.period = 21
        # percent of funds avaiable used on each trade
        self.tradeSize_accountPct = 0.50

        # number of buy hits trigerred before buying or selling
        self.buy_Hits = 10
        self.sell_Hits = 3

        self.date_ = []
        self.open_ = []
        self.high_ = []
        self.low_ = []
        self.close_ = []

        self.close_p15_max = []
        self.close_p15_min = []

        self.roi_from_high = []
        self.roi_from_low = []

        self.roi_from_high_10th_pct = []
        self.roi_from_low_90th_pct = []

        # To keep track of pending orders
        self.order = None

        # Balance before transaction
        self.account_Value = [ self.broker.get_cash() ]

        # total shares
        self.total_shares_holding = []

        # total holds
        self.holdings = 0

        # counts the number of triggers
        self.buy_triggers = 0
        self.sell_triggers = 0




    def log(self, txt):
        ''' Logging function fot this strategy'''
        dt = self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def orderInfo(self, total_shares):

        # number of shares purchased
        self.shares = total_shares

        # transaction value
        self.transaction_value = round(self.datas[0].close * self.shares)
        print("Transaction Amount {}, Number of Shares {}".format(self.transaction_value, self.shares))


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
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        dt = self.datas[0].datetime.date(0)

        self.date_.append(dt.isoformat())
        self.open_.append(self.datas[0].open[0])
        self.high_.append(self.datas[0].high[0])
        self.low_.append(self.datas[0].low[0])
        self.close_.append(self.datas[0].close[0])

        if len(self.close_) > self.period :
            self.close_p15_max.append(np.max(self.close_[-self.period:]))
            self.close_p15_min.append(np.min(self.close_[-self.period:]))

            self.roi_from_high.append(self.close_[-1] / self.close_p15_max[-1] - 1)
            self.roi_from_low.append(self.close_[-1] / self.close_p15_min[-1] - 1 )

            self.roi_from_high_10th_pct.append(np.quantile(self.roi_from_high,0.05))
            self.roi_from_low_90th_pct.append(np.quantile(self.roi_from_low,0.95))


            if (self.roi_from_high[-1] <= self.roi_from_high_10th_pct[-1]
            ) & (self.roi_from_low[-1] < self.roi_from_low_90th_pct[-1]):
                
                while self.buy_triggers > self.buy_Hits:
                    # BUY, BUY, BUY!!! (with default parameters)

                    self.log('BUY CREATED, %.2f' % self.close_[-1])

                    # the currenr account value
                    account_value = self.broker.get_cash() 

                    # the number of shares I can buy
                    total_shares = round(account_value * self.tradeSize_accountPct / self.close_[-1])

                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy(size=total_shares)

                    if total_shares >= 1:
                        self.holdings += 1
                        self.total_shares_holding.append(total_shares)

                                # print order info
                    self.orderInfo(total_shares)

                                # keep track of account value
                    self.account_Value.append(cerebro.broker.getvalue())

                    self.buy_triggers = 0

                self.buy_triggers += 1

        
            if  (self.roi_from_low[-1] >= self.roi_from_low_90th_pct[-1]) & (
                self.roi_from_high[-1] > self.roi_from_high_10th_pct[-1]):
                #& (len(self.total_shares_holding)>0):

                tot_shares = sum(self.total_shares_holding)

                if (tot_shares > 0 ):
                    while self.sell_triggers >= self.sell_Hits:
                        self.log('SELL CREATED, %.2f' % self.close_[-1])

                            # place sell order
                        # self.order = self.sell(size = self.total_shares_holding[0]) 
                        # sell all shares 
                        
                        self.order = self.sell(size = tot_shares) 


                            
                        self.orderInfo(tot_shares)

                            # reduce holding position
                        self.holdings -= 1

                            # update remaining positions
                        self.total_shares_holding = [0]

                        self.sell_triggers = 0
                    self.sell_triggers += 1

        data = {'Date': self.date_[self.period:],
                'Close': self.close_[self.period:],
                'roi_from_high': self.roi_from_high,
                'roi_from_low': self.roi_from_low,
                'roi_from_high_10th_pct': self.roi_from_high_10th_pct,
                'roi_from_low_90th_pct': self.roi_from_low_90th_pct
                }
        data = pd.DataFrame(data)
        data.to_csv('results.csv')







