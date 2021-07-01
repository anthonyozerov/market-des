from random import uniform, expovariate, shuffle
import heapq
from asset import Asset
from agent import Agent
from event import Event
from momentum import Momentum_Agent
import numpy as np
import math
import argparse

argp = argparse.ArgumentParser()
argp.add_argument('-m', '--assets', default=4)
argp.add_argument('-n', '--agents', default=4)
argp.add_argument('-r', '--rules', default = "full")
argp.add_argument('-s', '--steps', default = 1000)
argp.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true')
argp.set_defaults(verbose=False)

args = argp.parse_args()
figgie = args.rules == "figgie"
suits = ["spades", "clubs", "hearts", "diamonds"]
goalsuit = -1
bonus = -1
distribution = []

times = []

verbose = args.verbose

# market will clear by matching the biggest bids with the smallest asks

if figgie:
    n = 4
    m = 4
else:
    n = int(args.agents)
    m = int(args.assets)
steps = int(args.steps)

def f_value(time,k):
    return np.zeros(m)+1+math.sin(time+k)

def print_inventories():
    assets_total = np.zeros(m)
    cash_total = 0
    for agent in agents:
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

    names = range(0,m)
    if figgie:
        #names = suits
        dist = distribution.copy()
    else:
        dist = np.zeros(m)+10
    for i in range(0,m):
        assets.append(Asset(name = names[i], number = i))
    
    agents = []
    #events is a min-priority queue, sorted by time
    events = []
    heapq.heapify(events)

    for i in range(0,n):
        if figgie:
            cash = 350
        else:
            cash = uniform(0,100)
        latency_i = uniform(0,100)
        latency_o = uniform(0, 100)
        rate_c = uniform(0,1)

        #if i == 2:
        #    agent = Momentum_Agent(cash = cash, latency_i = latency_i,
        #              latency_o = latency_o, rate_c = rate_c,
        #              m = m, name = i)
        #    params = {'horizon':50}
        #    agent.init_params(params)
        #else:
        agent = Agent(cash = cash, latency_i = latency_i,
                          latency_o = latency_o, rate_c = rate_c,
                          m = m, name = i)
        for i in range(0,10):
            assetno = np.random.choice(range(0,m), 1, p=np.array(dist)/sum(dist))[0]
            dist[assetno]-=1
            agent.inventory[assetno]+=1

        heapq.heappush(events, agent.get_nextconsider(0))
        agents.append(agent)

    return assets, agents, events

def update():
    event = heapq.heappop(events)
    time = event.time
    times.append(time)
    if verbose: print(t,time,": agent",event.agent.name,event.type)
    #for j in range(0, m):
        #print(assets[j])
         
    #in a consideration event, an agent starts considering and we either add a
    #new consideration event to the queue (if they decided not to make an order)
    #or an addorder event to the queue (if they decided to make an order)
    if event.type == "consider":
        data = {"orders" : assets,"f" : f_value(time,event.agent.name), "m": m, "time": time}
        event_d = event.agent.consider(data = data)
        heapq.heappush(events, event_d)

    #in an addorder event, we add an agent's order to an asset's order book, clear
    #that asset's market, and add a new consideration event for the agent.
    if event.type == "addorder":
        asset = assets[event.order.assetno]
        asset.add_order(event.order, time)
        heapq.heappush(events,event.agent.get_nextconsider(event.time))


def payout():
    max_cards = max([agent.inventory[goalsuit] for agent in agents])
    max_agents = [agent for agent in agents if agent.inventory[goalsuit] == max_cards]
    bonus_split = bonus/len(max_agents)
    for agent in max_agents:
        agent.cash += bonus_split


if figgie:
    bonus, distribution, goalsuit = initialize_figgie()

assets, agents, events = initialize(bonus, distribution, goalsuit)
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
    winner = agents[np.argmax([agent.cash for agent in agents])]
    print("The winner is", winner.name)
