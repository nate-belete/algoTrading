
import backtrader as bt
import numpy as np
import pandas as pd

# establish an instance
cerebro = bt.Cerebro()


class BuyOnPullBack(bt.Strategy):

    def __init__(self):

        # number of datapoints needed to build strategy
        self.period = 21
        self.period_buy = 21
        self.period_sell = 30
        # percent of funds avaiable used on each trade
        self.tradeSize_accountPct = 0.50

        # number of buy hits trigerred before buying or selling
        self.buy_Hits = 10
        self.sell_Hits = 1

        # bootstrapped means 
        self.boot_ratio_from_high_mean = -0.05
        self.boot_ratio_from_low_mean = abs(self.boot_ratio_from_high_mean)*1.0

        self.date_ = []
        self.open_ = []
        self.high_ = []
        self.low_ = []
        self.close_ = []

        self.close_p15_max = []
        self.close_p15_min = []

        self.roi_from_high = []
        self.roi_from_low = []

        self.roi_from_high_10th_pct = [0] * (self.period-1)
        self.roi_from_low_90th_pct = [0] * (self.period-1)

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

        self.round = 0




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

    def roiBandStrategy(self, close_):
        # get prior highs and lows
        prior_max = max(close_)
        prior_min = min(close_)
        
        # get ratio from prior high/low
        ratio_from_high = close_[-1] / prior_max - 1
        ratio_from_low = close_[-1] / prior_min - 1
        
        
        return prior_max, prior_min, ratio_from_high, ratio_from_low

        


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

            

            self.roi_from_high_10th_pct.append(np.quantile(self.roi_from_high[-self.period_buy:],0.10))
            self.roi_from_low_90th_pct.append(np.quantile(self.roi_from_low[-self.period_sell:],0.90))



            if (self.roi_from_high[-1] <= self.boot_ratio_from_high_mean):
                    
                    # if trigger has been on for buy_Hits period, and the trigger just turned off
                while (self.buy_triggers > self.buy_Hits) & (self.roi_from_high[-1] <= self.boot_ratio_from_high_mean):
                    # print("self.buy_triggers ", self.buy_triggers)
                    # print("self.buy_Hits ", self.buy_Hits)
                    # print("--")
                    # print("roi_from_high[-1] ", self.roi_from_high[-1])
                    # print("self.boot_ratio_from_high_mean ", self.boot_ratio_from_high_mean)
                    # print("--")
                    # print("--")
                    # print("--")

                        # if rolling ROI exceeds the bootstapped mean
                    

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

            
            if  (self.roi_from_low[-1] >= self.boot_ratio_from_low_mean):

                tot_shares = sum(self.total_shares_holding)

                # print("tot_shares ", tot_shares)

                if (tot_shares > 0 ):
                    while (self.sell_triggers >= self.sell_Hits) & ((self.roi_from_low[-1] >= self.boot_ratio_from_low_mean)):
                            # if rolling ROI exceeds the bootstapped mean


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
                'roi_from_high_10th_pct': self.roi_from_high_10th_pct[self.period-1:],
                'roi_from_low_90th_pct': self.roi_from_low_90th_pct[self.period-1:]
                }

        data = pd.DataFrame(data)
        data.to_csv('results.csv')







