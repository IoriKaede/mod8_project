import math
import random
from core import Simulation, Event, StopSimulation
from statistics import TimeWeightedStatistic, SampleStatistic, Counter
from distributions import Sequence



class Limit_order:
    def __init__(self, order, ba, price, arrival_time):
        self.order = order
        self.status = "arrived"#cancelled/matched
        self.binary = ba#bid/ask
        self.price = price
        self.arrival_time = arrival_time
        self.matched = False
        self.cancelled = False

def arrival(n):
    return 15 * ((1 + math.sin(n * math.pi / 12)) ** 2) + 2

def limit_price(n):
    return 100 + 2 * math.sin(n * math.e), 2

def cancellation(n, t):
    return 30 * (1 + math.cos(n) ** 2) + t

    class LOB:
    def __init__(self):


    def best_bid(self):


    def best_ask(self):


    def queue_status(self, t):


    def spread_status(self, t):


    def matching(self, sim):


if __name__ == "__main__":
    simulation()





