import tcod
import constants as const

class Entity:
    """
    A generic entity
    """

    def __init__(self, x, y, char, color, name, collision, transparent, render_order, is_seen=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.visible_color = color # color when visible
        self.hidden_color = const.base01 # color when hidden
        self.name = name
        self.collision = collision
        self.transparent = transparent
        self.is_seen = is_seen
        self.render_order = render_order

class Tile(Entity):
    """
    A floor, a door or a wall
    """

    def __init__(self, x, y, ftype=const.TileType.WALL):
        super().__init__(x, y, ftype.value.get("char"), ftype.value.get("color"), ftype.value.get("name"), ftype.value.get("collision"), ftype.value.get("transparent"), const.RenderOrder.TILE)
        self.ftype = ftype

class Weapon(Entity):
    """
    A debugger
    """

    def __init__(self, wslot, success_rate, duration, wego, level):
        super().__init__(None, None, wego.value.get("char"), const.base2, wego.value.get("name")+" "+wslot.value.get("name"), False, True, const.RenderOrder.ITEM)
        self.wego = wego
        self.level = level
        # TODO : use wslot
        self.success_rate = success_rate
        self.duration = duration
        self.wslot = wslot

class Feature(Entity):

    def __init__(self, fslot, fego, level, stability):
        super().__init__(None, None, fego.value.get("char"), fslot.value.get("color"), fego.value.get("name")+" "+fslot.value.get("name"), False, True, const.RenderOrder.ITEM)
        self.flot = fslot
        self.fego = fego
        self.level = level
        self.stability = stability

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, '@', const.base3, "You", True, True, const.RenderOrder.ACTOR, is_seen=True)

class Monster(Entity):
    def __init__(self, x, y, fslot, hp, speed, fcreator):
        super().__init__(x, y, str(hp), fslot.value.get("color"), fslot+" bug", True, True, const.RenderOrder.ACTOR)
        self.fslot = fslot
        self.hp = hp
        self.speed = speed
        self.fcreator = fcreator
