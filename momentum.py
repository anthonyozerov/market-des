from agent import Agent
from order import Order
from event import Event
import numpy as np
import math

class Momentum_Agent(Agent):

    def init_params(self,params):
        self.horizon = params['horizon']


    #this overwrites the consider function of the parent Agent class
    def consider(self, data):
        m = data["m"]
        assets = data["orders"]
        time = data["time"]
        #print("price series at time",t)
        avg_returns = []
        prices = []
        for asset in assets:
            price_series = asset.get_price_series(time-self.horizon)
            if(len(price_series)==0):
                avg_returns.append(0)
                prices.append(-1)
                continue
            #print(price_series)
            current_price = price_series[0,1]
            t = time-self.horizon
            avg_return = 0
            for i in range (1, len(price_series)):
                now = price_series[i,:]
                previous_price = current_price
                current_price = price_series[i,1]
                spot_return = math.log(current_price/previous_price)
                time_spent = price_series[i,0]-t

                avg_return += spot_return * time_spent/self.horizon

                t = price_series[i,0]
            last_price = price_series[-1,1]
            expected_price = last_price * math.exp(avg_return * self.horizon)
            avg_returns.append(avg_return)
            prices.append(last_price)
        assetno = np.argmax(np.abs(avg_returns))
        make_order =  avg_returns[assetno] != 0
        buy = True if avg_returns[assetno]>0 else False
        price = prices[assetno]
        n = 1

        cashgain = price if not buy else -1*price
        order = Order(self, n, cashgain, assetno, buy)

        self.time_c = 1

        if make_order:
            return self.orderevent(time=data["time"], order=order)
        else:
            return self.get_nextconsider(data["time"]+self.time_c)
