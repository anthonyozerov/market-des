class Order:
    def __init__(self, agent, n, cashgain, assetno, buy):
        self.agent = agent
        self.n = n
        self.cashgain = cashgain #negative if buy, positive if sell
        #(the negative/positive distinction isn't necessarily true, but
        #should hold fo the agents have good strategies)
        self.price = cashgain if not buy else -1*cashgain
        self.assetno = assetno
        self.buy = buy

    def __lt__(self, other): return self.cashgain < other.cashgain
    def __eq__(self, other): return self.cashgain == other.cashgain
    def __gt__(self, other): return self.cashgain > other.cashgain

    def __str__(self):
        typestring = "buy" if self.buy else "sell"
        price = -1 * self.cashgain if self.buy else self.cashgain
        return str(self.agent.name) + " " + typestring + " " + str(self.n) + " of " + str(self.assetno) + " at " + str(price)
