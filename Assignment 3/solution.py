
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






class Arrival:
    def __init__():
        self.time = #9.5 = 9:30 in minutes

        day = time\24
        week = day\7

        queue_emergency = [] #with prioity
        queue_normal = []
        queue_scheduled = []#draw this  from index0 to normal

        waiting_


    def eme_arrival(self):

        emergency_arrive(t):


        schedule emergency_arrive t + exponential(lambda_emergency)

        p = new patient
        p.type = "emergency"
        p.patient_id = next_id()
        p.request_time = t
        p.arrival_time = t
        p.outside_room = false


        k = find_free_scanner()

        if k != -1:

            dispatch_to_scanner(k, p, t)

            if warmup_done:
                wait_times_e.append(0.0)
                overflow_flags.append(0)
        else:
            #in queue p,t


    def inp_arrival(time,)

        schedule inpatient_arrive at + exponential(lambda_inpatient)

        p = new patient
        p.type = "inpatient"
        p.patient_id = next_id()
        p.request_time = t
        p.arrival_time = t
        p.outside_room = false
        p.request_during_oh = is_office_hours(t)?
        p.scanned_after_1600 = false

        k = find_free_scanner()

        if k != -1:
            dispatch_to_scanner(k, p, t)
            if warmup_done and p.request_during_oh:
                pm5_flags.append(0)
        else:
            enqueue_patient(p, t)
        if time >9 and time < 15:

            lam_t = sin()time

        lam_t = lam_i


    def op_arrival(self):
        op_request_arrive(t):

        schedule op_request_arrive at t+exponential(lambda_op_request)

        p = new patient
        p.type = "outpatient"
        p.patient_id = next_id()
        p.request_time = t
        p.request_day = day_number(t)
        p.arrival_time = none
        p.outside_room = false

        earliest_day = p.request_day + 1

        slot = find_earliest_slot(earliest_day)

        if slot != none:
            (day, hour, slot_idx) = slot
            appointment_t = book_slot(day, hour, slot_idx, p)

            schedule op_appointment(p) appointment_t
        else:
            waiting_list.append(p)



K = 3
len(queue_emergency)+len(queue_normal) >K:

count inpatients in the office hour
count_ioh=0