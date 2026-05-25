from itertools import cycle

import numpy as np
import math
import random

from jupyter_client.kernelspec import NATIVE_KERNEL_NAME
from prompt_toolkit.key_binding.bindings.named_commands import self_insert

from core import Simulation, Event
from statistics import TimeWeightedStatistic, SampleStatistic, Counter, _t_critical
from distributions import Exponential, Erlang



#Arrival rates: λ1 = λ2 = λ3 = 0.4
# Waste type probabilities: q1 = q2 = 1/3
# Type 1 service: Erlang(k1 = 2, µ1 = 1.0)
# Type 2 service: Erlang(k2 = 3, µ2 = 1.5)
# Type 3 service: Exp(µ3 = 1.0)
# Friendliness: p = 0.5
# Rerouting threshold: K = 5
#metrics:Waiting time.Queue length.Truck utilisation.
#reroute_count = 0


l_1 ,l_2 ,l_3 = 0.4, 0.4, 0.4
q_1,q_2,q_3 = 1/3, 1/3, 1/3
k_1 = 2
mu_1 = 1.0
k_2 = 3
mu_2 = 1.5
mu_3 = 1.0
p = 0.5
K = 5
M= 3
N=3
random.seed(42)
np.random.seed(42)




def Erlang(k,mu):  #changed to np
    l = np.random.exponential(1.0/mu, k) #scale, size
    return np.sum(l)
#mu is rate so scale is 1/mu
def Exponential(mu):
    return np.random.exponential(scale=1.0 / mu)

def interarrival(la): #lambda, poisson arrival
    return np.random.exponential(scale=1.0 / la)





class UWC:
    def __init__(self,N,arrival_rate): #remove i

        #self.home_district = list(range(1, i + 1)) #range of i also below is
        self.type = 0 #arrival time, waste type/last drawn
        self.queues = [[] for _ in range(N)]



        self.truck_status = ['idle'] * N  #idle,serving_home,serving_foreign/idle, serving
        self.truck_task = [None] *N  # check if currently serving/current task
        self.counter = 0
        #for rerouting rate self.reroute_count
        self.district_job = [0]* N
        self.queues = [[] for _ in range(N)]

        self.arrival_rate = arrival_rate
        self.truck_at = [None] * N
        self.truck_depart = [None] *N

        self.sojourn_stats = [SampleStatistic() for _ in range(N)]
        self.queue_stat = [TimeWeightedStatistic() for _ in range(N)]
        self.serving_stat = [TimeWeightedStatistic() for _ in range(N)]

        self.reroute_count = Counter()

        self.reg_cycles = []  # list of completed cycle dicts
        self.cycle_start = 0  # when the current cycle start
        self.cycle_sojourn = 0  # sojourn accumulated in current cycle
        self.cycle_count = 0  # completions in current cycle
        self._new_cycle = False  # bollean a new cycle just closed?

        self.sim = Simulation()

        self.recording_batch = False
        self.batch_sojourn = [0]*N
        self.batch_count = [0] * N


    def arrival(self, district, current_time ,sim):
        #i = self.district
        #queue = self.queues

        #schedule next arrival = t+exp(λi)
        #next_time = interarrival(l)

        #arrival(time) to some distinct
        rd = np.random.uniform()
        if rd <= q_1:
            self.type = 1
        elif rd <= q_1+q_2:
            self.type = 2
        else:
            self.type = 3

        waste_type = self.type
        record = (current_time, waste_type)  # (arrival_time, type)
        self.queues[district].append(record)
        self.district_job[district] += 1
        self.queue_stat[district].update(current_time, self.district_job[i])

        truck = district
        #next_arrival_time = current_time + next_time
        if self.truck_status =="idle":
            self.routing(district, current_time)
        elif self.truck_status =="serving" and self.truck_at[district] !=district:
            #rerouting(,,)
            #check rerouting condition
            if K < len(self.queues[district]):
                sim.schedule(Rerouting_Event(current_time, district, self))



    def service_time(self, type):
        if type ==1:
            return Erlang(k_1,mu_1)
        elif type ==2:
            return Erlang(k_2,mu_2)
        else:
            return Exponential(mu_3)

    def routing(self,truck,current_time):
        #check home queue
        home = truck
        #queue = self.queues[i]
        foreign_districts = [a for a in range(1, N)]
        for fd in foreign_districts:
            if len(self.queues[fd]) > 0:
                if np.random.uniform() < p:
                    self.service(truck, fd, current_time)
                    return

            # iterate foreign districts in cyclic order, each with Bernoulli(p) trial


    def rerouting(self, truck, current_time, sim):
        if self.truck_status[truck] == 'idle':
            return
        if self.truck_at[truck] == truck:   # stop when truck is already at home district
            return
        foreign_district = self.truck_at[truck]    # where truck was serving
        interrupted_task = self.truck_task[truck]   # what it was in the middle of

        if self.truck_depart[truck] is not None:
            sim.cancel(self.truck_depart[truck])#cancel departure

        self.queues[foreign_district].insert(0, interrupted_task)#interruptted task to the 0of queue

        self.serving_stat[truck].update(current_time, 0)  # 0=idle
        self.truck_status[truck] = 'idle'
        self.truck_at[truck] = None
        self.truck_task[truck] = None
        self.truck_depart[truck] = None

        self.routing(truck, current_time)

        self.reroute_count.increment()
        #increment reroute_count
    
    def service(self,truck, district,current_time):
        current_task = self.queues[district].pop(0)
        self.truck_status[truck] = 'serving'
        self.truck_at[truck] = district
        self.truck_task[truck] = current_task
        self.serving_stat[truck].update(current_time, 1)  # 1 = serving
        service_time = self.service_time(current_task[1])  # current_task[1] = waste_type

        depart = Departure_Event(current_time + service_time, truck, district, current_task, self)
        self.truck_depart[truck] = depart
        self.sim.schedule(depart)

        #truck, district
        #random service time S from waste-type
        #schedule departure t+S
        #update truck_status
    
    def departure(self, truck, district, current_task, current_time):
        sojourn = current_time - current_task[0]  # current_task[0] = arrival_time
        self.sojourn_stats[district].record(sojourn)

        self.cycle_sojourn += sojourn
        self.cycle_count += 1

        self.district_job[district] -= 1
        self.queue_stat[district].update(current_time, self.district_job[district])


        self.serving_stat[truck].update(current_time, 0)
        self.truck_status[truck] = 'idle'
        self.truck_at[truck] = None
        self.truck_task[truck] = None
        self.truck_depart[truck] = None



        self.routing(truck, current_time)
        #check all idle?
        self.cycle_check(current_time)

        #if self.steady_state.recording_batch:
        #    self.steady_state.batch_sojourn[district]+=sojourn
        #    self.steady_state.batch_count[district]+= 1

        if self.recording_batch:
            self.batch_sojourn[district] += sojourn
            self.batch_count[district] += 1


    def cycle_check(self, current_time):
        all_idle  = all(s == 'idle' for s in self.truck_status)
        all_empty = all(len(q) == 0 for q in self.queues)

        if all_idle and all_empty:
            cycle_len = current_time - self.cycle_start
            if cycle_len > 0:
                self.reg_cycles.append({
                    'sojourn' : self.cycle_sojourn,
                    'count'   : self.cycle_count,
                    'length'  : cycle_len,
                })
                self._new_cycle = True   # tell steady_state to recheck CI

            # Reset for the next cycle
            self.cycle_start   = current_time
            self.cycle_sojourn = 0
            self.cycle_count   = 0




class Arrival_Event(Event):
    def __init__(self, time, district, uwc):
        super().__init__(time)
        self.district = district
        self.uwc      = uwc

    def execute(self, sim):
        current_time = self.time
        d= self.district
        self.uwc.arrival(d, current_time, sim)

        next_t = current_time + interarrival(self.uwc.arrival_rate[d])# Schedule the next arrival at this district
        sim.schedule(Arrival_Event(next_t, d, self.uwc))


class Departure_Event(Event):
    def __init__(self, time, truck, district, current_task, uwc):
        super().__init__(time)
        self.truck = truck
        self.district = district
        self.current_task = current_task      # (arrival_time, waste_type)
        self.uwc = uwc

    def execute(self, sim):
        if self.cancelled:
            return
        self.uwc.departure(self.truck, self.district, self.current_task, self.time)



class Rerouting_Event(Event):
    def __init__(self, time, truck, uwc):
        super().__init__(time)
        self.truck = truck
        self.uwc   = uwc

    def execute(self, sim):
        self.uwc.rerouting(self.truck, self.time, sim)








class steady_state:
    def __init__(self,uwc):
        self.uwc = uwc
        self.batch_mean = []  # one overall batch mean per batch
        self.batch_district = [[] for _ in range(N)]
    #Regenerative method/Batch means method

    def critical_t(self,df):
        t =_t_critical(0.95, df)



    def confidence_interval_reg(self):

        cycles = self.uwc.reg_cycles #(sojurn, count, lenth)
        n = len(cycles)

        W_total = sum(c["sojourn"] for c in cycles)
        M = sum(c["count"] for c in cycles)

        W_hat = W_total/M
        M_bar = M/n
        N= []
        for c in cycles:
            N.append(c["sojourn"]-W_hat*c["count"])
        N_bar = sum(N)/n
        N_var = sum((n_k - N_bar)**2 for n_k in N)/(n-1)

        ci = self.critical_t(n-1)*((N_var/(n*(M_bar**2))))**0.5
        result = ci/W_hat #half stop
        return W_hat, W_hat-ci, W_hat +ci, result



    def regenerative(self):
        #call the arrival
        for i in range(N):
            self.uwc.sim.schedule(Arrival_Event(0,i,self.uwc))

        def stop():
        #self.uwc._new_cycle
            if not self.uwc._new_cycle:
                return False
            self.uwc._new_cycle = False
            min_cycles = 10
            max_cycles = 1000
            n = len(self.uwc.reg_cycles)
            if n < min_cycles:
                return False
            if n >= max_cycles:
                return True

            result = self.confidence_interval_reg()
            if result is None:
                return False
            _, _, _, res = result
            if res <= 0.1:  #10%
                return True
            else:
                return False


    #stop condition

    #run simulation
        self.uwc.sim.run(stop())  #def run(self, stop_condition: Optional[Callable[["Simulation"], bool]] = None)


    def confidence_interval_batch(self, r):
        n = len(r)
        L_bar = sum(r) / n
        r_var = sum((x - L_bar) ** 2 for x in r) / (n - 1)
        ci = self.critical_t(n - 1) * ((r_var/n)**0.5)
        return L_bar, L_bar - ci, L_bar + ci


    def batch_mean(self):
        cycles = self.uwc.reg_cycles
        mean_cycle =sum(c["length"] for c in cycles)/len(cycles)

        #batch_length = mean
        #num_batchs = len(cycles) / batch_length
        num_batchs = 10 #idk but try
        warm_up = mean_cycle
        batch_length = mean_cycle *num_batchs
        warmup_end = self.uwc.current_time + warm_up
        #stop condition
        def stop_warm():
            return self.uwc.current_time >= warmup_end
        self.uwc.sim.run(stop_warm())   #def run(self, stop_condition: Optional[Callable[["Simulation"], bool]] = None)
        #start single batch, ↑ cut warm up, ↓
        for b in range(num_batchs):
            self.batch_sojourn = [0]*N
            self.batch_count =[0]*N
            self.recording_batch = True

            batch_end = self.current_time + batch_length
            def stop_batch():
                return self.uwc.current_time >= batch_end
            self.uwc.sim.run(stop_batch())

            self.recording_batch = False


            total_s = sum(self.batch_sojourn)
            total_c = sum(self.batch_count)
            self.batch_mean.append(total_s / total_c)

            for i in range(N):
                if self.batch_count[i] > 0:
                    self.batch_district[i].append(self.batch_sojourn[i] / self.batch_count[i])




    def result(self):
        uwc = self.uwc









