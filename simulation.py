from random import uniform, expovariate, shuffle
import heapq
from asset import Asset
from agent import Agent
from event import Event
import numpy as np
import math
import argparse

argp = argparse.ArgumentParser()
argp.add_argument('-m', '--assets', default=4)
argp.add_argument('-n', '--agents', default=4)
argp.add_argument('-t', '--type', default = "figgie")

args = argp.parse_args()

figgie = args.type == "figgie"
print(figgie)
suits = ["spades", "clubs", "hearts", "diamonds"]
goalsuit = -1
bonus = -1

times = []


# market will clear by matching the biggest bids with the smallest asks

n = 4 #number of agents
m = 4 #number of assets



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


    if figgie:
        names = suits
    else:
        names = range(0,m)
    for i in range(0,m):
        assets.append(Asset(name = names[i], number = i))
    
    agents = []
    #events is a min-priority queue, sorted by time
    events = []
    heapq.heapify(events)

    cards = distribution.copy()

    for i in range(0,n):
        if figgie:
            cash = 350
        else:
            cash = uniform(0,100)
        latency_i = uniform(0,100)
        latency_o = uniform(0, 100)
        rate_c = uniform(0,1)
            

        agent = Agent(cash = cash, latency_i = latency_i,
                      latency_o = latency_o, rate_c = rate_c,
                      m = m, name = i)
        if figgie:
            for i in range(0,10):
                assetno = np.random.choice(range(0,4), 1, p=np.array(cards)/sum(cards))[0]
                cards[assetno]-=1
                agent.inventory[assetno]+=1
        else:
            for i in range(0,m):
                agent.inventory[i] = math.floor(uniform(0,20))

        initial_consider = Event(time = expovariate(rate_c),etype = "consider", agent = agent)
        heapq.heappush(events, initial_consider)
        agents.append(agent)

    return assets, agents, events

def update():
    event = heapq.heappop(events)
    time = event.time
    times.append(time)
    print(t,time,": agent",event.agent.name,event.type)
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
        asset.addOrder(event.order)
        asset.clearMarket()
        heapq.heappush(events,event.agent.get_nextconsider(event.time))

def payout():
    maxagent = [agents[0]]
    for agent in agents:
        agent.cash += agent.inventory[goalsuit]*10
        if(agent.inventory[goalsuit] == maxagent[0].inventory[goalsuit] and agent not in maxagent):
            maxagent.append(agent)
        elif(agent.inventory[goalsuit] > maxagent[0].inventory[goalsuit]):
            maxagent = [agent]
    bonus_split = bonus/len(maxagent)
    for agent in maxagent:
        agent.cash += bonus_split





if figgie:
    bonus, distribution, goalsuit = initialize_figgie()

assets, agents, events = initialize(bonus, distribution, goalsuit)
print("Inventories before trading:--------------")
print_inventories()
for t in range(0,100):
    update()
print("Inventories after trading:---------------")
print_inventories()

if figgie:
    print("Adding bonuses---------------------------")
    print("goal suit:", goalsuit)
    print("bonus:", bonus)
    payout()
    print_inventories()
    winner = agents[0]
    for agent in agents:
        if agent.cash>winner.cash:
            winner = agent
    print("The winner is", winner.name)
