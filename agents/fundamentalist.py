import sys
sys.path.append('..')
from agent import Agent
from probability import Probability
import copy
import data
from random import sample
import numpy as np

class Trader(Agent):

    def init_params(self,params):
        self.next_trades = [0, 0, 0, 0]
        self.belief_state =[ [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0] ]
        self.initial_hand = [0, 0, 0, 0]

        self.sell_expectations = np.empty([0,data.m+1])
        self.buy_expectations = np.empty([0,data.m+1])
        self.color = 'skyblue'
    
        self.r = params['r'] if 'r' in params else 1.5

    #this overwrites the consider function of the parent Agent class
    def consider(self):
        
        if all( [v == 0 for v in self.initial_hand] ):
            self.initial_hand = copy.copy(self.inventory)
            self.belief_state[self.number] = copy.copy(self.inventory)

        assets = data.assets
        for asset in assets:
            assetno = asset.assetno
            j = self.next_trades[assetno]
            while j < len(asset.trades):
                trade = asset.trades[j]
                buyerno = trade.buyer.number
                sellerno = trade.seller.number
                volume = trade.volume
                self.belief_state[sellerno][assetno] = self.belief_state[sellerno][assetno] - volume if self.belief_state[sellerno][assetno] > 0 else 0
                self.belief_state[buyerno][assetno] = self.belief_state[buyerno][assetno] + volume
                j += 1
            self.next_trades[assetno] = j

        total_state = [0, 0, 0, 0]
        for belief_list in self.belief_state:
            for i in range(4):
                total_state[i] = total_state[i] + belief_list[i]    
       
        ### for now, I implemented the likelihoods using total_state, but we can just use the self.intial_hand as Alejandra mentioned by changing it below 
        likelihoods = Probability.model_probabilities(total_state) 
        values = [Probability.expected_value_v2(likelihoods, self.inventory, card_index, self.r) for card_index in range(0, 4)]

        buy_values = [values[i][0] for i in range(4)]
        sell_values = [values[i][1] for i in range(4)]

        self.save_expectations([buy_values,sell_values])

        for order in self.orders:
            if order.buy == True:
                if order.price > values[order.assetno][0]:
                    order.deleted = True
            else:
                if order.price < values[order.assetno][1]:
                    order.deleted = True        

        #print(likelihoods)
        #print(values) 
        
        i = sample
        assetno = sample(range(0,data.m),1)[0]
        return self.get_order(assetno, values[assetno])

        #to implement: making an order based on the price series seen
        #(for example, see parent Agent class)
