from utils.config import u

class TrafficLight:
    def __init__(self, name):
        self.name = name
        self.state = 'RED'
        self.time_in_state = 0
        self.requested = False
        self.min_green_remaining = 0
        self.next_state = None

    def set_state(self, new_state, next_state=None):
        prev = self.state
        self.state = new_state
        self.next_state = next_state
        self.time_in_state = 0

        if new_state == 'GREEN':
            self.min_green_remaining = u
            self.next_state = None
        elif new_state == 'YELLOW':
            self.next_state = next_state or ('RED' if prev == 'GREEN' else 'GREEN')
            self.min_green_remaining = 0
        else:
            self.min_green_remaining = 0
            self.next_state = None

    def tick(self):
        self.time_in_state += 1
        if self.state == 'GREEN' and self.min_green_remaining > 0:
            self.min_green_remaining -= 1
