import tcod
import constants as const
import random

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

    def __str__(self):
        return self.name

    def move(self, dx, dy):
        self.x += dx
        self.y += dy



class Tile(Entity):
    """
    A floor, a door or a wall
    """

    def __init__(self, x, y, ftype=const.TileType.WALL):
        super().__init__(x, y, ftype.value.get("char"), ftype.value.get("color"), ftype.value.get("name"), ftype.value.get("collision"), ftype.value.get("transparent"), const.RenderOrder.TILE)
        self.ftype = ftype
        self.item = None

    def put_item(self, item, entities):
        assert self.item == None
        assert item not in entities
        self.item = item
        item.x = self.x
        item.y = self.y
        entities.append(item)

    def take_item(self, entities):
        assert self.item != None
        assert self.item in entities
        item = self.item
        item.x = None
        item.y = None
        entities.remove(item)
        self.item = None
        return item

class Weapon(Entity):
    """
    A debugger
    """
    def __init__(self, wslot, wego, level):
        super().__init__(None, None, wego.value.get("char"), const.base3, wego.value.get("name")+" "+wslot.value.get("name"), False, True, const.RenderOrder.ITEM)
        self.wego = wego
        self.level = level
        self.success_rate = int(100*(wslot.value.get("success_rate_base")+level*0.05))/100
        self.duration = wslot.value.get("duration_base")
        self.wslot = wslot
        self.is_in_inventory = False
        self.equiped = False
        self.fslot_effective = []

    def update_effective(self, fequiped):
        self.fslot_effective = [fslot for fslot in const.FeatureSlot if fequiped.get(fslot) and fequiped.get(fslot).fego in self.wego.value.get("fego")]

    def stat_string(self):
        string = str(round(self.success_rate * 100))+"% "+str(self.duration)+"mn"
        if self.wslot.value.get("instable"):
            string = "Stab- "+string
        return string

    def attack(self, target, msglog):
        dmg = 0
        if random.random() < self.success_rate:
            # succesfull attack
            effective = target.fslot in self.fslot_effective
            if effective:
                msglog.add_log("Your "+self.name+" is super effective on the "+target.name+"!")
                dmg = 2*self.level
            else:
                dmg = self.level
        else:
            msglog.add_log("You miss the "+target.name)
        return dmg

class Feature(Entity):
    """
    A feature
    """
    def __init__(self, fslot, fego, level):
        super().__init__(None, None, fego.value.get("char"), fslot.value.get("desat_color"), fego.value.get("name")+" "+fslot.value.get("name"), False, True, const.RenderOrder.ITEM)
        self.n_bugs = 0
        self.n_bugs_max = 10
        self.max_stability = 10 * (level*level)
        self.stability = int(self.max_stability / 10)
        self.fslot = fslot
        self.fego = fego
        self.is_in_inventory = False
        self.equiped = False
        self.level = level

    def destabilize(self, level):
        self.stability -= level
        if self.stability < 0:
            self.stability = 0

    def stabilize(self, level):
        if self.stability == self.max_stability:
            return False
        self.stability += level
        if self.stability > self.max_stability:
            self.stability = self.max_stability
        return True

    def is_stable(self):
        return (self.stability / self.max_stability) >= const.stability_threshold

class Player(Entity):
    """
    The player
    """
    def __init__(self, x, y):
        super().__init__(x, y, '@', const.base3, "You", True, True, const.RenderOrder.ACTOR, is_seen=True)
        self.inventory = {}

        letter_index = ord('a')
        for i in range(const.inventory_max_size):
            self.inventory[chr(letter_index+i)] = None

        self.wequiped = {}
        self.fequiped = {}
        self.resistances = {}
        self.active_weapon = None
        for fslot in const.FeatureSlot:
            self.resistances[fslot] = 0

    def is_inventory_full(self):
        return len([i for i in self.inventory if self.inventory.get(i)]) == const.inventory_max_size

    def is_inventory_empty(self):
        return len([i for i in self.inventory if self.inventory.get(i)]) == 0

    def remove_from_inventory(self, item, drop_key):
        assert item.is_in_inventory
        assert self.inventory.get(drop_key)
        self.inventory[drop_key].is_in_inventory = False
        self.inventory[drop_key] = None

    def add_to_inventory(self, item):
        assert not item.is_in_inventory
        assert not self.is_inventory_full()
        for i in self.inventory:
            if not self.inventory.get(i):
                self.inventory[i] = item
                item.is_in_inventory = True
                if isinstance(item, Weapon):
                    item.update_effective(self.fequiped)
                return i
        assert False
        return None

    def fequip(self, feature, key):
        assert not feature.equiped
        assert feature.is_in_inventory
        previous_feature = self.fequiped.get(feature.fslot)
        feature.equiped = True
        feature.is_in_inventory = False
        self.fequiped[feature.fslot] = feature
        for weapon in self.wequiped:
            w = self.wequiped.get(weapon)
            if w:
                w.update_effective(self.fequiped)
        for i in self.inventory:
            item = self.inventory.get(i)
            if item and isinstance(item, Weapon):
                item.update_effective(self.fequiped)
        if previous_feature:
            previous_feature.is_in_inventory = True
            previous_feature.equiped = False
            self.inventory[key] = previous_feature
        else:
            self.inventory[key] = None
        self.update_resistance()

    def wequip(self, weapon, key):
        assert not weapon.equiped
        assert weapon.is_in_inventory
        previous_weapon = self.wequiped.get(weapon.wslot)
        weapon.equiped = True
        weapon.is_in_inventory = False
        self.wequiped[weapon.wslot] = weapon
        weapon.update_effective(self.fequiped)

        if previous_weapon:
            if self.active_weapon == previous_weapon:
                self.active_weapon = None
            previous_weapon.is_in_inventory = True
            previous_weapon.equiped = False
            self.inventory[key] = previous_weapon
        else:
            self.inventory[key] = None

        if not self.active_weapon:
            self.active_weapon = weapon

    def update_resistance(self):
        for fslot in const.FeatureSlot:
            r = 0
            feature = self.fequiped.get(fslot)
            if feature:
                fego = feature.fego
                for fslot_equiped in const.FeatureSlot:
                    other = self.fequiped.get(fslot_equiped)
                    if other and other.fego == fego:
                        if other.is_stable():
                            r += other.level
                        else:
                            r += int(other.level/2)
            self.resistances[fslot] = r

class Monster(Entity):
    """
    A bug
    """
    def __init__(self, x, y, level, fcreator):
        self.hp = level * level
        super().__init__(x, y, str(self.hp), fcreator.fslot.value.get("color"), fcreator.fslot.value.get("name")+" bug", True, True, const.RenderOrder.ACTOR)
        self.level = level
        self.fslot = fcreator.fslot
        self.atk = 1
        self.speed = 5 - level
        self.fcreator = fcreator
        fcreator.n_bugs += 1

    def dead(self, entities):
        entities.remove(self)
        self.fcreator.n_bugs -= 1
        return self.fcreator.stabilize(self.level)

    def update_symbol(self):
        if self.hp > 0:
            self.char = str(self.hp)

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = abs(dx) + abs(dy)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if dx == 0:
            for i in [0,-1,1]:
                if not (game_map.is_blocked(self.x + dx + i, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x + dx + i, self.y + dy)):
                    self.move(dx + i, dy)
                    break
        elif dy == 0:
            for i in [0,-1,1]:
                if not (game_map.is_blocked(self.x + dx, self.y + dy + i) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y + dy + i)):
                    self.move(dx, dy + i)
                    break
        else: # both dx and dy are non-null
            if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
                self.move(dx, dy)
            elif not (game_map.is_blocked(self.x + dx, self.y) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y)):
                self.move(dx, 0)
            elif not (game_map.is_blocked(self.x, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x, self.y + dy)):
                self.move(0, dy)

    def distance_to(self, other):
        # Manhattan distance
        # distance = 1 iff the two points are adjacent
        dx = other.x - self.x
        dy = other.y - self.y
        return max(abs(dx), abs(dy))

    def move_astar(self, target, entities, game_map):
        # Create a FOV map that has the dimensions of the map
        pathfinding_map = game_map.get_copy_map()

        for entity in entities:
            if entity.collision and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                pathfinding_map.transparent[entity.y,entity.x] = pathfinding_map.walkable[entity.y,entity.x] = False

        astar = tcod.path.AStar(pathfinding_map)
        # Compute the path between self's coordinates and the target's coordinates
        path = astar.get_path(self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if path and len(path) < 25:
            # Find the next coordinates in the computed full path
            x, y = path[0]
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)



def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.collision and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None
