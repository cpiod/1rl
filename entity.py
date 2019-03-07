import tcod
import constants as const
import random
import math

class Entity:
    """
    A generic entity
    """

    def __init__(self, x, y, char, color, name, collision, transparent, render_order, is_seen=False):
        self.x = x
        self.y = y
        self.char = char
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

    def describe(self):
        return ["No description."]

class Tile(Entity):
    """
    A floor, a door or a wall
    """

    def __init__(self, x, y, color_coeff=1, ttype=const.TileType.WALL):
        super().__init__(x, y, ttype.value.get("char"), ttype.value.get("color")*color_coeff, ttype.value.get("name"), ttype.value.get("collision"), ttype.value.get("transparent"), const.RenderOrder.TILE)
        self.ftype = ttype
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

    def describe(self):
        if self.ftype == const.TileType.DOOR:
            return ["A plain old wood door."]
        elif self.ftype == const.TileType.STAIRS:
            return ["These stairs lead to the next floor."]
        elif self.ftype == const.TileType.BOSS_STAIRS:
            return ["You feel anxious about these stairs."]
        return super().describe()

class Weapon(Entity):
    """
    A debugger
    """
    def __init__(self, wslot, wego, level):
        super().__init__(None, None, wego.value.get("char"), const.base3, wego.value.get("name")+" "+wslot.value.get("name")+" v"+str(level), False, True, const.RenderOrder.ITEM)
        self.wego = wego
        self.level = level
        # self.success_rate = min(1, int(100*(wslot.value.get("success_rate_base")+level*0.05))/100)
        self.success_rate = wslot.value.get("success_rate_base")
        self.duration = wslot.value.get("duration_base")
        self.wslot = wslot
        self.dmg = self.level
        self.is_in_inventory = False
        self.equiped = False
        self.fslot_effective = []

    def update_effective(self, fequiped):
        self.fslot_effective = [fslot for fslot in const.FeatureSlot if fequiped.get(fslot) and fequiped.get(fslot).fego in self.wego.value.get("fego")]

    def stat_string(self):
        string = str(round(self.success_rate * 100))+"% "+str(self.duration)+"s"
        if self.wslot.value.get("instable"):
            string = "Stab- "+string
        return string

    def is_effective_on_fego(self, fego):
        return fego in self.wego.value.get("fego")

    def is_effective_on(self, fslot):
        return fslot in self.fslot_effective

    def equip_log(self, msglog):
        pass

    def attack(self, target, msglog, turns):
        dmg = 0
        duration = self.duration
        if random.random() < self.success_rate:
            dmg = self.dmg
            target.hp -= dmg
            target.update_symbol()
           # succesfull attack
            effective = self.is_effective_on(target)
            if effective:
                duration = int(self.duration/2)
        else:
            msglog.add_log("You miss the "+target.name)

        return (dmg, duration)

    def effect_on_active(self, player):
        player.time_move = const.time_move
        player.name = "You"

    def describe(self):
        d = ["Weapons help you fight bugs.", "", "Each hit uses "+str(self.duration)+"s.", "Its hit probability is "+str(round(self.success_rate*100))+"%.", ""]
        if self.wslot.value.get("instable"):
            d.append("It's a hack: fighting bugs decrease the stability!")
            d.append("")
        l = self.wego.value.get("fego")
        d.append("It is twice as fast against "+l[0].value.get("name")+", "+l[1].value.get("name")+" and "+l[2].value.get("name")+" bugs.")
        return d

class ConsciousWeapon(Weapon):
    def equip_log(self, msglog):
        msglog.add_log("You feel conscious of bug presence.")

    def describe(self):
        d = super().describe()
        d.append("")
        d.append("It grants its wielder telepathy: bugs are visible through walls.")
        return d

class BasicWeapon(Weapon):
    def equip_log(self, msglog):
        msglog.add_log("You feel surrounded by a caustic aura.")

    def effect_on_active(self, player):
        super().effect_on_active(player)
        player.name = "You (protected by a caustic aura)"

    def describe(self):
        d = super().describe()
        d.append("")
        d.append("It protects its wielder with a caustic aura. Bugs may take damage when they miss.")
        return d

class ParadoxicalWeapon(Weapon):
    def attack(self, target, msglog, turns):
        (dmg,duration) = super().attack(target, msglog, turns)
        # if we missed it
        if dmg == 0 and not isinstance(target, Boss) and not target.confusion_date and random.randint(1, 2) == 1:
            msglog.add_log(random.choice(const.paradox_list))
            msglog.add_log("The "+target.name+" is confused!")
            target.confusion_date = turns.current_date + const.confusion_duration
            target.name = "confused "+target.fslot.value.get("name")+" bug v"+str(target.level)
        return (dmg,duration)

    def equip_log(self, msglog):
        msglog.add_log("Your weapon tells you a confusing paradox.")

    def describe(self):
        d = super().describe()
        d.append("")
        d.append("Its attacks can confuse bugs. Confused bugs cannot attack nor move.")
        return d

class MythicalWeapon(Weapon):
    def equip_log(self, msglog):
        msglog.add_log("Your mythical weapon grants you superhuman speed.")

    def effect_on_active(self, player):
        super().effect_on_active(player)
        player.time_move = int(const.time_move * 0.75)
        player.name = "You (fast)"

    def describe(self):
        d = super().describe()
        d.append("")
        d.append("It makes its wielder faster in its moving.")
        return d


class Feature(Entity):
    """
    A feature
    """
    def __init__(self, fslot, fego, level):
        super().__init__(None, None, fego.value.get("char"), fslot.value.get("desat_color"), fego.value.get("name")+" "+fslot.value.get("name")+" v"+str(level), False, True, const.RenderOrder.ITEM)
        self.n_bugs = [0,0,0]
        self.n_bugs_max = const.n_bugs_max[level-1]
        self.max_stability = const.max_stab[level-1]
        self.stability = 0
        self.fslot = fslot
        self.fego = fego
        self.is_in_inventory = False
        self.equiped = False
        self.level = level

    def destabilize(self, amount):
        self.stability -= amount
        if self.stability < 0:
            self.stability = 0

    def stabilize(self, amount):
        if self.stability == self.max_stability:
            return False
        self.stability += amount
        if self.stability > self.max_stability:
            self.stability = self.max_stability
        return True

    def is_stable(self):
        return (self.stability / self.max_stability) >= const.stability_threshold

    def describe(self):
        wego = [wego for wego in const.WeaponEgo if self.fego in wego.value.get("fego")]
        assert len(wego) == 1
        wego = wego[0]
        d = ["Features grant you resistance.", "", "Stability: "+str(self.stability)+"/"+str(self.max_stability)]
        if self.is_stable():
            d.append("This feature is stable.")
        else:
            d.append("This feature is unstable.  Once equipped, you cannot unequip it.")
        d += ["", "Its bugs are squashed by "+wego.value.get("name")+" weapons."]
        if self.level == 2:
            d += ["", "It is a v2 feature: its bugs are tougher!"]
            d += ["", "Receive a stability bonus if it upgrades a "+self.fego.value.get("name")+" "+self.fslot.value.get("name")+" v"+str(self.level-1)+"."]
        elif self.level == 1:
            d += ["", "Grants a stability bonus if upgraded with a "+self.fego.value.get("name")+" "+self.fslot.value.get("name")+" v"+str(self.level+1)+"."]
        return d

class Player(Entity):
    """
    The player
    """
    def __init__(self, x, y):
        super().__init__(x, y, '@', const.base3, "You", True, True, const.RenderOrder.ACTOR, is_seen=True)
        self.inventory = {}

        letter_index = ord('a')
        for i in range(const.inventory_max_size+1):
            self.inventory[chr(letter_index+i)] = None
        self.time_move = const.time_move
        self.synergy = []
        self.wequiped = {}
        self.fequiped = {}
        self.resistances = {}
        self.active_weapon = None
        for fslot in const.FeatureSlot:
            self.resistances[fslot] = 0

    def change_active_weapon(self, weapon):
        self.active_weapon = weapon
        self.visible_color = weapon.wego.value.get("player_color")
        weapon.effect_on_active(self)

    def can_go_boss(self):
        # return True # TODO
        for fslot in const.FeatureSlot:
            f = self.fequiped.get(fslot)
            if not f or not f.is_stable():
                return False
        return True

    def is_inventory_full(self):
        assert len([i for i in self.inventory if self.inventory.get(i)]) <= const.inventory_max_size
        return len([i for i in self.inventory if self.inventory.get(i)]) == const.inventory_max_size

    def is_inventory_empty(self):
        assert len([i for i in self.inventory if self.inventory.get(i)]) <= const.inventory_max_size
        return len([i for i in self.inventory if self.inventory.get(i)]) == 0

    def remove_from_inventory(self, item, drop_key):
        assert item.is_in_inventory
        assert self.inventory.get(drop_key)
        self.inventory[drop_key].is_in_inventory = False
        self.inventory[drop_key] = None

    def add_to_inventory(self, item):
        assert not item.is_in_inventory
        # assert not self.is_inventory_full()
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
        # you can't equip an unstable feature
        if previous_feature and not previous_feature.is_stable():
            return {"unstable-previous": previous_feature}
        if not previous_feature and feature.level > 1:
            return {"level-problem-no-previous": True}
        if previous_feature and previous_feature.level < feature.level - 1:
            return {"level-problem-previous": previous_feature}
        feature.equiped = True
        feature.is_in_inventory = False
        self.fequiped[feature.fslot] = feature
        # update effective
        for weapon in self.wequiped:
            w = self.wequiped.get(weapon)
            if w:
                w.update_effective(self.fequiped)
        for i in self.inventory:
            item = self.inventory.get(i)
            if item and isinstance(item, Weapon):
                item.update_effective(self.fequiped)
        # replace previous feature in inventory
        if previous_feature:
            previous_feature.is_in_inventory = True
            previous_feature.equiped = False
            self.inventory[key] = previous_feature
        else:
            self.inventory[key] = None
        # update player resistance
        self.update_resistance()
        # there is no need to recall the synergy
        if previous_feature and previous_feature.fego == feature.fego:
            return {"inheritance": previous_feature,"synergy": None}

        synergy = self.get_synergy(feature.fego)
        return {"synergy": synergy}

    def flevel(self):
        level = 0
        for fslot in self.fequiped:
            feature = self.fequiped.get(fslot)
            if feature:
                level += feature.level
                if not feature.is_stable():
                    level -= 0.5
        return level / 5

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
                self.change_active_weapon(weapon)
            previous_weapon.is_in_inventory = True
            previous_weapon.equiped = False
            self.inventory[key] = previous_weapon
        else:
            self.inventory[key] = None

        if not self.active_weapon:
            self.change_active_weapon(weapon)

        return {}

    def get_synergy(self, fego):
        nb = 0
        for fslot in const.FeatureSlot:
            feature = self.fequiped.get(fslot)
            if feature and feature.fego == fego:
                nb += 1
        if nb > 1:
            return nb
        return None

    def update_resistance(self):
        self.synergy = []
        for fslot in const.FeatureSlot:
            idem = 0
            feature = self.fequiped.get(fslot)
            r = 0
            if feature:
                r = 2*feature.level
                if not feature.is_stable():
                    r -= 1
                for fslot_equiped in const.FeatureSlot:
                    other = self.fequiped.get(fslot_equiped)
                    if other and other.fego == feature.fego:
                        idem += 1
            if idem > 1:
                self.synergy.append(fslot)
            self.resistances[fslot] = r + const.bonus_idem[idem]

    def describe(self):
        d = ["You are a young and hopeful programmer.", "", "Your goal is to release your first game in 7 days.  Your game must have five stable features.","","Beware, bugs are not the only things between you and the release..."]
        if not self.active_weapon:
            d += ["", "You wield no weapon."]
        else:
            d += ["", "You wield a "+self.active_weapon.name+"."]
            if isinstance(self.active_weapon, BasicWeapon):
                d += ["", "You are protected by a caustic aura.", "Click on your weapon for more details."]
            elif isinstance(self.active_weapon, MythicalWeapon):
                d += ["", "You move fast."]
            elif isinstance(self.active_weapon, ConsciousWeapon):
                d += ["", "You are a telepath."]
        return d

    def get_score(self):
        score = 0
        for fslot in const.FeatureSlot:
            f = self.fequiped.get(fslot)
            if f:
                score += f.stability
                if f.is_stable():
                    score += 50
        score += 100*len(self.synergy)
        return score

class Monster(Entity):
    """
    A bug
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        if fslot == None:
            self.fslot = fcreator.fslot
        else:
            self.fslot = fslot
        self.hp = const.bug_hp[level-1]
        super().__init__(x, y, str(self.hp), self.fslot.value.get("color"), self.fslot.value.get("name")+" bug v"+str(level), True, True, const.RenderOrder.ACTOR)
        self.level = level
        self.atk = const.bug_atk[level-1]
        self.speed_atk = const.bug_speed_atk[level-1]
        self.speed_mov = const.bug_speed_mov[level-1]
        self.fcreator = fcreator
        self.success_rate = const.monster_success_rate[self.level - 1]
        if self.fcreator:
            assert fcreator.n_bugs[self.level - 1] < fcreator.n_bugs_max[self.level - 1]
            fcreator.n_bugs[self.level - 1] += 1
        self.stability_reward = const.stab_reward[self.level-1]
        self.confusion_date = None

    def dead(self, stabilize=True):
        if self.fcreator:
            self.fcreator.n_bugs[self.level - 1] -= 1
            assert self.fcreator.n_bugs[self.level - 1] >= 0
            if not stabilize:
                return False
            return self.fcreator.stabilize(self.stability_reward)
        else:
            return False

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

    def get_copy_map(self, game_map):
        return game_map.get_copy_map()

    def move_astar(self, target, entities, game_map, turns):
        if self.confusion_date:
            if self.confusion_date >= turns.current_date:
                return
            else:
                self.name = self.fslot.value.get("name")+" bug v"+str(self.level)
                self.confusion_date = None

        # Create a FOV map that has the dimensions of the map
        pathfinding_map = self.get_copy_map(game_map)

        astar = tcod.path.AStar(pathfinding_map)
        path = astar.get_path(self.x, self.y, target.x, target.y)
        backup_x = backup_y = None
        if path:
            backup_x, backup_y = path[0]

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
        if path and len(path) < 45:
            # Find the next coordinates in the computed full path
            x, y = path[0]
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            if (backup_x or backup_y) and pathfinding_map.walkable[backup_y,backup_x]:
                self.x = backup_x
                self.y = backup_y
            else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
                self.move_towards(target.x, target.y, game_map, entities)


    def attack(self, player, turns):
        if self.confusion_date:
            if self.confusion_date >= turns.current_date:
                return {}
            else:
                self.name = self.fslot.value.get("name")+" bug v"+str(self.level)
                self.confusion_date = None
        if random.random() < self.success_rate:
            r = player.resistances[self.fslot]
            mul = const.resistance_mul[min(len(const.resistance_mul)-1, r)]
            delta_malus = round(self.atk*mul)
            return {"dmg": delta_malus}
        else:
            return {}

    def describe(self):
        d = ["Bugs are generated by unstable features.  Fight them to stabilize your features!"]
        if self.fcreator:
            d += ["","This bug has been generated by a "+self.fcreator.name+"."]
        if self.confusion_date:
            d += ["","It is confused: it cannot attack nor move."]
        return d

class Boss(Monster):
    def __init__(self, x, y):
        self.fcreator = None
        self.max_hp = 200
        self.hp = self.max_hp
        Entity.__init__(self, x, y, "@", const.red, "Self-doubt", True, True, const.RenderOrder.ACTOR)
        self.fslot = None
        self.atk = 100
        self.speed_atk = 20
        self.speed_mov = 10
        self.success_rate = 1
        self.stability_reward = 0
        self.confusion_date = None
        self.invocations = list(const.FeatureSlot)
        random.shuffle(self.invocations)

    def update_symbol(self):
        pass

    def attack(self, player, turns):
        if self.hp/self.max_hp <= len(self.invocations)/6:
            out = self.invocations[0]
            del self.invocations[0]
            return {"invok": out}
        return {"dmg": round(self.atk)}

    def describe(self):
        return ["Self-doubt is the last thing between you and the release.","", "There is no time to lose: fight to win!"]

class MonsterBug(Monster):
    """
    Monster bug are tougher
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        super().__init__(x, y, level, fcreator, fslot)
        self.atk = int(self.atk * 1.5)

    def describe(self):
        return super().describe() + ["", "This v2 "+self.fslot.value.get("name")+" bug hits harder."]

class LootBug(Monster):
    """
    Loot bug have a lower stability reward
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        super().__init__(x, y, level, fcreator, fslot)
        self.stability_reward = 1.5 * self.stability_reward

    def describe(self):
        return super().describe() + ["", "This v2 "+self.fslot.value.get("name")+" bug stabilizes faster your feature."]


class RNGBug(Monster):
    """
    RNG bugs can't fail their attack
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        super().__init__(x, y, level, fcreator, fslot)
        self.success_rate = 1

    def describe(self):
        return super().describe() + ["", "This v2 "+self.fslot.value.get("name")+" bug cannot miss its attacks."]


class AnimationBug(Monster):
    """
    Animation bug don't have their HP written
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        super().__init__(x, y, level, fcreator, fslot)
        self.char = "?"

    def update_symbol(self):
        pass

    def describe(self):
        return super().describe() + ["", "You cannot see the HP of this v2 "+self.fslot.value.get("name")+" bug."]


class MapGenBug(Monster):
    """
    Mapgen bug can phase
    """
    def get_copy_map(self, game_map):
        return game_map.get_copy_empty_map()

    def describe(self):
        return super().describe() + ["", "This v2 "+self.fslot.value.get("name")+" bug phases through walls."]

def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.collision and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None
