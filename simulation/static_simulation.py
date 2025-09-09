from simulation.simulation import Simulation

class StaticSimulation(Simulation):
    def __init__(self, green_time=6, yellow_time=2, red_time=6):
        super().__init__()
        self.green_time = green_time
        self.yellow_time = yellow_time
        self.red_time = red_time
        self.cycle_time = green_time + yellow_time + red_time
        self.t = 0

        # Semáforo A inicia en rojo, B en rojo
        self.lightA.set_state('RED')
        self.lightB.set_state('RED')

    def apply_rules_and_transition(self):
        cycle_pos = self.t % self.cycle_time

        # Semáforo A: Verde → Amarillo → Rojo
        if cycle_pos < self.green_time:
            self.lightA.set_state('GREEN')
            self.lightB.set_state('RED')
        elif cycle_pos < self.green_time + self.yellow_time:
            self.lightA.set_state('YELLOW', next_state='RED')
            self.lightB.set_state('RED')
        else:
            self.lightA.set_state('RED')
            # B entra en su ciclo
            cycle_pos_B = (cycle_pos - (self.green_time + self.yellow_time)) % self.cycle_time
            if cycle_pos_B < self.green_time:
                self.lightB.set_state('GREEN')
            elif cycle_pos_B < self.green_time + self.yellow_time:
                self.lightB.set_state('YELLOW', next_state='RED')
            else:
                self.lightB.set_state('RED')
