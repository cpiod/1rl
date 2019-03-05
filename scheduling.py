import heapq

class Scheduling():
    def __init__(self):
        self.turns = []
        self.current_date = 0

    def add_turn(self, delta_time, ttype, entity):
        self.add_turn_absolute(Turn(self.current_date + delta_time, ttype, entity))

    def add_turn_absolute(self, turn):
        heapq.heappush(self.turns, turn)

    def get_turn(self):
        out = heapq.heappop(self.turns)
        self.current_date = out.date
        return out

    def is_boss_ready(self):
        remaining = 7*24*60*60 - self.current_date
        remaining_d = int(remaining / (24*60*60))
        # return True # TODO
        return remaining_d <= 2

    def get_remaining(self):
        remaining = 7*24*60*60 - self.current_date
        remaining_d = int(remaining / (24*60*60))
        remaining_h = int((remaining / (60*60))) % 24
        remaining_m = int((remaining / (60))) % 60
        remaining_s = remaining % 60
        return (remaining_d, remaining_h, remaining_m, remaining_s)

class Turn():
    def __init__(self, date, ttype, entity):
        self.date = date
        self.ttype = ttype
        self.entity = entity

    def __lt__(self, other):
        return self.date < other.date

