from heapq import heappop, heappush, heapify
from order import Order
from trade import Trade
import numpy as np
import data
import math

def pop_lazy(heap):
    if len(heap)==0:
        return False
    order = heappop(heap)
    order.check_expire()
    while(order.deleted == True and len(heap)>0):
        order = heappop(heap)
        order.check_expire()
    return order

class Asset:
    def __init__(self, name, number):
        self.name = name
        #arrays of Orders (should be made into min and max queues)
        self.buys = []
        heapify(self.buys)
        self.sells = []
        heapify(self.sells)
        self.assetno = number

        #create empty array with 0 rows and 2 columns
        self.price_series = np.empty([0,2])
        self.trades = []

    def get_price(self,buying=True):
        heap = self.sells if buying else self.buys
        order = pop_lazy(heap)
        if(not order or order.deleted):
            if buying == True:
                return float('inf')
            else:
                return 0
        heappush(heap,order)
        return order.price

    def hasorders(self):
        if len(self.buys)*len(self.sells)>0:
            return True
        return False

    def match_orders(self):
        if not self.hasorders():
            return
        maxbuy = pop_lazy(self.buys)
        minsell = pop_lazy(self.sells)
        if maxbuy.deleted or minsell.deleted:
            return
        if len(self.price_series) == 0 or self.price_series[-1,1] != maxbuy.price:
            self.price_series = np.append(self.price_series,
                                  np.array([[data.time,maxbuy.price]]),axis=0)

        while(maxbuy.price >= minsell.price and self.hasorders()):
            available = minsell.agent.inventory[self.assetno]

            # volume traded is upper bounded by the size of the buy
            # order, the size of the sell order, and how much the seller
            # has available
            volume = min(maxbuy.n, minsell.n, available)
            price = maxbuy.price
            buyer = maxbuy.agent
            seller = minsell.agent
            if volume>0:
                # if a trader tries to sell something they don't have,
                # punish the trader?
                trade = Trade(buyer, seller, self.assetno, self.name, volume, price, data.time)
                if data.verbose: print(trade)
                self.trades.append(trade)
            if maxbuy.n > min(minsell.n,available):
                maxbuy.n -= volume
                heappush(self.buys,maxbuy)
            elif maxbuy.n < min(minsell.n,available):
                minsell.n -= volume
                if available > 0:
                    heappush(self.sells,minsell)
            if len(self.buys)*len(self.sells)==0: break
            maxbuy = pop_lazy(self.buys)
            minsell = pop_lazy(self.sells)
            if maxbuy.deleted or minsell.deleted:
                return
        heappush(self.buys,maxbuy)
        heappush(self.sells,minsell)

    def add_order(self, order):
        if(order.buy):
            heappush(self.buys,order)
        else:
            heappush(self.sells,order)
        self.match_orders()

    def get_price_series(self,start):
        if len(self.price_series) == 0:
            return self.price_series

        min_index = 0
        while(min_index < len(self.price_series) and self.price_series[min_index,0]<start):
            min_index += 1
        min_index -= 1
        if(min_index<0):
            return self.price_series
        return(self.price_series[min_index:len(self.price_series),:])

    def __str__(self):
        return str(self.name) + "\n" + str([str(buy) for buy in self.buys]) + "\n" + str([str(sell) for sell in self.sells])


    def get_mean_spot_return(self, horizon):
        price_series = self.get_price_series(data.time-horizon)
        if(len(price_series)==0):
            return 0
        #print(price_series)
        current_price = price_series[0,1]
        t = data.time-horizon
        avg_return = 0
        for i in range (1, len(price_series)):
            now = price_series[i,:]
            previous_price = current_price
            current_price = price_series[i,1]
            spot_return = math.log(current_price/previous_price)
            #take log at end instead?
            #print('spot return:', spot_return)
            time_spent = price_series[i,0]-t

            avg_return += spot_return * (time_spent/horizon)

            t = price_series[i,0]
        #print('avg return:', avg_return)
        return avg_return

    def get_return_variance(self, horizon):
        mean_return = self.get_mean_spot_return(horizon)
        price_series = self.get_price_series(data.time-horizon)
        if(len(price_series)==0):
            return 0.001

        current_price = price_series[0,1]
        t = data.time-horizon
        variance = 0
        for i in range (1, len(price_series)):
            now = price_series[i,:]
            previous_price = current_price
            current_price = price_series[i,1]
            spot_return = current_price/previous_price
            diff_sq = (spot_return-mean_return)**2
            time_spent = price_series[i,0]-t

            variance += diff_sq * time_spent/horizon

            t = price_series[i,0]
        return variance
