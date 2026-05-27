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

        self.N = N  #add this to change N later

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
        self.queue_stat[district].update(current_time, self.district_job[district])

        #truck = district
        #next_arrival_time = current_time + next_time
        if self.truck_status[district] =="idle":
            self.routing(district, current_time)
        else:  #should be if busy not elif
            if (self.truck_status[district] =="serving" and self.truck_at[district] !=district):
            #rerouting(,,)
            #check rerouting condition
                if K < len(self.queues[district]):
                    sim.schedule(Rerouting_Event(current_time, district, self))

            if len(self.queues[district]) == 1: #added see foreign truck ^^
                for foreign_truck in range(self.N):
                    if foreign_truck != district and self.truck_status[foreign_truck] == "idle":
                        if np.random.uniform() < p:
                            self.service(foreign_truck, district, current_time)
                            break  #


    def service_time(self, type):
        if type ==1:
            return Erlang(k_1,mu_1)
        elif type ==2:
            return Erlang(k_2,mu_2)
        else:
            return Exponential(mu_3)

    def routing(self,truck,current_time):
        #check home queue
        if len(self.queues[truck]) > 0:
            self.service(truck, truck, current_time)
            return
        #home = truck
        #queue = self.queues[i]
        foreign_districts = [(truck + a) % self.N for a in range(1, self.N)]
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

        self.reroute_count.increment()
        self.routing(truck, current_time)

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
        self.uwc=uwc

    def execute(self, sim):

        current_time = self.time
        d= self.district
        self.uwc.arrival(d, current_time, sim)

        if self.uwc.arrival_rate[d] >0:
            next_t = current_time + interarrival(self.uwc.arrival_rate[d])# Schedule the next arrival at this district
            if next_t != current_time:
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
        self.uwc = uwc

    def execute(self, sim):
        self.uwc.rerouting(self.truck, self.time, sim)








class steady_state:
    def __init__(self,uwc):
        self.uwc = uwc
        self.batch_mean_list = []  # one overall batch mean per batch
        self.batch_district = [[] for _ in range(N)]
    #Regenerative method/Batch means method

    def critical_t(self,df):
        t =_t_critical(0.95, df)
        return t



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

        def stop(instance=None):
        #self.uwc._new_cycle
            if not self.uwc._new_cycle:
                return False
            self.uwc._new_cycle = False
            min_cycles = 100
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
        self.uwc.sim.run(stop)  #def run(self, stop_condition: Optional[Callable[["Simulation"], bool]] = None)


    def confidence_interval_batch(self, r):
        n = len(r)
        if n ==0:
            return 0,0,0
        if n==1:
            return r[0], r[0], r[0]
        L_bar = sum(r) / n #division by zero
        r_var = sum((x - L_bar) ** 2 for x in r) / (n - 1)
        ci = self.critical_t(n - 1) * ((r_var/n)**0.5)
        return L_bar, L_bar - ci, L_bar + ci


    def batch_mean(self):
        #cycles = self.uwc.reg_cycles
        #if cycles:
        #    mean_cycle =sum(c["length"] for c in cycles)/len(cycles)
        #else:
        #    mean_cycle = 10

        #batch_length = mean
        #num_batchs = len(cycles) / batch_length
        num_batchs = 30 #idk but try, can modify/ try 30
        warm_up = 50
        #batch_length = mean_cycle *num_batchs
        batch_length = 200   #4*warmup
        warmup_end = self.uwc.sim.current_time + warm_up
        #stop condition
        def stop_warm(instance=None):
            return self.uwc.sim.current_time >= warmup_end
        self.uwc.sim.run(stop_warm)   #def run(self, stop_condition: Optional[Callable[["Simulation"], bool]] = None)
        #start single batch, ↑ cut warm up, ↓
        for b in range(num_batchs):
            self.uwc.batch_sojourn = [0]*self.uwc.N
            self.uwc.batch_count =[0]*self.uwc.N
            self.uwc.recording_batch = True

            batch_end = self.uwc.sim.current_time + batch_length
            def stop_batch(instance=None, end = batch_end):
                return self.uwc.sim.current_time >= end
            self.uwc.sim.run(stop_batch)

            self.uwc.recording_batch = False


            total_s = sum(self.uwc.batch_sojourn)
            total_c = sum(self.uwc.batch_count)
            if total_c>0:
                self.batch_mean_list.append(total_s / total_c)

            for i in range(self.uwc.N):
                if self.uwc.batch_count[i] > 0:
                    self.batch_district[i].append(self.uwc.batch_sojourn[i] / self.uwc.batch_count[i])










def verification_v1():
    global N, p, q_1, q_2, q_3, mu_3, K, l_1
    N = 1
    p = 0
    q_1, q_2, q_3 = 0, 0, 1  #make sure only type 3
    l_1 = 0.5
    mu_3 = 1
    K = float('inf') #infinity way

    theoretical_W = 1/(mu_3-l_1)
    print(f"v1, theoretical E[W]={theoretical_W}")

    arrival_rates = [l_1] #reg
    uwc_1 = UWC(N, arrival_rates)

    ss_1 = steady_state(uwc_1)
    ss_1.regenerative()

    reg_time = uwc_1.sim.current_time
    W_hat, ci_low, ci_high, res = ss_1.confidence_interval_reg()
    print(f"regenerative: simulated E[W]={W_hat}, CI=[{ci_low}, {ci_high}], relative precision={res}")



    if ci_low<=theoretical_W and theoretical_W<=ci_high:
        print("pass 95% ci")
    else:
        print("not 95%")

    #bm
    ss_1.batch_mean()
    bm_time = uwc_1.sim.current_time
    W_hat_b, ci_low_b, ci_high_b = steady_state(uwc_1).confidence_interval_batch(ss_1.batch_mean_list)
    print(f"batch mean: simulated E[W] = {W_hat_b}, CI = [{ci_low_b}, {ci_high_b}]")
    if ci_low_b <= theoretical_W and theoretical_W <= ci_high_b:
        print("pass 95% ci")
    else:
        print("not 95%")

    reroute = uwc_1.reroute_count.value
    print(f"{reroute}")


def verification_v2():
    global N, p, q_1, q_2, q_3, mu_3, K, l_1, l_2
    N = 2
    p = 1
    q_1, q_2,q_3 = 0,0,1
    l_1 = l_2 = 0.6
    mu_3 = 1
    K = float('inf')

    a = (2*0.6)/mu_3
    C_2_a = (a**2)/(2 + a)
    E_Wq = C_2_a/(2*mu_3-2*0.6)
    theoretical_W = E_Wq+(1/mu_3)
    print(f"v2,C(2,a)={C_2_a},E[W_q]= {E_Wq}, theortical E[W] = {theoretical_W}")


    arrival_rates = [l_1, l_2]
    uwc_2 = UWC(N, arrival_rates)
    ss_2 = steady_state(uwc_2)
    ss_2.regenerative()

    W_hat, ci_low, ci_high, precision = ss_2.confidence_interval_reg()
    print(f"simulated E[W] = {W_hat}, ci = [{ci_low}, {ci_high}], precision = {precision}")



    if ci_low <= theoretical_W and theoretical_W <= ci_high:
        print("pass 95% ci")
    else:
        print("not 95%")



    #bm
    ss_2.batch_mean()
    bm_time = uwc_2.sim.current_time
    W_hat_b, ci_low_b, ci_high_b = steady_state(uwc_2).confidence_interval_batch(ss_2.batch_mean_list)
    print(f"batch mean: simulated E[W] = {W_hat_b}, CI = [{ci_low_b}, {ci_high_b}]")
    if ci_low_b <= theoretical_W and theoretical_W <= ci_high_b:
        print("pass 95% ci")
    else:
        print("not 95%")

    reroute = uwc_2.reroute_count.value
    print(f"{reroute}")


def result_print_reg(uwc, steady_state, time_simulate):
    print("reg")
    lambdas = uwc.arrival_rate
    lambda_tot = sum(lambdas)
    W_hat_tot, W_low_tot, W_high_tot, _ = steady_state.confidence_interval_reg()









    E_W = []
    for i in range(uwc.N):
        #for in sojorn
        mean_w = uwc.sojourn_stats[i].mean()

        E_W.append(mean_w)
        local_low = mean_w*(W_low_tot/W_hat_tot)
        local_high = mean_w * (W_high_tot / W_hat_tot)
        print(f"Regenerative: waiting time: {i+1} district, E[W] = {mean_w} ,CI= [{local_low}, {local_high}])")


    print(f"reg E[W_tot] = {W_hat_tot}, CI tot =[{W_low_tot}, {W_high_tot}])")

    for i in range(uwc.N):
        L_i = lambdas[i] * E_W[i]   #little law l=lambda*W

        L_low_i = lambdas[i] * (E_W[i] * (W_low_tot / W_hat_tot))
        L_high_i = lambdas[i] * (E_W[i] * (W_high_tot / W_hat_tot))
        print(f"reg queue length: {i+1} district: L_{i + 1} = {L_i}, CI=[{L_low_i}, {L_high_i}])")


    L_tot = lambda_tot * W_hat_tot
    L_tot_low = lambda_tot * W_low_tot
    L_tot_high = lambda_tot * W_high_tot
    print(f"reg L_tot = {L_tot}, CI tot= [{L_tot_low}, {L_tot_high}])")




    for truck in range(len(uwc.serving_stat)):
        uti = uwc.serving_stat[truck].mean(time_simulate)

        uti_low=max(0,uti*(W_low_tot/W_hat_tot))
        uti_high = min(uti * (W_high_tot / W_hat_tot),1)
        print(f"reg {truck + 1} truck utilisation: {uti} , CI=[{uti_low}, {uti_high}])")


    reroute = uwc.reroute_count.value #counter() is not interger but need value

    rerouting_rate = reroute / time_simulate
    print(f"reg num of reroutings ={reroute}, reroute rate = {rerouting_rate}")
    return W_hat_tot, W_low_tot, W_high_tot

def result_print_bm(uwc, ss, time_simulate):
    print("bm")
    lambdas = uwc.arrival_rate
    lambda_tot = sum(lambdas)
    W_hat_tot, W_low_tot, W_high_tot = ss.confidence_interval_batch(ss.batch_mean_list)

    if W_hat_tot ==0:
        print("empty")
        return  W_hat_tot, W_low_tot,W_high_tot

    E_W = []
    for i in range(uwc.N):
        #for in sojorn
        if len(ss.batch_district[i]) != 0:
            mean_w = sum(ss.batch_district[i]) / len(ss.batch_district[i])
        else:
            mean_w =0

        E_W.append(mean_w)
        if W_hat_tot !=0:
            local_low = mean_w*(W_low_tot/W_hat_tot)
            local_high = mean_w * (W_high_tot / W_hat_tot)
        else:
            local_low, local_high = 0,0
        print(f"Batch mean : waiting time: {i+1} district, E[W] = {mean_w} ,CI= [{local_low}, {local_high}])")


    print(f"bm E[W_tot] = {W_hat_tot}, CI tot =[{W_low_tot}, {W_high_tot}])")

    for i in range(uwc.N):
        L_i = lambdas[i] * E_W[i]   #little law l=lambda*W
        if W_hat_tot != 0:

            L_low_i = lambdas[i] * (E_W[i] * (W_low_tot / W_hat_tot))
            L_high_i = lambdas[i] * (E_W[i] * (W_high_tot / W_hat_tot))
        else:
            L_low_i, L_high_i = 0,0
        print(f"bm queue length: {i+1} district: L_{i + 1} = {L_i}, CI=[{L_low_i}, {L_high_i}])")


    L_tot = lambda_tot * W_hat_tot
    L_tot_low = lambda_tot * W_low_tot
    L_tot_high = lambda_tot * W_high_tot
    print(f"bm L_tot = {L_tot}, CI tot= [{L_tot_low}, {L_tot_high}])")




    for truck in range(len(uwc.serving_stat)):
        uti = uwc.serving_stat[truck].mean(time_simulate)
        if W_hat_tot !=0:

            uti_low=max(0,uti*(W_low_tot/W_hat_tot))
            uti_high = min(uti * (W_high_tot / W_hat_tot),1)
        else:
            uti_low, uti_high = 0,0
        print(f"bm {truck + 1} truck utilisation: {uti} , CI=[{uti_low}, {uti_high}])")


    reroute = uwc.reroute_count.value #counter() is not interger but need value

    rerouting_rate = reroute / time_simulate
    print(f"bm num of reroutings ={reroute}, reroute rate = {rerouting_rate}")
    return W_hat_tot, W_low_tot, W_high_tot



def comparison_experiment():
    global N, K, p, q_1, q_2, q_3, mu_1, mu_2, mu_3, k_1, k_2, l_1, l_2, l_3
    N = 3
    K = 5
    q_1 = q_2 = q_3 = 1/3
    k_1, mu_1 = 2, 1
    k_2, mu_2 = 3, 1.5
    mu_3 = 1
    l_1 = l_2 = l_3 = 0.4
    arrival_rates = [l_1, l_2, l_3]
    random.seed(42)
    np.random.seed(42)


    p = 0.5
    uwc_1 = UWC(N, arrival_rates)
    ss_1 = steady_state(uwc_1)



    ss_1.regenerative()
    reg_time_1 = uwc_1.sim.current_time
    w_1, low_1, high_1 = result_print_reg(uwc_1, ss_1, reg_time_1)

    ss_1.batch_mean()
    bm_time_1= uwc_1.sim.current_time
    w_1_b, low_1_b, high_1_b = result_print_bm(uwc_1, ss_1, bm_time_1)

    p = 0.51
    uwc_2 = UWC(N, arrival_rates)
    ss_2 =steady_state(uwc_2)

    ss_2.regenerative()
    reg_time_2 = uwc_2.sim.current_time
    w_2, low_2, high_2 = result_print_reg(uwc_2, ss_2, reg_time_2)

    ss_2.batch_mean()
    bm_time_2 = uwc_2.sim.current_time
    w_2_b, low_2_b, high_2_b = result_print_bm(uwc_2, ss_2, bm_time_2)

    print(f"reg friendliness p=0.50: E[W]={w_1}, CI=[{low_1}, {high_1}], p=0.51: E[W]={w_2}, CI=[{low_2}, {high_2}]")
    print(f"bm friendliness p=0.50: E[W]={w_1_b}, CI=[{low_1_b}, {high_1_b}], p=0.51: E[W]={w_2_b}, CI=[{low_2_b}, {high_2_b}]")
    if high_1 < low_2 or high_2 < low_1:
        print("ci no overlap")
    else:
        print("ci overlap")


if __name__ == "__main__":
    verification_v1()
    verification_v2()
    comparison_experiment()




