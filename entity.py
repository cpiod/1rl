import tcod

class Entity:
    """
    A generic entity
    """

    def __init__(self, x, y, char, color, name, collision, is_seen=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.collision = collision
        self.is_seen = is_seen

class Floor(Entity):
    """
    A floor or a wall
    """

    def __init__(self, x, y, ftype, is_seen=False):
        super().__init__(x, y, ftype.char, None, ftype.name, ftype.collision, is_seen) # TODO color
        self.ftype = ftype

class Weapon(Entity):
    """
    A debugger
    """

    def __init__(self, wslot, success_rate, duration, wego, level):
        super().__init__(None, None, wego.char, wego.fslot.color, wego.name, collision=False)
        self.wego = wego
        self.level = level
        self.success_rate = success_rate
        self.duration = duration
        self.wslot = wslot

class Feature(Entity):

    def __init__(self, fslot, fego, level, stability):
        super().__init__(None, None, fego.char, fslot.color, fego.name, collision=False)
        self.flot = fslot
        self.fego = fego
        self.level = level
        self.stability = stability

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, '@', None, "You", collision=True, is_seen=True) # TODO color

class Monster(Entity):
    def __init__(self, x, y, fslot, hp, speed, fcreator):
        super().__init__(x, y, str(hp), fslot.color, fslot+" bug", collision=True)
        self.fslot = fslot
        self.hp = hp
        self.speed = speed
        self.fcreator = fcreator
