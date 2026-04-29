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
        self.cancel_event = None

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
        self.spread = 0
        self.length()

        self.spread= 0
        self.spread_last_time = 0
        self.spread_boolean=True
        self.spread_integral = 0


    def ba(self, order):
        if order.binary == "bid":
            bid_queue.append(order)
        else:
            ask_queue.append(order)

    def length(self):
        self.bid_length = TimeWeightedStatistic(initial_value=0.0, start_time=0.0) #need initial value
        self.ask_length = TimeWeightedStatistic(initial_value=0.0, start_time=0.0)

    def best_bid(self):
        if not bid_queue: #in case it is empty
            return
        return max(bid_queue,key=lambda order: order.price)

    def best_ask(self):
        if not ask_queue:
            return
        return min(ask_queue, key=lambda order: order.price)

    def queue_status(self, t):
        self.bid_length.update(t,len(bid_queue))
        self.ask_length.update(t, len(ask_queue))

    def spread_status(self, t):
        ba = self.best_ask()
        bb = self.best_bid()
        spread = {}
        if not self.ask_length or not self.bid_length: #for the object is not an integer use not :)
            spread[t] = "a"
        else:
            spread[t] = ba.price - bb.price  #subtract the price of best ba not themselves
        return spread

    def matching(self, sim):
        global count, T
        while bid_queue and ask_queue:
            bestb = self.best_bid()
            besta = self.best_ask()
            if bestb.price >=besta.price:
                t = sim.current_time
                self.spread_status(t)
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
                    T = t
                    sim.stop()
                    return  #use this to stop the function but not returning anything

class event_arrival(Event):
    def __init__(self,n,time,lob):
        self.time=time
        self.cancelled = False
        self.n=n
        self.lob=lob

    def execute(self, sim):   #I just found that the library could only call event.execute()
        global count, T
        t = sim.current_time
        lob=self.lob
        n = self.n
        if random.random() < 0.7:
            if random.random() < 0.5:
                ba = "bid"
            else:
                ba = "ask"
            price = limit_price(n)

            order = Limit_order(order=n, ba=ba, price=price, arrival_time=t)

            lob.limit_counter.increment() #I hope this increment will work(hope/ cannot use + because it is object


            lob.spread_status(t)
            lob.ba(order)
            lob.queue_status(t)
            lob.spread_status(t)

            cancel_time = cancellation(n, t)
            cancel_event = event_cancel(order,cancel_time,lob)
            sim.schedule(cancel_event)
            order.cancel_event = cancel_event
        else:
            if random.random() < 0.5:
                ba = "bid"
                opposite = lob.best_ask()
            else:
                ba = "ask"
                opposite = lob.best_bid()

            if opposite is not None: #in case the market order come without a bb/ba exist
                lob.spread_status(t)

                if opposite.binary == "bid":
                    bid_queue.remove(opposite)
                else:
                    ask_queue.remove(opposite)
                sim.cancel(opposite.cancel_event)
                opposite.matched = True
                opposite.status = "matched"
                lob.time.record(t - opposite.arrival_time)
                lob.queue_status(t)
                lob.spread_status(t)

                count += 1

                if count >= 500:
                    T = t
                    sim.stop()
                    return

            if count < 500:
                sim.schedule(event_arrival(n+1, t+arrival(n), lob)) # schedule for next arrival but arrival is returning a float not class


class event_cancel(Event):
    def __init__(self, order, time, lob):
        self.time = time
        self.cancelled = False
        self.order = order
        self.lob = lob

    def execute(self,sim):
        global count, T
        t = sim.current_time
        lob = self.lob
        order = self.order

        if order.matched:
            return

        lob.spread_status(t)

        if order.binary == "bid":
            bid_queue.remove(order)
        else:
            ask_queue.remove(order)

        order.cancelled = True
        order.status = "cancelled"
        lob.cancel_counter.increment()

        lob.queue_status(t)
        lob.spread_status(t)
        lob.matching(sim)


def simulation():
    lob = LOB()
    sim = Simulation()
    sim.schedule(event_arrival(0,0,lob))
    sim.run()
    return lob, sim


def time_avg_spread(spread):
    a = 0
    b = 0
    prevtime = 0
    for t in spread.keys:
        if spread[t] == "a":   # updates the time but does not add anything so we are not counting one spred for longer then we should because there was none
            prevtime = t
        else:
            a += (t - prevtime)*spread[t]
            b +=  (t - prevtime)
            prevtime = t
    t_avg_spread = a/b
    return t_avg_spread




if __name__ == "__main__":
    simulation()

    total_limit = LOB.limit_counter.value
    cancelled = LOB.cancel_counter.value