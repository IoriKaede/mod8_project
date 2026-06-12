
import numpy as np
import math
import random

from core import Simulation, Event
from statistics import TimeWeightedStatistic, SampleStatistic, Counter, _t_critical
from distributions import Exponential, Erlang

office_start = 8.0  # 08:00
office_end = 16.0  # 16:00

weekday_count = 5  # mon–fri
day = time%24
week = day%7

queue_emergency = []  # with prioity
queue_normal = []
queue_scheduled = []  # draw this  from index0 to normal
# scheduled =(0,1,0,...)

slots_per_hour_morning = 4
slots_per_hour_afternoon = 3
waiting_room_capacity = 3

lambda_e = 1
lambda_i = (21 + 6) / 24
lambda_op_request = 23 /8  # for service is 23/8

mu =  # service rate

slots_morning = 4
slots_afternoon = 3

chair_limit = 3

emergency = "emergency"
inpatient = "inpatient"
outpatient = "outpatient"

sc1 = 0  # index/ maybe not hard coded  original scanner_x
sc2 = 1
num_scanners = 2



def day_number(t):
    return int(t/24)

def day_of_week(t):
    return int(t/24)%7

def weekday_check(t):
    if day_of_week(t) < 5:
        return True
    else:
        return False

def is_office_hours(t):
    if not weekday_check(t):
        return False
    h = t % 24
    return office_start <= h < office_end

def next_oh_start(t):
    d = int(t / 24)
    h = t % 24
    if d%7 < 5:
        if h < office_start:
            return d*24 + office_start
        if h < office_end:
            return t
    d = d+1
    for i in range(10):
        if d%7 < 5:
            return d*24 + office_start
        d = d + 1
    return

def next_period_boundary(t):
    d = int(t/24)
    h = t % 24
    dow = d % 7
    if dow < 5:
        if h < office_start:
            return d * 24 + office_start
        elif h < office_end:
            return d * 24 + office_end
        else:
            return (d + 1) * 24
    else:
        days_to_monday = 7 - dow
        return (d + days_to_monday) * 24
    

def lambda_I(time):
    if not weekday_check(t):
        return 0.375
    h = time %24
    if 9.0 <= h < 12.0:
        return 0.375+1.5*math.pi*math.sin(math.pi*(h-9.0)/3.0)
    elif 12.0 <= h < 15.0:
        return 0.375+1.5*math.pi*math.sin(math.pi*(h-12.0)/3.0)
    return 0.375





class Arrival:
    def __init__(self):
        self.patient = 0
        self.queue_emergency = []
        self.queue_normal = []
        self.waiting_list = []

    def next_id(self):
        self.patient += 1
        return self.patient


    def eme_arrival(self,t,sim):

        #emergency_arrive(t):


        #schedule emergency_arrive t + exponential(lambda_emergency)

        p = new patient
        p.type = "emergency"
        p.patient_id = next_id()
        p.request_time = t
        p.arrival_time = t
        p.outside_room = false

        k = sim.find_free_scanner()
        if k != -1:
            sim.dispatch_to_scanner(k, p, t)
            if sim.warmup_done:
                sim.wait_times_e.append(0.0)
                sim.overflow_flags.append(0)
        else:

            if (len(self.queue_emergency) + len(self.queue_normal)) >= chair_limit:
                p.outside_room = True
                if sim.warmup_done:
                    sim.overflow_flags.append(1)
            else:
                if sim.warmup_done:
                    sim.overflow_flags.append(0)

            self.queue_emergency.append(p)


    def inp_arrival(self,t,sim)

        #schedule inpatient_arrive at + exponential(lambda_inpatient)

        p = new patient
        p.type = "inpatient"
        p.patient_id = next_id()
        p.request_time = t
        p.arrival_time = t
        p.outside_room = false
        p.request_during_oh = is_office_hours(t)?
        p.scanned_after_1600 = false

        k = sim.find_free_scanner()
        if k != -1:
            sim.dispatch_to_scanner(k, p, t)
            if sim.warmup_done and p.request_during_oh:
                sim.pm5_flags.append(0)  # Met timeline target
        else:
            if (len(self.queue_emergency) + len(self.queue_normal)) >= chair_limit:
                p.outside_room = True
                if sim.warmup_done:
                    sim.overflow_flags.append(1)
            else:
                if sim.warmup_done:
                    sim.overflow_flags.append(0)

            self.queue_normal.append(p)


    def op_arrival(self,t,sim):
        #op_request_arrive(t):

        #schedule op_request_arrive at t+exponential(lambda_op_request)

        p = new patient
        p.type = "outpatient"
        p.patient_id = next_id()
        p.request_time = t
        p.request_day = day_number(t)
        p.arrival_time = none
        p.outside_room = false

        earliest_day = p.request_day+ 1
        this_friday = p.request_day+(4-day_of_week(t))

        if earliest_day <= this_friday:
            monday_this_week = p.request_day-day_of_week(t)
            self.allocate_weekly_slots(monday_this_week)
            slot = self.find_earliest_slot(earliest_day, this_friday)
        else:
            slot = None

        if slot is not None:
            d, hour, slot_idx = slot
            self.slot_table[(d, hour, slot_idx)] = p.patient_id

            p.appt_day = d
            p.appt_time= d * 24+hour+slot_idx/slots_per_hour
            if random.random() <= 0.84:
                sim.schedule_event(p['appt_time'], "OP_ARRIVE", p)
        else:
            self.waiting_list.append(p)



#K = 3
#len(queue_emergency)+len(queue_normal) >K:

#count inpatients in the office hour
#count_ioh=0