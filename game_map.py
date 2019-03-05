import tcod
import random
import copy
import constants as const
import entity
import render
import numpy as np
import random_loot as rloot

class Room:
    def __init__(self, x, y, w, h):
        self.x = x # upper left point
        self.y = y # upper left point
        self.w = w
        self.h = h
        self.n_loot = 0
        self.neighbors = []

class GameMap:
    def __init__(self, width, height, con, show_map=False):
        self.width = width
        self.con = con
        self.height = height
        self.dlevel = 0
        self.tcod_empty_map = tcod.map.Map(self.width, self.height)
        self.show_map = show_map
        for x in range(self.width):
            for y in range(self.height):
                self.tcod_empty_map.transparent[y,x] = True
                self.tcod_empty_map.walkable[y,x] = True
        # ogrid = [np.arange(width, dtype=np.float32),
        # np.arange(height, dtype=np.float32)]

        # noise = tcod.noise.Noise(
        #     dimensions=2,
        #     algorithm=tcod.NOISE_PERLIN,
        #     implementation=tcod.noise.TURBULENCE,
        #     hurst=0.9,
        #     lacunarity=1.6,
        #     octaves=5
        #     )
        # min_lum = 0.5
        # max_lum = 1
        # sample = noise.sample_ogrid(ogrid)*(max_lum-min_lum) + min_lum

    def add_loot(self, turns, player, entities):
        n_loot = 15 + sum([random.randint(1,4) for i in range(4)])
        while n_loot > 0:
            arity = random.choice([1,1,1,2,2,3,4,5])
            rlist = [r for r in self.rooms_with_arity(arity) if r.n_loot < 2] # 2 items per room max
            if rlist:
                room = random.choice(rlist)
                (x,y) = self.random_cell_in_room(room)
                if not self.tiles[x][y].item:
                    room.n_loot += 1
                    self.tiles[x][y].put_item(rloot.get_random_loot(turns, player), entities)
                    n_loot -= 1

    def rooms_with_arity(self, max_arity):
        return [r for r in self.room_list if len(r.neighbors) <= max_arity]

    def make_boss_map(self, turns, entities, player):
        self.tiles = [[entity.Tile(x,y) for y in range(self.height)] for x in range(self.width)]
        self.tcod_map = tcod.map.Map(self.width, self.height)
        center_x = self.width / 2
        center_y = self.height / 2
        a = 20
        b = 10
        self.room_list = [Room(int(center_x - a), int(center_y - b), 2*a, 2*b)]
        for x in range(self.width):
            for y in range(self.height):
                if ((x - center_x)/a)**2 + ((y - center_y)/b)**2 <= 1:
                    self.set_unblocked(x, y)
        (player.x, player.y) = (int(center_x / 2), int(center_y))
        boss = entity.Boss(int(center_x * 1.5), int(center_y))
        entities.append(boss)
        turns.add_turn(boss.speed, const.TurnType.ENNEMY, boss)
        self.recompute_fov(player.x, player.y)
        return boss

    def make_map_bsp(self, turns, entities, player):
        self.tiles = [[entity.Tile(x,y) for y in range(self.height)] for x in range(self.width)]
        self.room_list = None
        self.tcod_map = tcod.map.Map(self.width, self.height)
        self.dlevel += 1
        map_width = self.width
        map_height = self.height
        if self.show_map:
            for x in range(map_width):
                for y in range(map_height):
                    self.tiles[x][y].is_seen = True
        # we garantee a wall on the north and the west
        # this is necessary due to the generation the room
        bsp = tcod.bsp.BSP(1,1,map_width-1, map_height-1)
        bsp.split_recursive(6,6,6,1,1)
        self.room_list = self.recursive_make_rooms(bsp)

        # After the BSP generation, the dungeon is a tree
        # Create some loops
        rlist = self.rooms_with_arity(2)
        for i in range(6):
            for j in range(10):
                c = random.choice(range(len(rlist)))
                best = self.closest_rooms([rlist[c]], self.room_list)
                if best:
                    astar = tcod.path.AStar(self.tcod_map)
                    score_tuple = None
                    best_tuple = []
                    for tuple_param in best:
                        (x1, y1, x2, y2, _, _) = tuple_param
                        path = astar.get_path(x1, y1, x2, y2)
                        tmp_score = int(len(path)/3)
                        if not score_tuple or tmp_score > score_tuple:
                            score_tuple = tmp_score
                            best_tuple = [tuple_param]
                        elif tmp_score == score_tuple:
                            best_tuple.append(tuple_param)
                    self.connect_rooms(random.choice(best_tuple))
                    del rlist[c]
                    break

        # Initialization
        (player.x, player.y) = self.random_cell()
        (x, y) = self.random_cell()
        self.place_stairs(x,y)
        if turns.is_boss_ready():
            (x, y) = self.random_cell()
            self.place_boss_stairs(x,y)
        # self.place_boss_stairs(player.x,player.y) # TODO
        self.add_loot(turns, player, entities)
        self.recompute_fov(player.x, player.y)

    def recompute_fov(self, x, y, light_walls=True, radius=0):
        self.tcod_map.compute_fov(x, y, algorithm=2, radius=radius, light_walls=light_walls)

    def is_visible(self, x, y):
        return self.tcod_map.fov[y,x]

    def spawn_boss(self, entities, fslot, level):
        for i in range(50):
            (x,y) = self.random_cell()
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if level > 1:
                    class_name = fslot.value.get("bug_class")
                    the_class = getattr(entity, class_name)
                    monster = the_class(x, y, level, None, fslot)
                else:
                    monster = entity.Monster(x, y, level, None, fslot)
                entities.append(monster)
                return monster
        return None

    def spawn(self, entities, feature):
        # We try at most 50 times to spawn it
        for i in range(50):
            (x,y) = self.random_cell()
            if not self.is_visible(x,y) and not any([entity for entity in entities if entity.x == x and entity.y == y]):
                level = random.randint(1, feature.level)
                if feature.n_bugs[level - 1] < feature.n_bugs_max[level - 1]:
                    if level > 1:
                        class_name = feature.fslot.value.get("bug_class")
                        the_class = getattr(entity, class_name)
                        monster = the_class(x, y, level, feature)
                    else:
                        monster = entity.Monster(x, y, level, feature)
                    entities.append(monster)
                    # print("Spawn from "+feature.name+": "+str(feature.n_bugs))
                    return monster
        return None

    def iterator_perimeter_room(self, r):
        for x in range(r.x, r.x + r.w):
            yield (x, r.y)
            yield (x, r.y + r.h - 1)
        # y has a shorter range because the corners are already yielded
        for y in range(r.y + 1, r.y + r.h - 1):
            yield (r.x, y)
            yield (r.x + r.w - 1, y)

    def closest_rooms(self, l1, l2):
        best = []
        score_best = None
        for r1 in l1:
            for r2 in l2:
                if r1 != r2 and r1 not in r2.neighbors:
                    for (x1, y1) in self.iterator_perimeter_room(r1):
                        for (x2, y2) in self.iterator_perimeter_room(r2):
                            dx = abs(x1-x2)
                            dy = abs(y1-y2)
                            # This is not a hack. It is… hand-crafted mapgen
#                            if dx >= 4 and dy >= 4:
#                                score = max(abs(x1-x2),abs(y1-y2)) # Chebyshev distance
#                            else:
                            score = abs(x1-x2) + abs(y1-y2) # Manhattan distance
                            if score_best == None or score < score_best:
                                score_best = score
                                best = [(x1,y1,x2,y2,r1,r2)]
                            elif score == score_best:
                                best.append((x1,y1,x2,y2,r1,r2))
        return best


    def random_cell(self):
        return self.random_cell_in_room(random.choice(self.room_list))

    def random_cell_in_room(self, r):
        while True:
            x = random.randrange(r.x, r.x + r.w)
            y = random.randrange(r.y, r.y + r.h)
            if self.is_floor(x,y):
                return (x,y)

    def recursive_make_rooms(self, bsp):
        if not bsp.children:
            w = random.randrange(max(3,int(bsp.w/3)),bsp.w-2)
            h = random.randrange(max(3,int(bsp.h/3)),bsp.h-2)
            # w = 1
            # h = 1
            # w = bsp.w - 1
            # h = bsp.h - 1
            upper_left_x = random.randrange(bsp.x, bsp.x + bsp.w - w)
            upper_left_y = random.randrange(bsp.y, bsp.y + bsp.h - h)

            for x in range(0,w):
                for y in range(0,h):
                    self.set_unblocked(upper_left_x + x, upper_left_y + y)

            # Sometimes, add a central pillar
            if (w % 2) == 1 and (h % 2) == 1:
                if random.randrange(0,10) == 0:
                    center_x = upper_left_x + int((w-1)/2)
                    center_y = upper_left_y + int((h-1)/2)
                    self.set_blocked(center_x, center_y)

            # And rarely a big one (rare because big rooms aren't common)
            if (w % 2) == 0 and (h % 2) == 0 and w >= 10 and h >= 10 and random.randrange(0,2) == 0:
                center_x = upper_left_x + int(w/2) - 1
                center_y = upper_left_y + int(h/2) - 1
                for x in range(0,2):
                    for y in range(0,2):
                        self.set_blocked(center_x + x, center_y + y)

            return [Room(upper_left_x, upper_left_y, w, h)]

        else:
            l1 = self.recursive_make_rooms(bsp.children[0])
            l2 = self.recursive_make_rooms(bsp.children[1])
            # it is garanteed to connect
            self.connect_rooms(random.choice(self.closest_rooms(l1,l2)))
            return l1+l2

    def connect_rooms(self, tuple_param, force=False):
        (x1, y1, x2, y2, r1, r2) = tuple_param
        r1.neighbors.append(r2)
        r2.neighbors.append(r1)
        door_chance = 4
        if x1 == x2:
            if y1 > y2:
                y1 -= 1
                y2 += 1
            else:
                y1 += 1
                y2 -= 1
            self.create_v_tunnel(y1, y2, x1)
            if random.randint(0,door_chance) == 0:
                self.place_door(x1, y1)
            elif random.randint(0,door_chance) == 0:
                self.place_door(x2, y2)
        elif y1 == y2:
            if x1 > x2:
                x1 -= 1
                x2 += 1
            else:
                x1 += 1
                x2 -= 1
            self.create_h_tunnel(x1, x2, y1)
            if random.randint(0,door_chance) == 0:
                self.place_door(x1, y1)
            elif random.randint(0,door_chance) == 0:
                self.place_door(x2, y2)
#        elif abs(x1-x2) < 3 or abs(y1-y2) < 3:
        else:
            if random.randint(0, 1) == 1:
                if x1 > x2:
                    x1 -= 1
                else:
                    x1 += 1
                if y1 > y2:
                    y2 += 1
                    y3 = y1 - 1
                else:
                    y2 -= 1
                    y3 = y1 + 1

                self.create_h_tunnel(x1, x2, y1)
                self.create_v_tunnel(y3, y2, x2)
                if random.randint(0,door_chance) == 0 and abs(x1-x2) > 1:
                    self.place_door(x1, y1)
                elif random.randint(0,door_chance) == 0 and abs(y1-y2) > 1:
                    self.place_door(x2, y2)

            else:
                if x1 > x2:
                    x2 += 1
                    x3 = x1 - 1
                else:
                    x2 -= 1
                    x3 = x1 + 1
                if y1 > y2:
                    y1 -= 1
                else:
                    y1 += 1

                self.create_v_tunnel(y1, y2, x1)
                self.create_h_tunnel(x3, x2, y2)
                if random.randint(0,door_chance) == 0 and abs(y1-y2) > 1:
                    self.place_door(x1, y1)
                elif random.randint(0,door_chance) == 0 and abs(x1-x2) > 1:
                    self.place_door(x2, y2)

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
#            tcod.console_set_char_foreground(self.con, x, y, c)
            self.set_unblocked(x,y)

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
#            tcod.console_set_char_foreground(self.con, x, y, c)
            self.set_unblocked(x,y)

    def get_copy_map(self):
        return copy.deepcopy(self.tcod_map)

    def get_copy_empty_map(self):
        return copy.deepcopy(self.tcod_empty_map)

    def set_tile_type(self, x, y, ttype):
        self.tiles[x][y] = entity.Tile(x, y, ttype)
        if self.show_map:
            self.tiles[x][y].is_seen = True
        self.tcod_map.transparent[y,x] = ttype.value.get("transparent")
        self.tcod_map.walkable[y,x] = not ttype.value.get("collision")


    def is_over_map(self, x, y):
        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def set_blocked(self, x, y):
        self.set_tile_type(x, y, const.TileType.WALL)

    def set_unblocked(self, x, y):
        self.set_tile_type(x, y, const.TileType.FLOOR)

    def place_door(self, x, y):
        self.set_tile_type(x, y, const.TileType.DOOR)

    def place_stairs(self, x, y):
        self.set_tile_type(x, y, const.TileType.STAIRS)

    def place_boss_stairs(self, x, y):
        self.set_tile_type(x, y, const.TileType.BOSS_STAIRS)

    def is_floor(self, x, y):
        return self.tiles[x][y].ftype == const.TileType.FLOOR

    def is_door(self, x, y):
        return self.tiles[x][y].ftype == const.TileType.DOOR

    def is_stairs(self, x, y):
        return self.tiles[x][y].ftype == const.TileType.STAIRS

    def is_boss_stairs(self, x, y):
        return self.tiles[x][y].ftype == const.TileType.BOSS_STAIRS

    def is_blocked(self, x, y):
        return not self.tcod_map.walkable[y,x]

    def drop_item_on_floor(self, player, entities, item, drop_key):
        if not self.tiles[player.x][player.y].item:
            player.remove_from_inventory(item, drop_key)
            return self.tiles[player.x][player.y].put_item(item, entities)

    def get_item_on_floor(self, player, entities):
        if self.tiles[player.x][player.y].item:
            item = self.tiles[player.x][player.y].take_item(entities)
            player.add_to_inventory(item)
            return item

    def description_item_on_floor(self, player):
        if self.tiles[player.x][player.y].item:
            return self.tiles[player.x][player.y].item.name
        return None

    def is_there_item_on_floor(self, player):
        return self.tiles[player.x][player.y].item != None
