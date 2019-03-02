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

class Turn():
    def __init__(self, date, ttype, entity):
        self.date = date
        self.ttype = ttype
        self.entity = entity

    def __lt__(self, other):
        return self.date < other.date

