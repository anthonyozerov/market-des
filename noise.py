from agent import Agent
from order import Order
from event import Event
import numpy as np
from random import sample
from numpy.random import normal
import data

class Noise_Agent(Agent):

    def init_params(self,params):
        self.horizon = params['horizon']
        self.var = params['var']

    #this overwrites the consider function of the parent Agent class
    def consider(self):
        assetno = sample(range(0,data.m),1)[0]
        asset = data.assets[assetno]
        buy = sample([0,1],1)[0]
        n = 1
        price_series = asset.get_price_series(data.time)
        if len(price_series)==0:
            expected = 0
        else:
            expected = price_series[-1,1]
        #print("actual",expected)
        expected += normal(scale = self.var**0.5)
        expected = abs(expected)
        #print("+noise",expected)

        self.time_c = 1

        return self.get_order(assetno, expected)
