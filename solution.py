import math
import random
from core import Simulation, Event, StopSimulation
from statistics import TimeWeightedStatistic, SampleStatistic, Counter
from distributions import Sequence

bid_queue = []
ask_queue = []
count = 0
random.seed(42)
T = 0

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

        self.spread_last_time = 0
        self.spread_check=False
        self.spread_integral = 0
        self.spread_last_value =0
        self.spread_total_time = 0


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
            return None
        return max(bid_queue,key=lambda order: order.price)

    def best_ask(self):
        if not ask_queue:
            return None
        return min(ask_queue, key=lambda order: order.price)

    def queue_status(self, t):
        self.bid_length.update(t,len(bid_queue))
        self.ask_length.update(t, len(ask_queue))

    def spread_status(self, t):
        ba = self.best_ask()
        bb = self.best_bid()
        spread = {}
        if ba is None or bb is None: #for the object is not an integer use not :)
            spread[t] = None #undefined
        else:
            spread[t] = ba.price - bb.price  #subtract the price of best ba not themselves
        return spread

    def spread_object(self, t):  #same thing as above but make track of time
        ba = self.best_ask()
        bb = self.best_bid()

        if self.spread_check:
            dt = t - self.spread_last_time
            self.spread_integral += self.spread_last_value*dt #the area under line
            self.spread_total_time += dt
            self.spread_last_time = t

        if ba is None or bb is None:
            self.spread_check = False
        else:
            self.spread = ba.price - bb.price
            self.spread_last_value = self.spread
            self.spread_last_time = t
            self.spread_check = True



    def matching(self, sim):
        global count, T
        while bid_queue and ask_queue:
            bestb = self.best_bid()
            besta = self.best_ask()
            if bestb.price >=besta.price:
                t = sim.current_time
                self.spread_object(t)
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
                self.spread_object(t)
                count += 1
                if count >= 500:
                    T = t
                    sim.stop()
                    return  #use this to stop the function but not returning anything
            else:
                break

class event_arrival(Event):
    def __init__(self,n,time,lob):
        self.time=time
        self.cancelled = False
        self.n=n
        self.lob=lob
        self._seq = 0 #this is for core.py to check

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


            lob.spread_object(t)
            lob.ba(order)
            lob.queue_status(t)
            lob.spread_object(t)

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
                lob.spread_object(t)

                if opposite.binary == "bid":
                    bid_queue.remove(opposite)
                else:
                    ask_queue.remove(opposite)
                sim.cancel(opposite.cancel_event)
                opposite.matched = True
                opposite.status = "matched"
                lob.time.record(t - opposite.arrival_time)
                lob.queue_status(t)
                lob.spread_object(t)

                count += 1

                if count >= 500:
                    T = t
                    sim.stop()
                    return

        if count < 500:
            lob.matching(sim)
            sim.schedule(event_arrival(n+1, t+arrival(n), lob)) # schedule for next arrival but arrival is returning a float not class


class event_cancel(Event):
    def __init__(self, order, time, lob):
        self.time = time
        self.cancelled = False
        self.order = order
        self.lob = lob
        self._seq = 0

    def execute(self,sim):
        global count, T
        t = sim.current_time
        lob = self.lob
        order = self.order

        if order.matched:
            return

        lob.spread_object(t)

        if order.binary == "bid":
            bid_queue.remove(order)
        else:
            ask_queue.remove(order)

        order.cancelled = True
        order.status = "cancelled"
        lob.cancel_counter.increment()

        lob.queue_status(t)
        lob.spread_object(t)
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
    for t in spread.keys(): #changed a bit grammar
        if spread[t] is None:   # updates the time but does not add anything so we are not counting one spred for longer then we should because there was none
            prevtime = t
        else:
            a += (t - prevtime)*spread[t]
            b +=  (t - prevtime)
            prevtime = t
    if b !=0:
        t_avg_spread = a/b
    return t_avg_spread




if __name__ == "__main__":
    lob,sim = simulation()

    total_limit = lob.limit_counter.value
    cancelled = lob.cancel_counter.value

    #avg_spread = time_avg_spread()
    if lob.spread_total_time > 0:
        avg_spread = lob.spread_integral / lob.spread_total_time
    else:
        avg_spread = 0
    print(f"T:{T}, total:{total_limit} , matched:{total_limit - cancelled}, cancelled:{cancelled}"
          f"num of trades:{count}, time avg spread{avg_spread}, avg time{lob.time.mean()}, cancellation rate:{lob.cancel_counter.fraction(total_limit)}"
          f"avg bid queue length{lob.bid_length.mean(T)}, ask:{lob.ask_length.mean(T)}")
