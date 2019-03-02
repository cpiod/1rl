import heapq

class Scheduling():
    def __init__(self):
        self.turns = []
        self.current_date = 0

    def add_turn(self, turn):
        heapq.heappush(self.turns, turn)

    def get_turn(self):
        return heapq.heappop(self.turns)

class Turn():
    def __init__(self, date, ttype, entity):
        self.date = date
        self.ttype = ttype
        self.entity = entity

    def __lt__(self, other):
        return self.date < other.date

