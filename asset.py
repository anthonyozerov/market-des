from heapq import heappop, heappush, heapify
from order import Order

class Asset:
    def __init__(self,name):
        self.name = name
        #arrays of Orders (should be made into min and max queues)
        self.buys = []
        heapify(self.buys)
        self.sells = []
        heapify(self.sells)
        self.assetno = self.name

    def hasorders(self):
        if len(self.buys)*len(self.sells)>0:
            return True
        return False

    def clearMarket(self):
        if len(self.buys)*len(self.sells)==0: return
        maxbuy = heappop(self.buys)
        minsell = heappop(self.sells)

        while(maxbuy.price >= minsell.price and self.hasorders()):
            volume = min(maxbuy.n, minsell.n)
            price = maxbuy.price
            buyer = maxbuy.agent
            seller = minsell.agent
            print(buyer.name, "buys", volume, "of", self.name, "from", seller.name, "at", price)
            #add delays to the money addition? Not a good idea, I think
            buyer.inventory[self.assetno] += volume
            buyer.cash -= volume*price
            seller.inventory[self.assetno] -= volume
            seller.cash += volume*price
            if maxbuy.n > minsell.n:
                maxbuy.n -= minsell.n
                heappush(self.buys,maxbuy)
            elif maxbuy.n < minsell.n:
                minsell.n -= maxbuy.n
                heappush(self.sells,minsell)
            if len(self.buys)*len(self.sells)==0: break
            maxbuy = heappop(self.buys)
            minsell = heappop(self.sells)
        heappush(self.buys,maxbuy)
        heappush(self.sells,minsell)

    def addOrder(self, order):#agent, n, price, buy):
        cashgain = order.cashgain
        if(order.buy):
            heappush(self.buys,order)
        else:
            heappush(self.sells,order)
        self.clearMarket()

    def __str__(self):
        return str(self.name) + "\n" + str([str(buy) for buy in self.buys]) + "\n" + str([str(sell) for sell in self.sells])
