import heapq

class Scheduling():
    """
    The turn system!
    This is a priority queue that remember, for each entity, the next turn it will play
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.turns = []
        self.current_date = 0
        self.current_turn = None

    def add_turn(self, delta_time, ttype, entity):
        assert int(delta_time) == delta_time, delta_time
        self.add_turn_absolute(Turn(self.current_date + delta_time, ttype, entity))

    def add_turn_absolute(self, turn):
        heapq.heappush(self.turns, turn)

    def remove_turn(self, entity):
        size_before = len(self.turns)
        self.turns = [t for t in self.turns if t.entity != entity]
        assert len(self.turns) != size_before
        heapq.heapify(self.turns)

    def nb_turns(self, ttype):
        out = len([t for t in self.turns if t.ttype == ttype])
        # if self.current_turn and self.current_turn.ttype == ttype:
            # out += 1
        return out

    def get_turn(self):
        out = heapq.heappop(self.turns)
        self.current_turn = out
        self.current_date = out.date
        assert int(out.date) == out.date, out.date
        return out

    def get_remaining(self):
        remaining = 7*24*60*60 - self.current_date
        remaining_d = int(remaining / (24*60*60))
        remaining_h = int((remaining / (60*60))) % 24
        remaining_m = int((remaining / 60)) % 60
        remaining_s = int(remaining) % 60
        return (remaining_d, remaining_h, remaining_m, remaining_s)


class Turn():
    def __init__(self, date, ttype, entity):
        self.date = date
        self.ttype = ttype
        self.entity = entity

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.date)+" "+self.ttype.name+" "+str(self.entity)
