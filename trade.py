class Trade:
    def __init__(self, buyer, seller, assetno, assetname, volume, price, time):
        self.buyer = buyer
        self.seller = seller
        self.assetno = assetno
        self.assetname = assetname
        self.volume = volume
        self.price = price
        self.time = time

    def __str__(self):
        return str(self.buyer.name) + " bought " + str(self.volume) + " of " + str(self.assetname) + " at " + str(self.price) + " from " + str(self.seller.name)
