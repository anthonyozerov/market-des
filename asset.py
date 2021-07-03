from heapq import heappop, heappush, heapify
from order import Order
from trade import Trade

class Asset:
    def __init__(self, name, number):
        self.name = name
        #arrays of Orders (should be made into min and max queues)
        self.buys = []
        heapify(self.buys)
        self.sells = []
        heapify(self.sells)
        self.assetno = number
        self.price_series = {}
        self.trades = []

    def hasorders(self):
        if len(self.buys)*len(self.sells)>0:
            return True
        return False

    def match_orders(self, time):
        if len(self.buys)*len(self.sells)==0: return
        maxbuy = heappop(self.buys)
        minsell = heappop(self.sells)
        self.price_series[time] = maxbuy.price

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
                trade = Trade(buyer, seller, self.assetno, self.name, volume, price, time)
                print(trade)
                self.trades.append(trade)
                buyer.inventory[self.assetno] += volume
                buyer.cash -= volume*price
                seller.inventory[self.assetno] -= volume
                seller.cash += volume*price
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
            return {}

        series = {k: v for k, v in self.price_series.items() if k > start}
        if len(series)>0:
            return series

        k = max(self.price_series.keys())
        v = self.price_series[k]
        return {k: v}

    def __str__(self):
        return str(self.name) + "\n" + str([str(buy) for buy in self.buys]) + "\n" + str([str(sell) for sell in self.sells])
