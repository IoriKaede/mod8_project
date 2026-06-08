
import numpy as np
import math
import random

from core import Simulation, Event
from statistics import TimeWeightedStatistic, SampleStatistic, Counter, _t_critical
from distributions import Exponential, Erlang

def

class CT:
    def __init__(self):
        office_start = 8.0  # 08:00
        office_end = 16.0  # 16:00

        weekday_count = 5  # mon–fri
        day = time\24
        week = day\7


        queue_emergency = [] #with prioity
        queue_normal = []
        queue_scheduled = []#draw this  from index0 to normal

        slots_per_hour_morning = 4
        slots_per_hour_afternoon = 3
        waiting_room_capacity = 3

        lambda_emergency =
        lambda_inpatient =
        lambda_op_request =

        mu =  #service rate

        scanner_1 = 0  # index/ maybe not hard coded
        scanner_2 = 1
        num_scanners = 2

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