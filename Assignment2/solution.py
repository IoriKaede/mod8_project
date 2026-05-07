import numpy as np
import math
import random

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
random.seed(42)




def Erlang(k,mu):
    l = []
    count = 0
    while count in range(k):
        l.append(np.random.exponential(mu))
        count +=1
    return sum(l)


class UWC:
    def __init__(self,i):
        self.truck = i
        self.distinct = i
        self.home_district = [1,2,3] #range of i also below is
        self.type = 0
        self.queues = [[],[],[]]  #arrival time, waste type
        self.truck_status = "idle"  #idle,serving_home,serving_foreign
        self.truck_serving = None  # check if currently serving
        self.counter = 0
        #for rerouting rate self.reroute_count





    def arrival(self):
        i = self.distinct
        queue = self.queues
        #schedule next arrival = t+exp(λi)
        #arrival(time) to some distinct
        rd = random.random()
        if rd <= q_1:
            self.type = 1
            self.service_time = Erlang(k_1, mu_1)
        elif rd <= q_1+q_2:
            self.type = 2
            self.service_time = Erlang(k_2, mu_2)
        else:
            self.type = 3
            self.service_time = np.random.exponential(mu_3)

        #random waste type and append (t, type) to queues
        if self.truck_status =="idle":
            #service(truck=i, district=i)
        if self.truck_status =="serving foreign":
            #check rerouting condition


    def routing(self):
        #check home queue
        # iterate foreign districts in cyclic order, each with Bernoulli(p) trial

    def rerouting(self):
        #truck=i, request being reshcdule
        #for pending departure for truck i, vaild? +counter
        #put interrupted request to head of foreign queue[j]
        # send truck i to home distinct and service(truck=i, district=i)
        #increment reroute_count
    
    def service(self):
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


class steady_state:
    def __init__(self):

    #Regenerative method/Batch means method
