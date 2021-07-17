import sys
sys.path.append('..')
from agent import Agent
import numpy as np
import math
import data
from random import sample

class Trader(Agent):

    def init_params(self,params):
        self.prey = params['prey']

    def consider(self):
        m = data.m
        assets = data.assets
        time = data.time
        expecteds = np.zeros(m)
        for agentno in self.prey:
            agent = data.agents[agentno]
            lower = np.full(shape=m, fill_value=False)
            upper = np.full(shape=m, fill_value=float('inf'))
            assets_done = np.full(shape=m, fill_value=0)
            for order in reversed(agent.orders):
                if all(assets_done):
                    break
                i = order.assetno
                if assets_done[i]:
                    continue
                price = order.price
                buy = order.buy
                if price > upper[i] and buy:
                    assets_done[i] = True
                elif price < lower[i] and not buy:
                    assets_done[i] = False
                if buy and price >= lower[i]:
                    lower[i] = price
                elif not buy and price <= upper[i]:
                    upper[i] = price
            diffs = upper-lower
            expecteds += (upper+lower)/2 / len(self.prey)



        assetno = sample(range(0,m),1)[0]
        expected = expecteds[assetno]
        #print(expected)

        return self.get_order(assetno, expected)
