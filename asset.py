from heapq import heappop, heappush, heapify
from order import Order
from trade import Trade
import numpy as np

class Asset:
    def __init__(self, name, number):
        self.name = name
        #arrays of Orders (should be made into min and max queues)
        self.buys = []
        heapify(self.buys)
        self.sells = []
        heapify(self.sells)
        self.assetno = number
        self.price_series = []
        self.price_series = np.empty([0,2])
        self.trades = []

    def hasorders(self):
        if len(self.buys)*len(self.sells)>0:
            return True
        return False

    def match_orders(self, time):
        if not self.hasorders():
            return
        maxbuy = heappop(self.buys)
        minsell = heappop(self.sells)
        if len(self.price_series) == 0 or self.price_series[-1,1] != maxbuy.price:
            self.price_series = np.append(self.price_series,np.array([[time,maxbuy.price]]),axis=0)

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
                trade = Trade(buyer, seller, self.assetno, self.name, volume, price, time)
                print(trade)
                self.trades.append(trade)
            if maxbuy.n > min(minsell.n,available):
                maxbuy.n -= volume
                heappush(self.buys,maxbuy)
            elif maxbuy.n < min(minsell.n,available):
                minsell.n -= volume
                if available > 0:
                    heappush(self.sells,minsell)
            if len(self.buys)*len(self.sells)==0: break
            maxbuy = heappop(self.buys)
            minsell = heappop(self.sells)
        heappush(self.buys,maxbuy)
        heappush(self.sells,minsell)

    def add_order(self, order, time):
        if(order.buy):
            heappush(self.buys,order)
        else:
            heappush(self.sells,order)
        self.match_orders(time)

    def get_price_series(self,start):
        if len(self.price_series) == 0:
            return self.price_series

        min_index = 0
        while(min_index < len(self.price_series) and self.price_series[min_index,0]<start):
            min_index += 1
        min_index -= 1
        return(self.price_series[min_index:len(self.price_series),:])

    def __str__(self):
        return str(self.name) + "\n" + str([str(buy) for buy in self.buys]) + "\n" + str([str(sell) for sell in self.sells])
