import tcod
import enum
import random

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
desat_orange = door_color

desat_red = tcod.Color(220,50,47)
tcod.color_scale_HSV(desat_red, 0.7, 1)
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
boss_stairs_color = desat_green

light_green = tcod.Color(133,153,0)*1.5
light_blue = tcod.Color(38,139,210)*1.5


stability_threshold = 0.7
inventory_max_size = 5
mul = 2
bug_hp = [2, 5, 9]
bonus_idem = [0, 0, 1, 2, 2, 3]
bug_atk = [70, 80, 100]
bug_speed_atk = [180*mul, 120*mul, 60*mul]
bug_speed_mov = [60*mul, 50*mul, 40*mul]
boss_level_invok = [1, 2, 3]
time_equip = 20*mul
time_move = 60*mul
spawn_interval = 60*mul
confusion_duration = 60*10*mul
malus_max = 30*60*mul
max_stab = [100,300,600]
stab_reward = [2,4,6]
resistance_mul = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
monster_success_rate = [0.8, 0.85, 0.9]
n_bugs_max = [[5,0,0],[2,5,1]]


paradox_list = ["\"Illusions are not real, yet it's real that illusion itself exists.\"", "\"I know one thing: that I know nothing.\"", "\"Can the Wizard of Yendor create a rock too heavy for itself to lift?\"", "\"What happens if Pinocchio says \"My nose will grow now\"?\"", "\"I am lying.\""]

class FeatureSlot(enum.Enum):
    m = {"name": "monsters", "color": magenta, "desat_color": desat_magenta, "bug_class": "MonsterBug"}
    i = {"name": "mapgen", "color": violet, "desat_color": desat_violet, "bug_class": "MapGenBug"}
    p = {"name": "RNG", "color": blue, "desat_color": desat_blue, "bug_class": "RNGBug"}
    c = {"name": "animation", "color": yellow, "desat_color": desat_yellow, "bug_class": "AnimationBug"}
    l = {"name": "loot", "color": green, "desat_color": desat_green, "bug_class": "LootBug"}

class WeaponSlot(enum.Enum):
    fast = {"name": "printf()", "success_rate_base": 0.5, "duration_base": int(60*5/7.5*mul), "instable": False, "key": "1"}
    slow = {"name": "profiler", "success_rate_base": 0.75, "duration_base": 60*mul, "instable": False, "key": "2"}
    hack = {"name": "hack", "success_rate_base": 1, "duration_base": 10*mul, "instable": True, "key": "3"}

fego_prob_c = [1/4,1/4,1/2]
fego_prob_b = [1/4,1/4,1/2]
fego_prob_p = [1/4,1/4,1/2]
fego_prob_m = [1/4,1/4,1/2]
random.shuffle(fego_prob_c)
random.shuffle(fego_prob_b)
random.shuffle(fego_prob_p)
random.shuffle(fego_prob_m)
fego_prob = fego_prob_c + fego_prob_b + fego_prob_p + fego_prob_m

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
    c = {"name": "telepathic", "fego": [FeatureEgo.c1, FeatureEgo.c2, FeatureEgo.c3], "char": "t", "w_class": "ConsciousWeapon", "player_color": base3}
    b = {"name": "basic", "fego": [FeatureEgo.b1, FeatureEgo.b2, FeatureEgo.b3], "char": "b", "w_class": "BasicWeapon", "player_color": light_green}
    p = {"name": "paradoxical", "fego": [FeatureEgo.p1, FeatureEgo.p2, FeatureEgo.p3], "char": "p", "w_class": "ParadoxicalWeapon", "player_color": base3}
    m = {"name": "mythical", "fego": [FeatureEgo.m1, FeatureEgo.m2, FeatureEgo.m3], "char": "m", "w_class": "MythicalWeapon", "player_color": light_blue}

class TurnType(enum.Enum):
    ENNEMY = 0
    PLAYER = 1
    SPAWN = 2
    MSG = 3
    GAME_OVER = 4
    WIN = 5

class TileType(enum.Enum):
    WALL = {"name": "", "collision": True, "transparent": False, "char": "#", "color": base2}
    FLOOR = {"name": "", "collision": False, "transparent": True, "char": ".", "color": base2}
    STAIRS = {"name": "stairs", "collision": False, "transparent": True, "char": ">", "color": door_color}
    BOSS_STAIRS = {"name": "strange stairs", "collision": False, "transparent": True, "char": ">", "color": boss_stairs_color}
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

intro_strings = ["Welcome to 1RL","You have 7 days to create", "your first roguelike!","","Complete your game by choosing its features.","","Beware: unstable features generate bugs!","","Fight bugs with weapons.", "Get higher resistance from better features.", "", "Click on anything to get details.","Press ? to get command help."]
help_adjust = 16
help_adjust_name = 15
help_strings = ["Help",\
                "numpad/vi/arrows".ljust(help_adjust, ' ')+"move/attack".rjust(help_adjust_name, ' '),\
                "g".ljust(help_adjust_name, ' ')+"pick up".rjust(help_adjust, ' '),\
                "d".ljust(help_adjust_name, ' ')+"drop".rjust(help_adjust, ' '),\
                "w".ljust(help_adjust_name, ' ')+"equip".rjust(help_adjust, ' '),\
                "[123]".ljust(help_adjust_name, ' ')+"change weapon".rjust(help_adjust, ' '),\
                "ENTER".ljust(help_adjust_name, ' ')+"use stairs".rjust(help_adjust, ' '),\
                "",
                "f".ljust(help_adjust_name, ' ')+"fullscreen".rjust(help_adjust, ' '),\
                "hover".ljust(help_adjust_name, ' ')+"get name".rjust(help_adjust, ' '),\
                "click".ljust(help_adjust_name, ' ')+"describe".rjust(help_adjust, ' '),\
                "?".ljust(help_adjust_name, ' ')+"help".rjust(help_adjust, ' '),\
               "", "", "This is a GPLv3 game.","Feel free to contribute at https://github.com/PFGimenez/1rl"]
