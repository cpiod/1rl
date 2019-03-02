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
        self.is_in_inventory = False
        self.fslot_effective = []

    def update_effective(self, fequiped):
        self.fslot_effective = [fslot for fslot in const.FeatureSlot if fequiped.get(fslot) and fequiped.get(fslot).fego in self.wego.value.get("fego")]
        # print(self.name+" is affective against "+str(self.fslot_effective))

    def stat_string(self):
        string = str(round(self.success_rate * 100))+"% "+str(self.duration)+"mn"
        if self.wslot.value.get("instable"):
            string = "Stab- "+string
        return string

class Feature(Entity):
    """
    A feature
    """
    def __init__(self, fslot, fego, level, stability, max_stability):
        super().__init__(None, None, fego.value.get("char"), fslot.value.get("color"), fego.value.get("name")+" "+fslot.value.get("name"), False, True, const.RenderOrder.ITEM)
        self.fslot = fslot
        self.fego = fego
        self.is_in_inventory = False
        self.level = level
        self.stability = stability
        self.max_stability = max_stability

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

    def add_to_inventory(self, item):
        if item.is_in_inventory:
            print("Already in inventory!")
            return
        for i in self.inventory:
            if not self.inventory.get(i):
                self.inventory[i] = item
                item.is_in_inventory = True
                return
        print("Inventory already full!")


    def fequip(self, feature):
        if not self.fequiped.get(feature.fslot):
            self.fequiped[feature.fslot] = feature
            for weapon in self.wequiped:
                weapon.update_effective(self.fequiped)
        else:
            print("Slot already used by "+str(self.fequiped.get(feature.fslot)))

    def wequip(self, weapon):
        if not self.wequiped.get(weapon.wslot):
            weapon.update_effective(self.fequiped)
            self.wequiped[weapon.wslot] = weapon
            if not self.active_weapon:
                self.active_weapon = weapon
        else:
            print("Slot already used by "+str(self.wequiped.get(weapon.fslot)))

class Monster(Entity):
    """
    A bug
    """
    def __init__(self, x, y, hp, speed, fcreator):
        super().__init__(x, y, str(hp), fcreator.fslot.value.get("color"), fcreator.fslot.value.get("name")+" bug", True, True, const.RenderOrder.ACTOR)
        self.fslot = fcreator.fslot
        self.hp = hp
        self.speed = speed
        self.fcreator = fcreator

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
