import sys
sys.path.append('agents')
from random import uniform, expovariate, shuffle
import heapq
from asset import Asset
from event import Event
from momentum import Momentum_Agent
from fundamentalist import Fundamentalist_Agent
from bottomfeeder import Bottomfeeder_Agent
from noise import Noise_Agent
import numpy as np
import math
import argparse
from probability import Probability
import pickle

import data

from agent import Agent

classdict = {'momentum': Momentum_Agent, 'fundamentalist': Fundamentalist_Agent, 'noise':Noise_Agent,
        'bottomfeeder': Bottomfeeder_Agent}

argp = argparse.ArgumentParser()
argp.add_argument('-m', '--assets', default=4)
argp.add_argument('-n', '--agents', default=4)
argp.add_argument('-r', '--rules', default = "full")
argp.add_argument('-s', '--steps', default = 1000)
argp.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true')
argp.add_argument('-c', '--config', default = 'agents')
argp.add_argument('-i', '--index', default = 0)
argp.add_argument('-o', '--output', default = 'datadump')
argp.set_defaults(verbose=False)

args = argp.parse_args()
figgie = args.rules == "figgie"
suits = ["spades", "clubs", "hearts", "diamonds"]
goalsuit = -1
bonus = -1
distribution = []


data.verbose = args.verbose

# market will clear by matching the biggest bids with the smallest asks



if figgie:
    n = 4
    data.m = 4
else:
    n = int(args.agents)
    data.m = int(args.assets)
steps = int(args.steps)

def print_inventories():
    assets_total = np.zeros(data.m)
    cash_total = 0
    for agent in data.agents:
        assets_total+=np.array(agent.inventory)
        cash_total += agent.cash
        fmt = "{0}: ${1}, assets {2}"
        print(fmt.format(agent.name, agent.cash, agent.inventory))
    print("Total cash:", cash_total)
    print("Total assets:", assets_total)


def initialize_figgie():
    distribution = [8,10,10,12]
    shuffle(distribution)
    maxsuit = np.argmax(distribution)
    if(maxsuit % 2 == 0):
        goalsuit = maxsuit+1
    else:
        goalsuit = maxsuit-1
    print("The goal suit is",goalsuit,"i.e.", suits[goalsuit])
    bonus = 100 if distribution[goalsuit]==10 else 120
    return bonus, distribution, goalsuit


def initialize(bonus, distribution, goalsuit):

    assets = [] #each Asset object has:
    # max priority queue for buys
    # min priority queue for sells

    names = range(0,data.m)
    if figgie:
        #names = suits
        dist = distribution.copy()
    else:
        dist = np.zeros(data.m)+10
    for i in range(0,data.m):
        assets.append(Asset(name = names[i], number = i))
    
    agents = []
    #events is a min-priority queue, sorted by time
    events = []
    heapq.heapify(events)

    from configparser import ConfigParser
    import ast
    config = ConfigParser()
    config.read('configs/'+args.config+'.ini')
    count = 0
    for section in config.sections():
        par = config[section]
        number = int(par["n"]) if "n" in par else 1
        cash = float(par["cash"]) if "cash" in par else 100
        params = ast.literal_eval(par["params"]) if "params" in par else {}
        latency_o = float(par["latency_o"]) if "latency_o" in par else 0
        rate_c = float(par["rate_c"]) if "rate_c" in par else uniform(0,1)
        base_name = par["name"] if "name" in par else str(section)
        agent_class = classdict[par["type"]] 
        risk = float(par["risk"]) if "risk" in par else 0
        for j in range(0, number):
            name = base_name+"."+str(j)
            agent = agent_class(cash=cash, latency_o = latency_o, rate_c = rate_c,
                      m=data.m, name=name, number=count, risk=risk)
            agent.init_params(params)
            count+=1
            for k in range(0,10):
                assetno = np.random.choice(range(0,data.m), 1, p=np.array(dist)/sum(dist))[0]
                dist[assetno]-=1
                agent.inventory[assetno]+=1

            heapq.heappush(events, agent.get_nextconsider())
            agents.append(agent) 

    return assets, agents, events

def update():
    event = heapq.heappop(events)
    data.time = event.time
    data.times.append(data.time)
    if data.verbose: print(t,data.time,": agent",event.agent.name,event.type)
    #for j in range(0, m):
        #print(assets[j])
         
    #in a consideration event, an agent starts considering and we either add a
    #new consideration event to the queue (if they decided not to make an order)
    #or an addorder event to the queue (if they decided to make an order)
    if event.type == "consider":
        event_d = event.agent.consider()
        heapq.heappush(events, event_d)

    #in an addorder event, we add an agent's order to an asset's order book, clear
    #that asset's market, and add a new consideration event for the agent.
    if event.type == "addorder":
        asset = data.assets[event.order.assetno]
        asset.add_order(event.order)
        event.agent.orders.append(event.order)
        heapq.heappush(events,event.agent.get_nextconsider())


def payout():
    max_cards = max([agent.inventory[goalsuit] for agent in data.agents])
    max_agents = [agent for agent in data.agents if agent.inventory[goalsuit] == max_cards]
    bonus_split = bonus/len(max_agents)
    for agent in max_agents:
        agent.cash += bonus_split
    for agent in data.agents:
        agent.cash += agent.inventory[goalsuit] * 10


if figgie:
    bonus, distribution, goalsuit = initialize_figgie()

data.assets, data.agents, events = initialize(bonus, distribution, goalsuit)
print("Inventories before trading:--------------")
print_inventories()
for t in range(0,steps):
    update()
print("Inventories after trading:---------------")
print_inventories()

if figgie:
    print("Adding bonuses---------------------------")
    print("goal suit:", goalsuit)
    print("bonus:", bonus)
    payout()
    print_inventories()
    winner = data.agents[np.argmax([agent.cash for agent in data.agents])]
    print("The winner is", winner.name)


#for i in range(0, data.m):
#    np.savetxt('price_series'+str(i)+'.csv',data.assets[i].get_price_series(0),
#            delimiter=',')

#for agent in data.agents:
#    try:
#        np.savetxt(agent.name+'_expectations.csv', agent.expectations,delimiter=",")
#    except AttributeError:
#        pass

import os
if not os.path.isdir('./output'):
    os.makedirs('./output')
filename = os.path.join('./output', args.output+'.'+str(args.index))
to_pickle = {'times': data.times, 'agents': data.agents, 'assets': data.assets,
        'm': data.m}
pickle.dump(to_pickle,open(filename,'wb'))
