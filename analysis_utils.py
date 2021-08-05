import pickle
import numpy as np
import os
import matplotlib.pyplot as plt
import math

import tikzplotlib

class Trader:
    pass

class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'Trader':
            return Trader
        return super().find_class(module, name)

def load_data(filename):
    return CustomUnpickler(open(os.path.join('./output', filename),'rb')).load()

def plot_expectations(filename):
    data = CustomUnpickler(open(os.path.join('./output', filename),'rb')).load()
    for i in range(0,4):
        fig, ax = plt.subplots()
        names = []
        for j in range(0,4):
            agent = data['agents'][j]
            if(hasattr(agent, 'buy_expectations')):
                expectations = agent.buy_expectations
                plt.plot(expectations[:,0],expectations[:,i+1])
                names.append(agent.name + ", buy")
            if(hasattr(agent, 'sell_expectations')):
                expectations = agent.sell_expectations
                plt.plot(expectations[:,0],expectations[:,i+1])
                names.append(agent.name + ", sell")
            elif(hasattr(agent, 'expectations')):
                expectations = agent.expectations
                if(len(expectations)>0):
                    plt.plot(expectations[:,0],expectations[:,i+1])
                    names.append(agent.name)
        plt.ylabel('value')
        plt.xlabel('time')
        plt.legend(labels = names)
        titlestring = 'Agents\' view of suit '+str(i)+'\'s value over time'
        if i == data['goalsuit']:
            titlestring += " (GOAL SUIT)"
        plt.title(titlestring)
        fig.savefig('graphs/'+filename+'.'+str(i)+"_expectations.svg", facecolor='white', transparent=False)
        tikzplotlib.save('graphs/'+filename+'.'+str(i)+'_expectations.tex', axis_height = '\\figH', axis_width = '\\figW')

def plot_rewards(input_base, iterations, output, ylab = True):
    endcash = np.zeros([iterations,4])
    endpayout = np.zeros([iterations,4])
    avg_trades = 0
    for i in range(0, iterations):
        filename = input_base + '.' +str(i)
        data = load_data(filename)
        cash = [agent.cash for agent in data['agents']]
        payout = [agent.payout for agent in data['agents']]
        names = [agent.name for agent in data['agents']]
        endcash[i,:] = cash
        endpayout[i,:] = payout
        avg_trades += sum([len(asset.trades) for asset in data["assets"]])/iterations
    cashmeans = np.mean(endcash,axis=0)
    payoutmeans = np.mean(endpayout,axis=0)
    cashstds  = np.std(endcash,axis=0)
    payoutstds  = np.std(endpayout,axis=0)

    fig, ax = plt.subplots()
    color = [agent.color for agent in data['agents']]
    ax.bar(range(0,4),cashmeans,color = color, edgecolor = "black")
    ax.errorbar(range(0,4), cashmeans, yerr = cashstds*2/math.sqrt(iterations),fmt="none", color="grey",capsize=5)
    ax.bar(range(0,4),payoutmeans,color = color,bottom=cashmeans, edgecolor = "black")
    ax.errorbar(range(0,4), payoutmeans+cashmeans, yerr=payoutstds*2/math.sqrt(iterations), fmt="none", color="black",capsize=5)
    ax.set_ylim((0,700))
    if ylab:
        ax.set_ylabel("Mean cash+payout")
    ax.set_xlabel("Agent")
    ax.set_xticks(range(0,4))
    ax.set_xticklabels(names)
    plt.axhline(y=350, color='grey', linestyle='--')
    plt.axhline(y=400, color='black', linestyle='--')
    #plt.title('Final cash+payout of agents in '+str(iterations)+' simulations')
    fig.savefig('graphs/'+output+".svg", facecolor='white', transparent=False)
    fig.tight_layout()
    tikzplotlib.save('graphs/'+output+'.tex', axis_height = '\\figH', axis_width = '\\figW')

def plot_prices(filename):
    data = load_data(filename)
    fig, ax = plt.subplots()
    for i in range(data["m"]):
        asset = data['assets'][i]
        price_series = asset.price_series
        times = price_series[:,0]
        prices = price_series[:,1]
        plt.plot(times,prices)
    plt.ylabel('price')
    plt.xlabel('time')
    plt.title('Asset prices over time')
    plt.legend(labels = range(data["m"]))
    plt.show()
    fig.savefig('graphs/'+filename+"_prices.svg", facecolor='white', transparent=False)

def plot_cashes(filename):
    data = load_data(filename)
    agents = data['agents']
    names = []
    fig, ax = plt.subplots()
    for agent in agents:
        cashes = agent.cashes
        times = cashes[:,0]
        amounts = cashes[:,1]
        plt.plot(times,amounts)
        names.append(agent.name)
    plt.ylabel('cash')
    plt.xlabel('time')
    plt.title('Agents\' cash over time')
    plt.legend(labels=names)
    plt.show()
    fig.savefig('graphs/'+filename+"_cashes.svg", facecolor='white', transparent=False)

import matplotlib.lines as mlines
def plot_orders(filename, assetno, agentno):
    fig, ax = plt.subplots()
    data = load_data(filename)
    agent = data['agents'][agentno]
    orders = agent.orders
    orders = [order for order in orders if order.assetno == assetno]
    prices = [order.price for order in orders]
    colors = ["red" if order.buy else "green" for order in orders]
    alphas = [0.5 if order.deleted else 1 for order in orders]
    plt.scatter(range(0,len(orders)),prices,color = colors, alpha=alphas)
    buyhandle = mlines.Line2D([],[], color='red', marker='.', linestyle='None', label='buy')
    sellhandle = mlines.Line2D([],[], color='green', marker='.', linestyle='None', label='sell')
    plt.legend(handles=[buyhandle,sellhandle])
    plt.ylabel('price')
    plt.xlabel('order index')
    plt.title(agent.name+'\'s orders for suit '+str(assetno))
    plt.show()
    fig.savefig('graphs/'+filename+"_orders"+str(assetno)+'.'+agent.name+".svg", facecolor='white', transparent=False)
