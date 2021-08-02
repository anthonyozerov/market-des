class Trade:
    def __init__(self, buyer, seller, assetno, assetname, volume, price, time):
        self.buyer = buyer
        self.seller = seller
        self.assetno = assetno
        self.assetname = assetname
        self.volume = volume
        self.price = price
        self.time = time

        #fulfill the trade
        buyer.inventory[assetno] += volume
        buyer.add_cash(-1 * volume * price)
        seller.inventory[assetno] -= volume
        seller.add_cash(volume*price)

    #trades are ordered by time
    def __lt__(self, other): return self.time < other.time
    def __eq__(self, other): return self.time == other.time
    def __gt__(self, other): return self.time > other.time

    def __str__(self):
        return str(self.buyer.name) + " bought " + str(self.volume) + " of " + str(self.assetname) + " at " + str(self.price) + " from " + str(self.seller.name)
