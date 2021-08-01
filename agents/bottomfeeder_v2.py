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
        self.ordersno = params['ordersno']

        self.color = 'darksalmon'

    def consider(self):
        m = data.m
        assets = data.assets
        time = data.time
        estimates = [[] for _ in range(m)]
        expecteds = [0,0,0,0]
        for agentno in self.prey:
            agent = data.agents[agentno]
            buys = [[] for _ in range(m)]
            sells = [[] for _ in range(m)]
            buys_done = np.full(shape=m, fill_value=False)
            sells_done = np.full(shape=m, fill_value=False)
            for order in reversed(agent.orders):
                if all(buys_done) and all(sells_done):
                    break
                i = order.assetno
                price = order.price
                buy = order.buy
                if buy:
                    if buys_done[i]:
                        continue
                    buys[i].append(price)
                    if len(buys[i]) >= self.ordersno:
                        buys_done[i] = True
                else:
                    if sells_done[i]:
                        continue
                    sells[i].append(price)
                    if len(sells[i]) >= self.ordersno:
                        sells_done[i] = True

            for i in range(m):
                if not buys_done[i] or not sells_done[i]:
                    continue
                buy_mean = np.mean(buys[i])
                sell_mean = np.mean(sells[i])
                estimate = (buy_mean+sell_mean)/2
                estimates[i].append(estimate)

        expecteds = [np.mean(est) if len(est)>0 else 0 for est in estimates]

        if max(expecteds) < float('inf'):
            self.save_expectations(expecteds)

        assetno = sample(range(0,m),1)[0]
        expected = expecteds[assetno]
        if expected != 0:
            return self.get_order(assetno, expected)
        return self.get_nextconsider()


