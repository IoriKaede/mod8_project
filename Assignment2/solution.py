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
class UWC:
    def __init__(self,i):
        self.truck = i
        self.distinct = i
        self.home_district = [1,2,3] #range of i also below is
        self.waste = [1,2,3]
        self.queues = [0,0]  #arrival time, waste type
        self.truck_status = "idle"  #idle,serving_home,serving_foreign
        self.truck_serving = None  # check if currently serving
        self.counter = 0
        #for rerouting rate self.reroute_count





    def arrival(self):
        i = self.distinct
        #schedule next arrival = t+exp(λi)
        #random waste type and append (t, type) to queues
        if self.truck_status =="idel":
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
