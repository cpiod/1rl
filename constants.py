import tcod
import enum

red = tcod.Color(220,50,47)
magenta = tcod.Color(211,54,130)
violet = tcod.Color(108,113,196)
blue = tcod.Color(38,139,210)
cyan = tcod.Color(42,161,152)
green = tcod.Color(133,153,0)
orange = tcod.Color(203,75,22)
yellow = tcod.Color(181,137,0)
base03 = tcod.Color(0,43,54)
base02 = tcod.Color(7,54,66)
base01 = tcod.Color(88,110,117)
base00 = tcod.Color(101,123,131)
base0 = tcod.Color(131,148,150)
base1 = tcod.Color(147,161,161)
base2 = tcod.Color(238,232,213)
base3 = tcod.Color(253,246,227)

door_color = tcod.Color(203,75,22)
tcod.color_scale_HSV(door_color, 0.7, 1)

desat_magenta = tcod.Color(211,54,130)
tcod.color_scale_HSV(desat_magenta, 0.7, 1)
desat_violet = tcod.Color(108,113,196)
tcod.color_scale_HSV(desat_violet, 0.7, 1)
desat_blue = tcod.Color(38,139,210)
tcod.color_scale_HSV(desat_blue, 0.7, 1)
desat_green = tcod.Color(133,153,0)
tcod.color_scale_HSV(desat_green, 0.7, 1)
desat_yellow = tcod.Color(181,137,0)
tcod.color_scale_HSV(desat_yellow, 0.7, 1)

stability_threshold = 0.7
inventory_max_size = 5

time_descend = 60
time_equip = 60*3
time_equip_weapon = 20
time_move = 60
spawn_interval = 60*3
confusion_duration = 60*20
malus_max = 15*60
paradox_list = ["\"Illusions are not real, yet it's real that illusion itself exists.\"", "\"I know one thing: that I know nothing.\"", "\"Can the Wizard of Yendor create a rock too heavy for itself to lift?\"", "\"What happens if Pinocchio says \"My nose will grow now\"?\"", "\"I am lying.\""]

class FeatureSlot(enum.Enum):
    m = {"name": "monsters", "color": magenta, "desat_color": desat_magenta, "bug_class": "MonsterBug"}
    i = {"name": "mapgen", "color": violet, "desat_color": desat_violet, "bug_class": "MapGenBug"}
    p = {"name": "RNG", "color": blue, "desat_color": desat_blue, "bug_class": "RNGBug"}
    c = {"name": "animation", "color": yellow, "desat_color": desat_yellow, "bug_class": "AnimationBug"}
    l = {"name": "loot", "color": green, "desat_color": desat_green, "bug_class": "LootBug"}

class WeaponSlot(enum.Enum):
    fast = {"name": "printf()", "success_rate_base": 0.5, "duration_base": int(120*5/7.5), "instable": False, "key": "1"}
    slow = {"name": "profiler", "success_rate_base": 0.75, "duration_base": 120, "instable": False, "key": "2"}
    hack = {"name": "hack", "success_rate_base": 1, "duration_base": 30, "instable": True, "key": "3"}

class FeatureEgo(enum.Enum):
    c1 = {"name": "narcoleptic", "char": "t"}
    c2 = {"name": "occult", "char": "t"}
    c3 = {"name": "psychic", "char": "t"}

    b1 = {"name": "magic-based", "char": "b"}
    b2 = {"name": "reputation-based", "char": "b"}
    b3 = {"name": "pun-based", "char": "b"}

    p1 = {"name": "recursive", "char": "p"}
    p2 = {"name": "meta", "char": "p"}
    p3 = {"name": "self-referenced", "char": "p"}

    m1 = {"name": "Sisyphean", "char": "m"}
    m2 = {"name": "Lovecraftian", "char": "m"}
    m3 = {"name": "Elvish", "char": "m"}

class WeaponEgo(enum.Enum):
    c = {"name": "telepathic", "fego": [FeatureEgo.c1, FeatureEgo.c2, FeatureEgo.c3], "char": "t", "w_class": "ConsciousWeapon"}
    b = {"name": "basic", "fego": [FeatureEgo.b1, FeatureEgo.b2, FeatureEgo.b3], "char": "b", "w_class": "BasicWeapon"}
    p = {"name": "paradoxical", "fego": [FeatureEgo.p1, FeatureEgo.p2, FeatureEgo.p3], "char": "p", "w_class": "ParadoxicalWeapon"}
    m = {"name": "mythical", "fego": [FeatureEgo.m1, FeatureEgo.m2, FeatureEgo.m3], "char": "m", "w_class": "MythicalWeapon"}

class TurnType(enum.Enum):
    ENNEMY = 0
    PLAYER = 1
    SPAWN = 2

class TileType(enum.Enum):
    WALL = {"name": "", "collision": True, "transparent": False, "char": "#", "color": base2}
    FLOOR = {"name": "", "collision": False, "transparent": True, "char": ".", "color": base2}
    STAIRS = {"name": "stairs", "collision": False, "transparent": True, "char": ">", "color": door_color}
    DOOR = {"name": "door", "collision": False, "transparent": False, "char": "+", "color": door_color}

class RenderOrder(enum.Enum):
    TILE = 1
    ITEM = 2
    ACTOR = 3

class MenuState(enum.Enum):
    STANDARD = 1
    DROP = 2
    EQUIP = 3
    POPUP = 4

resistance_mul = [1, 0.9, 0.8, 0.7, 0.6, 0.5]
monster_success_rate = [0.7, 0.75, 0.8]
n_bugs_max = [[10,0,0],[15,3,0],[20,5,1]]


help_adjust = 30
help_strings = ["1RL","","You have 7 days to complete your game.","","","Commands","","g        pick-up".ljust(help_adjust, ' '),"d        drop".ljust(help_adjust, ' '),"w        equip".ljust(help_adjust, ' '),"123      change active weapon".ljust(help_adjust, ' '),"ENTER    use stairs".ljust(help_adjust, ' ')]
