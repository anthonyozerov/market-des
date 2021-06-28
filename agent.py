from random import expovariate, sample
import numpy as np
from event import Event
from order import Order

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
        m = data["m"]
        assetno = sample(range(0,m),1)[0]
        fundamentals = data["f"][assetno]
        orderbook = data["orders"][assetno]
        buy = sample([0,1],1)[0]
        n = 1
        
        price = fundamentals*0.9
        cashgain = price if not buy else -1*price
        order = Order(self, n, cashgain, assetno, buy)

        time_c = 1 #time spent considering

        event_o = Event(agent = self, time = data["time"] + time_c + self.latency_o, etype = "addorder")
        event_o.order = order
        make_order = True
        if make_order:
            return event_o
        #orderbook.addOrder(self, n, fundamentals*0.9, buy)
        else:
            return self.get_nextconsider(data["time"])



