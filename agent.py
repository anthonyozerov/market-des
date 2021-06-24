from random import expovariate, sample
import numpy as np
from event import Event

class Agent:
    def __init__(self, cash, latency_i, latency_o, rate_c, m, name):
        self.latency_i = latency_i #latency of market information getting to agent
        self.latency_o = latency_o #latency between agent sending order and it being added to order book
        self.rate_c = rate_c
        
        self.cash = cash
        self.inventory = np.zeros(m)
        self.considering = False

        self.name = name

    def get_nextconsider(self,time):
        self.considering = True
        return Event(agent = self, etype = "consider", time = time+expovariate(self.rate_c))

    def consider(self, data):
        self.considering = False
        m = data[2]
        assetno = sample(range(0,m),1)[0]
        fundamentals = data[1][assetno]
        orderbook = data[0][assetno]
        buy = sample([0,1],1)[0]
        n = 1
        if(buy):
            orderbook.addOrder(self, n, fundamentals*0.9, buy)
        else:
            orderbook.addOrder(self, n, fundamentals*0.9, buy)

        return False


