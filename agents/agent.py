import sys
sys.path.append('..')
from random import expovariate, sample
import numpy as np
from event import Event
from order import Order
from random import uniform
import data
from scipy.special import lambertw
import math

class Agent:

    #init method common to all agents
    def __init__(self, cash, latency_o, rate_c, m, name, number, risk):
        self.latency_o = latency_o #latency between agent sending order and it being added to order book
        self.rate_c = rate_c
        
        self.cash = cash
        self.inventory = np.zeros(m)
        self.considering = False

        self.name = name
        self.number = number
        self.time_c = 0
        self.risk = risk

        self.orders = []

        self.payout = 0


    def init_params(self,params):
        pass

    def get_nextconsider(self):
        return Event(agent = self, etype = "consider", time = data.time+self.time_c+expovariate(self.rate_c))

    def orderevent(self, wait_time, order):
        event_o = Event(agent = self, time = data.time + wait_time + self.time_c
                + self.latency_o, etype = "addorder")
        event_o.order = order
        return event_o

    def get_p_star(self, assetno, expected, horizon):
        alpha = self.risk
        variance = data.assets[assetno].get_return_variance(horizon)
        stock_position = self.inventory[assetno]
        if(stock_position == 0 or variance == 0):
            return expected
        #print(stock_position * self.alpha * variance * expected)
        coef = stock_position * alpha * variance
        p_star = np.real(lambertw(coef*expected)/coef)
        #print(expected,stock_position,variance,p_star,math.isnan(p_star))
        return p_star

    def get_order(self, assetno, expected, horizon=float('inf')):
        if self.risk>0:
            expected = self.get_p_star(assetno, expected, horizon)
        minprice = 0
        maxprice = expected*2
        n = 1
        price = uniform(minprice,maxprice)
        buy = price<expected if price>0 else sample([False,True],1)[0]
        #print(expected,price)
        if(buy):
            price = min(price,data.assets[assetno].get_price(buying=True))
        else:
            price = max(price,data.assets[assetno].get_price(buying=False))

        order = Order(self, n, price, assetno, buy)
        return self.orderevent(0,order)


