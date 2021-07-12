from agent import Agent
from order import Order
from event import Event
import numpy as np
import math
import data

class Momentum_Agent(Agent):

    def init_params(self,params):
        self.horizon = params['horizon']


    #this overwrites the consider function of the parent Agent class
    def consider(self):
        m = data.m
        assets = data.assets
        time = data.time
        #print("price series at time",t)
        avg_returns = []
        expected_prices = []
        for asset in assets:
            price_series = asset.get_price_series(time-self.horizon)
            avg_return = asset.get_mean_spot_return(self.horizon)
            avg_returns.append(avg_return)

            if(len(price_series)==0):
                expected_prices.append(-1)
                continue
            last_price = price_series[-1,1]
            #print(avg_return)
            #print(self.horizon)
            #print(last_price)
            expected_price = last_price * math.exp(avg_return * self.horizon)
            expected_prices.append(expected_price)

        assetno = np.argmax(np.abs(avg_returns))
        make_order =  avg_returns[assetno] != 0
        expected = expected_prices[assetno]
        print(expected)

        self.time_c = 1

        if make_order:
            return self.get_order(assetno, expected)
        else:
            return self.get_nextconsider()
