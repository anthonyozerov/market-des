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

        self.expectations = np.empty([0,5])

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
        values = [Probability.expected_value(likelihoods, self.inventory, card_index) for card_index in range(0, 4)]

        self.expectations = np.append(self.expectations,
                np.array([[data.time]+values]), axis=0)

        #print(likelihoods)
        #print(values) 

        i = sample
        assetno = sample(range(0,data.m),1)[0]
        return self.get_order(assetno, values[assetno])

        #to implement: making an order based on the price series seen
        #(for example, see parent Agent class)


        make_order = False
        if make_order:
            return event_o #the order event
        else:
            return self.get_nextconsider()
        
