import random
from simulation.traffic_light import TrafficLight
from simulation.road import Road
from utils.config import n, YELLOW_TIME

class Simulation:
    def __init__(self):
        self.lightA = TrafficLight('A')
        self.lightB = TrafficLight('B')
        self.lightA.set_state('RED')
        self.lightB.set_state('RED')
        self.roadA = Road('A')
        self.roadB = Road('B')
        self.t = 0
        self.priority = None
        self.last_was = None
        self.log = []

    def evaluate_requests(self):
        cA = self.roadA.count_behind_red()
        cB = self.roadB.count_behind_red()
        self.lightA.requested = (cA >= n)
        self.lightB.requested = (cB >= n)
        return cA, cB

    def apply_rules_and_transition(self):
        A = self.lightA
        B = self.lightB
        cA, cB = self.evaluate_requests()

        congestA = self.roadA.vehicles_stopped_beyond_e() > 0
        congestB = self.roadB.vehicles_stopped_beyond_e() > 0
        if congestA and congestB:
            if A.state == 'GREEN':
                A.set_state('YELLOW')
            if B.state == 'GREEN':
                B.set_state('YELLOW')
            return

        if A.requested and B.requested:
            if A.state == 'RED' and B.state == 'RED':
                if self.last_was is None:
                    chosen = random.choice(['A','B'])
                else:
                    chosen = 'A' if self.last_was == 'B' else 'B'
                if chosen == 'A':
                    A.set_state('YELLOW')
                    B.set_state('RED')
                else:
                    B.set_state('YELLOW')
                    A.set_state('RED')
                self.priority = chosen
                return

        if A.state == 'GREEN' and cA == 0 and cB > 0:
            A.set_state('YELLOW')
            return
        if B.state == 'GREEN' and cB == 0 and cA > 0:
            B.set_state('YELLOW')
            return

        if A.requested and B.state == 'GREEN':
            if B.min_green_remaining > 0:
                return
            if self.roadB.vehicles_in_intersection_zone() > 0:
                return
            B.set_state('YELLOW')
            return

        if B.requested and A.state == 'GREEN':
            if A.min_green_remaining > 0:
                return
            if self.roadA.vehicles_in_intersection_zone() > 0:
                return
            A.set_state('YELLOW')
            return

        if A.state == 'RED' and A.requested and not (B.state in ('YELLOW','GREEN')):
            A.set_state('YELLOW')
            return
        if B.state == 'RED' and B.requested and not (A.state in ('YELLOW','GREEN')):
            B.set_state('YELLOW')
            return

        if A.state == 'YELLOW' and A.time_in_state >= YELLOW_TIME:
            target = A.next_state or 'RED'
            A.set_state(target)
            if target == 'GREEN':
                self.last_was = 'A'
            return
        if B.state == 'YELLOW' and B.time_in_state >= YELLOW_TIME:
            target = B.next_state or 'RED'
            B.set_state(target)
            if target == 'GREEN':
                self.last_was = 'B'
            return

        if A.state == 'RED' and B.state == 'RED':
            if cA > 0 and cB == 0:
                A.set_state('YELLOW')
                return
            if cB > 0 and cA == 0:
                B.set_state('YELLOW')
                return

    def step(self):
        self.t += 1

        self.roadA.spawn_vehicle()
        self.roadB.spawn_vehicle()

        self.apply_rules_and_transition()

        canA = (self.lightA.state == 'GREEN')
        canB = (self.lightB.state == 'GREEN')

        crossedA = self.roadA.move_vehicles_forward(canA)
        crossedB = self.roadB.move_vehicles_forward(canB)

        self.lightA.tick()
        self.lightB.tick()

        self.log.append((self.t, crossedA, crossedB))
