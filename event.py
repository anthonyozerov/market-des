class Event:
    def __init__(self, agent, time, etype):
        self.agent = agent
        self.time = time
        self.type = etype

    def __lt__(self, other): return self.time < other.time
    def __eq__(self, other): return self.time == other.time
    def __gt__(self, other): return self.time > other.time
