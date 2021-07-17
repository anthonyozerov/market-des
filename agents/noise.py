import sys
sys.path.append('..')
from agent import Agent
import numpy as np
from random import sample
from numpy.random import normal
from random import uniform
import data
import math

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
            price = uniform(0,10)
        else:
            price = price_series[-1,1]
        expected_return = normal(scale = self.var ** 0.5)
        expected = price * math.exp(expected_return)
        #print("actual",expected)
        #print("+noise",expected)

        self.time_c = 0

        return self.get_order(assetno, expected)
