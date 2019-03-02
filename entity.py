import tcod
import constants as const

class Entity:
    """
    A generic entity
    """

    def __init__(self, x, y, char, color, name, collision, transparent, is_seen=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.collision = collision
        self.transparent = transparent
        self.is_seen = is_seen

class Tile(Entity):
    """
    A floor, a door or a wall
    """

    def __init__(self, x, y, ftype=const.TileType.WALL, is_seen=False):
        super().__init__(x, y, ftype.value.get("char"), const.base2, ftype.value.get("name"), ftype.value.get("collision"), ftype.value.get("transparent"), is_seen) # TODO color
        self.ftype = ftype

class Weapon(Entity):
    """
    A debugger
    """

    def __init__(self, wslot, success_rate, duration, wego, level):
        super().__init__(None, None, wego.value.get("char"), const.base2, wego.value.get("name")+" "+wslot.value.get("name"), collision=False, transparent=True)
        self.wego = wego
        self.level = level
        # TODO : use wslot
        self.success_rate = success_rate
        self.duration = duration
        self.wslot = wslot

class Feature(Entity):

    def __init__(self, fslot, fego, level, stability):
        super().__init__(None, None, fego.value.get("char"), fslot.value.get("color"), fego.value.get("name")+" "+fslot.value.get("name"), collision=False, transparent=True)
        self.flot = fslot
        self.fego = fego
        self.level = level
        self.stability = stability

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, '@', const.base3, "You", collision=True, transparent=True, is_seen=True) # TODO color

class Monster(Entity):
    def __init__(self, x, y, fslot, hp, speed, fcreator):
        super().__init__(x, y, str(hp), fslot.value.get("color"), fslot+" bug", collision=True, transparent=True)
        self.fslot = fslot
        self.hp = hp
        self.speed = speed
        self.fcreator = fcreator
