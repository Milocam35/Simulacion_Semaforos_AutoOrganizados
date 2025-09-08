from collections import deque
from utils.config import IN_LENGTH, OUT_LENGTH, r, d, e, SPAWN_PROB
import random

class Road:
    def __init__(self, name):
        self.name = name
        self.approach = deque([0]*IN_LENGTH)
        self.exit_lane = deque([0]*OUT_LENGTH)

    def spawn_vehicle(self, prob=SPAWN_PROB):
        if random.random() < prob:
            if self.approach[0] == 0:
                self.approach[0] = 1

    def count_behind_red(self, distance=d):
        start = max(0, IN_LENGTH - distance)
        return sum(self.approach[i] for i in range(start, IN_LENGTH))

    def vehicle_at_r(self):
        return self.approach[IN_LENGTH-r] == 1 if IN_LENGTH-r >= 0 else False

    def vehicles_in_intersection_zone(self):
        start = max(0, IN_LENGTH - r)
        return sum(self.approach[i] for i in range(start, IN_LENGTH))

    def vehicles_stopped_beyond_e(self):
        return sum(self.exit_lane[i] for i in range(min(e, len(self.exit_lane))))

    def move_vehicles_forward(self, can_enter_intersection):
        crossed = 0

        if self.exit_lane[-1] == 1:
            self.exit_lane[-1] = 0

        for i in range(OUT_LENGTH-2, -1, -1):
            if self.exit_lane[i] == 1:
                self.exit_lane[i+1] = 1
                self.exit_lane[i] = 0

        if self.approach[IN_LENGTH-1] == 1 and can_enter_intersection:
            if self.exit_lane[0] == 0:
                self.exit_lane[0] = 1
                self.approach[IN_LENGTH-1] = 0
                crossed = 1

        for i in range(IN_LENGTH-2, -1, -1):
            if self.approach[i] == 1 and self.approach[i+1] == 0:
                self.approach[i+1] = 1
                self.approach[i] = 0

        return crossed
