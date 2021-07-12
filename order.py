import data

class Order:
    def __init__(self, agent, n, price, assetno, buy, expire = float('inf')):
        self.agent = agent
        self.n = n
        self.cashgain = -1 * price if buy else price #negative if buy, positive if sell
        #(the negative/positive distinction isn't necessarily true, but
        #should hold fo the agents have good strategies)
        self.price = price
        self.assetno = assetno
        self.buy = buy
        self.deleted = False
        self.expiration_time = data.time + expire

    def check_expire(self):
        if data.time>self.expiration_time:
            self.deleted = True

    def __lt__(self, other): return self.cashgain < other.cashgain
    def __eq__(self, other): return self.cashgain == other.cashgain
    def __gt__(self, other): return self.cashgain > other.cashgain

    def __str__(self):
        typestring = "buy" if self.buy else "sell"
        price = -1 * self.cashgain if self.buy else self.cashgain
        return str(self.agent.name) + " " + typestring + " " + str(self.n) + " of " + str(self.assetno) + " at " + str(price)
