from random import choice

class FireArea:
    def __init__(self, fire_area):
        self.area = fire_area
        self.inactive_time, self.warning_time, self.active_time = self.phase_time_duration()
        self.phase = "inactive"
        self.phase_sum = sum([self.inactive_time, self.warning_time, self.active_time])

    def phase_time_duration(self):
        inactive = choice([4, 5, 6, 7])
        warning = choice([1, 1.5, 2, 2.5, 3])
        active = choice([2, 2.5, 3, 3.5, 4])
        return inactive, warning, active
    
    def update(self, game_time):
        self.phase_time = game_time % self.phase_sum

        if self.phase_time < self.inactive_time:
            self.phase = "inactive"
        elif self.phase_time < self.inactive_time + self.warning_time:
            self.phase = "warning"
        else:
            self.phase = "burning"