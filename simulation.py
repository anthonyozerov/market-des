from random import uniform, expovariate
import heapq
from asset import Asset
from agent import Agent
from event import Event
import numpy as np
import math

times = []

#events is a min-priority queue, sorted by time
events = []
heapq.heapify(events)

assets = [] #each Asset object will have:
# max priority queue for buys
# min priority queue for sells

# market will clear by matching the biggest bids with the smallest asks

n = 4 #number of agents
m = 4 #number of assets

for i in range(0,m):
    assets.append(Asset(name=i))

agents = []

def f_value(time,k):
    return np.zeros(m)+1+math.sin(time+k)

def print_inventories():
    print("Agent inventories:")
    assets_total = np.zeros(m)
    cash_total = 0
    for agent in agents:
        assets_total+=np.array(agent.inventory)
        cash_total += agent.cash
        fmt = "{0}: ${1}, assets {2}"
        print(fmt.format(agent.name, agent.cash, agent.inventory))
    print("Total cash:", cash_total)
    print("Total assets:", assets_total)


for i in range(0,n):
    cash = uniform(0,100)
    latency_i = uniform(0,100)
    latency_o = uniform(0, 100)
    rate_c = uniform(0,1)
    agent = Agent(cash = cash, latency_i = latency_i,
                  latency_o = latency_o, rate_c = rate_c,
                  m = m, name = i)
    for i in range(0,m):
        agent.inventory[i] = uniform(0,20)
    initial_consider = Event(time = expovariate(rate_c),etype = "consider", agent = agent)
    heapq.heappush(events, initial_consider)
    agents.append(agent)


print_inventories()

for t in range(0,100):
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
        data = {"orders" : assets,"f" : f_value(time,agent.name), "m": m, "time": time}
        event_d = event.agent.consider(data = data)
        heapq.heappush(events, event_d)

    #in an addorder event, we add an agent's order to an asset's order book, clear
    #that asset's market, and add a new consideration event for the agent.
    if event.type == "addorder":
        asset = assets[event.order.assetno]
        asset.addOrder(event.order)
        asset.clearMarket()
        heapq.heappush(events,event.agent.get_nextconsider(event.time))

print_inventories()
