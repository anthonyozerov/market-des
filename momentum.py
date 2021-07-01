from agent import Agent
from order import Order
from event import Event

class Momentum_Agent(Agent):

    def init_params(self,params):
        self.horizon = params['horizon']


    #this overwrites the consider function of the parent Agent class
    def consider(self, data):
        m = data["m"]
        assets = data["orders"]
        t = data["time"]
        print("price series at time",t)
        for asset in assets:
            price_series = asset.get_price_series(t-self.horizon)
            print(price_series)

        time_c = 1

        #to implement: making an order based on the price series seen
        #(for example, see parent Agent class)

        make_order = False
        if make_order:
            return event_o #the order event
        else:
            return self.get_nextconsider(data["time"]+time_c)
