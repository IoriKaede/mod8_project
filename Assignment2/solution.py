from asyncio import current_task

import numpy as np
import math
import random

from core import Simulation, Event
from statistics import TimeWeightedStatistic, SampleStatistic, Counter
from distributions import Exponential, Erlang


x = np.random.exponential(scale=...)

#Arrival rates: λ1 = λ2 = λ3 = 0.4
# Waste type probabilities: q1 = q2 = 1/3
# Type 1 service: Erlang(k1 = 2, µ1 = 1.0)
# Type 2 service: Erlang(k2 = 3, µ2 = 1.5)
# Type 3 service: Exp(µ3 = 1.0)
# Friendliness: p = 0.5
# Rerouting threshold: K = 5
#metrics:Waiting time.Queue length.Truck utilisation.
reroute_count = 0


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
    def __init__(self,i,N):
        self.truck = i
        self.district = i
        self.home_district = list(range(1, i + 1)) #range of i also below is
        self.type = 0 #arrival time, waste type
        self.queues = [[] for _ in range(N)]

        self.queue_stat = [TimeWeightedStatistic() for _ in range(self.N)]


        self.truck_status = "idle"  #idle,serving_home,serving_foreign/idle, serving
        self.truck_serving = None  # check if currently serving/current task
        self.counter = 0
        #for rerouting rate self.reroute_count
        self.district_job = [0]*n





    def arrival(self, current_time ,sim, l):
        i = self.district
        queue = self.queues

        #schedule next arrival = t+exp(λi)
        next_time = interarrival(l)

        #arrival(time) to some distinct
        rd = np.random.uniform()
        if rd <= q_1:
            self.type = 1
        elif rd <= q_1+q_2:
            self.type = 2
        else:
            self.type = 3

        type = self.type
        record = (current_time, type)  # (arrival_time, type)
        self.queues[i].append(record)
        self.district_job[i] += 1
        self.queue_stat[i].update(current_time, self.district_job[i])

        truck = self.district
        next_arrival_time = current_time + next_time
        if self.truck_status =="idle":
            service(truck=i, district=i)
            self.routing(truck, current_time)
        elif self.truck_status =="serving foreign":
            #rerouting(,,)
            #check rerouting condition



    def service_time(self):
        if self.type ==1:
            return Erlang(k_1,mu_1)
        elif self.type ==2:
            return Erlang(k_2,mu_2)
        else:
            return Exponential(mu_3)

    def routing(self,i,p):
        #check home queue
        queue = self.queues[i]
        if queue is not []:
            truck_current_assignment = queue[0]
            #service(truck, region)
            return
        else:
            if self.truck_status ="idle":
            for i in range(3):
                if queue[i] is not []:
                    if np.random.random() < p:
                        #assign the truck to forign region
                        self.truck_status = "serving foreign"
                    else:
                        pass

            # iterate foreign districts in cyclic order, each with Bernoulli(p) trial


    def rerouting(self,district,home):
        K = len(self.district_job)
        queue = self.queues[district]
        home_queue = self.queues[truck]
        if K>5:
            #send the truck to its home
            self.truck_status = "serving local"
            queue.insert(0,self.truck_serving)
            #return the tasks to the queue of region
            self.truck_serving = home_queue[0]









        #truck=i, request being reshcdule

        #for pending departure for truck i, vaild? +counter
        #put interrupted request to head of foreign queue[j]
        # send truck i to home distinct and service(truck=i, district=i)
        #increment reroute_count
    
    def service(self,truck, district,time):
        i = truck
        queue = self.queues[district]
        st = service_time()
        ending_time = time+st



        time = ending_time
        queue.remove()





        #truck, district
        #from queues[district] do requests?
        #random service time S from waste-type
        #schedule departure t+S
        #update truck_status
    
    def departure(self):
        #trucki, district, request
        # record sojourn time: W = t - request.arrival_time
        #routing/service
        if #no work found:
            .status = "idle"


    def time_pushing(self):
        #min(timepoint)

class steady_state:
    def __init__(self):

    #Regenerative method/Batch means method
