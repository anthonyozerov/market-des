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

for t in range(0,100):
    event = heapq.heappop(events)
    time = event.time
    times.append(time)
    print("\n",t,time,": agent",event.agent.name,event.type)
    for j in range(0, m):
        print(assets[j])

    if event.type == "consider":
       event_d = event.agent.consider(data = [assets,f_value(time,agent.name),m])
       #if the agent wants to make an order, add it to the events
       if event_d != False:
           heapq.heappush(events, event_d)
    if event.type == "placeorder":
        agent = event.agent
        event_po = Event(time = agent.latency_o+time,etype = "addorder", agent = agent)
        event_po.order = event.order
        heapq.heappush(events, event_po)
    if event.type == "addorder":
        asset = assets[event.order.assetno]
        asset.addOrder(event.order)
        asset.clearMarket()

    for agent in agents:
        if not agent.considering:
            heapq.heappush(events,agent.get_nextconsider(time))
#to remove:
for asset in assets:
    asset.clearMarket()
