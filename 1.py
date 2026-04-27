import math
import random
from core import Simulation, Event, StopSimulation
from statistics import TimeWeightedStatistic, SampleStatistic, Counter
from distributions import Sequence

bid_queue = []
ask_queue = []
count = 0
random.seed(42)

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
    return round(100 + 2 * math.sin(n * math.e), 2)

def cancellation(n, t):
    return 30 * (1 + math.cos(n) ** 2) + t

class LOB:
    def __init__(self):
        self.time = SampleStatistic()
        self.cancel_counter = Counter()
        self.limit_counter = Counter()
        self.cancellation_rate = 0 #rate=cancel counter/limit counter
        self.spread = 0


    def ba(self):
        if random.random()<0.5:#do to 0.5 prob
            ba = "bid"
        else:
            ba = "ask"

        if ba == "bid":
            bid_queue.append(#order)
        else:
            ask_queue.append(#order)

    def length(self):
        self.bid_length = TimeWeightedStatistic()
        self.ask_length = TimeWeightedStatistic()

    def best_bid(self):
        return max(bid_queue,key=lambda order: order.price)

    def best_ask(self):
        return min(ask_queue, key=lambda order: order.price)

    def queue_status(self, t):
        self.bid_length.update(t,len(bid_queue))
        self.ask_length.update(t, len(ask_queue))

    def spread_status(self, t):
        #spread

    def matching(self, sim):
        global count
        bestb = self.best_bid()
        besta = self.best_ask()
        t = sim.current_time
        #self.spread_status(t)
        bid_queue.remove(bestb)
        ask_queue.remove(besta)
        sim.cancel(bestb.cancel_event)
        sim.cancel(besta.cancel_event)
        bestb.matched = True
        besta.matched = True
        bestb.status = "matched"
        besta.status = "matched"
        self.time.record(t - bestb.arrival_time)
        self.time.record(t - besta.arrival_time)
        self.queue_status(t)
        self.spread_status(t)
        count += 1
        if count >= 500:
            sim.stop()
            return t


class arrival(event):
    def __init__(self):



class cancel(event):
    def __init__(self):






def simulation():
    lob = LOB()
    sim = Simulation()
    sim.schedule()
    sim.run()
    return lob, sim


if __name__ == "__main__":
    simulation()

    total_limit = LOB.limit_counter.value
    cancelled = LOB.cancel_counter.value