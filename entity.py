import tcod
import constants as const
import random
import math

"""
All the entity classes. Uses inheritance, not composition
"""

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
        # should be overriden !
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
        """
        Put item on the floor
        """
        assert self.item == None
        assert item not in entities
        self.item = item
        item.x = self.x
        item.y = self.y
        entities.append(item)

    def take_item(self, entities):
        """
        Take item from the floor
        """
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
        else:
            # floor and walls have no name, so they can't be described
            assert False
        return super().describe()

class Weapon(Entity):
    """
    A debugger
    """
    def __init__(self, wslot, wego, level):
        super().__init__(None, None, wego.value.get("char"), const.base3, wego.value.get("name")+" "+wslot.value.get("name")+" v"+str(level), False, True, const.RenderOrder.ITEM)
        self.wego = wego
        self.level = level
        self.success_rate = wslot.value.get("success_rate_base")
        self.duration = wslot.value.get("duration_base")
        self.wslot = wslot
        self.is_in_inventory = False
        self.equiped = False
        self.fslot_effective = []

    def update_effective(self, fequiped):
        self.fslot_effective = [fslot for fslot in const.FeatureSlot if fequiped.get(fslot) and fequiped.get(fslot).fego in self.wego.value.get("fego")]

    def stat_string(self):
        """
        used to render the right panel
        """
        string = str(round(self.success_rate * 100))+"% "+str(self.duration)+"s"
        if self.wslot.value.get("unstable"):
            string = "Stab- "+string
        return string

    def is_effective_on_fego(self, fego):
        return fego in self.wego.value.get("fego")

    def is_effective_on(self, target):
        if target.fcreator:
            return self.is_effective_on_fego(target.fcreator.fego)
        else: # fallback: check with the current equiped feature
            return target.fslot in self.fslot_effective

    def equip_log(self, msglog):
        # overriden
        pass

    def attack(self, target, msglog, turns, passive=False):
        dmg = 0
        duration = self.duration
        if random.random() < self.success_rate:
            # a confused attacked bug has 50% chance of being not confuse anymore
            if target.confusion_date and random.randint(1,2) == 1:
                target.confusion_date = None
                target.name = target.fslot.value.get("name")+" bug v"+str(target.level)
                msglog.add_log("Your attack makes the "+target.name+" focused again!")

           # succesfull attack
            if passive:
                # passive (basic) attack inflict only 1 dmg
                dmg = 1
            else:
                effective = self.is_effective_on(target)
                # not effective: 1d(level). effective: 1d(2*level)
                if effective:
                    dmg = random.randint(1, 2*self.level)
                else:
                    dmg = random.randint(1, self.level)
            target.hp -= dmg
            # because symbol = HP
            target.update_symbol()
        else:
            if isinstance(target, Boss):
                msglog.add_log("You miss "+target.name+".")
            else:
                msglog.add_log("You miss the "+target.name+".")

        return (dmg, duration)

    def effect_on_active(self, player):
        # overriden
        player.time_move = const.time_move
        player.name = "You"

    def describe(self):
        d = ["Weapons help you fight bugs.", "", "Each hit uses "+str(self.duration)+"s.", "Its hit probability is "+str(round(self.success_rate*100))+"%."]
        l = self.wego.value.get("fego")
        d += ["", "Damage:","1d"+str(self.level*2)+" against "+l[0].value.get("name")+", "+l[1].value.get("name")+" and "+l[2].value.get("name")+" bugs.","1d"+str(self.level)+" against other bugs."]

        if self.wslot.value.get("unstable"):
            d += ["", "It's a hack: fighting bugs decreases the stability!"]
        return d

class TelepathicWeapon(Weapon):
    """
    Grant telepathy. See effect in render.py
    """
    def equip_log(self, msglog):
        msglog.add_log("You feel conscious of bug presence.")

    def describe(self):
        d = super().describe()
        d.append("")
        d.append("It grants its wielder telepathy: bugs are visible through walls.")
        return d

class BasicWeapon(Weapon):
    """
    Pun-based weapon: basic (standard) and basic (not acid)
    Note: RNG bug v2 and v3 are immune to basic weapons because they never miss their attack
    """
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
    """
    Paradoxical weapons confuse bugs. Confused bugs can't attack nor move.
    """
    def attack(self, target, msglog, turns, passive):
        (dmg,duration) = super().attack(target, msglog, turns, passive)
        # if we didn't missed it
        if dmg != 0  and not target.confusion_date and random.randint(1, 3) == 1:
            if isinstance(target, Boss):
                msglog.add_log("Paradoxes won't help you against Self-doubt!", color_active=const.red, color_inactive=const.desat_red)
            elif dmg < target.hp:
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
    """
    Mythical weapon make you faster (movement uses 75% of normal time). Handy to explore…
    """
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
        # track the number of generated bugs
        self.n_bugs = [0,0,0]
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
        """
        Returns True iff the feature is more stable
        """
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
        # there is a hidden inventory slot (used when the player equips a weapon from the ground directly)
        for i in range(const.inventory_max_size+1):
            self.inventory[chr(letter_index+i)] = None
        self.time_move = const.time_move
        self.time_malus = 0
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
        # return True # DEBUG
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
        # drop an object
        assert item.is_in_inventory
        assert self.inventory.get(drop_key)
        self.inventory[drop_key].is_in_inventory = False
        self.inventory[drop_key] = None

    def add_to_inventory(self, item):
        # pick up an object
        assert not item.is_in_inventory
        for i in self.inventory:
            if not self.inventory.get(i):
                self.inventory[i] = item
                item.is_in_inventory = True
                if isinstance(item, Weapon):
                    item.update_effective(self.fequiped)
                return i
        # there should be an empty slot! (can be the extra/hidden slot)
        assert False
        return None

    def fequip(self, feature, key):
        assert not feature.equiped
        assert feature.is_in_inventory
        previous_feature = self.fequiped.get(feature.fslot)

        # you can't equip an unstable feature
        if previous_feature and not previous_feature.is_stable():
            return {"unstable-previous": previous_feature}

        # you want to equip a v2 feature but don't have a v1 feature
        if not previous_feature and feature.level > 1:
            return {"level-problem-no-previous": True}

        # jumps for v1 to v3. Obsolete.
        if previous_feature and previous_feature.level < feature.level - 1:
            assert False # obsolete
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
        """
        Returns a metric estimating the level of the player
        Used for weapon generation
        """
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
                if feature.level == 1:
                    r = 2
                else:
                    assert feature.level == 2
                    r = 6
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
            elif isinstance(self.active_weapon, TelepathicWeapon):
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
        return int(score)

    def reset_time_malus(self):
        self.time_malus = 0

    def add_time_malus(self, delta_malus, fslot):
        self.time_malus += delta_malus

class Monster(Entity):
    """
    A bug
    It has generally a creator: the feature that generated it
    Some bugs have no creator: the boss and its minions
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        # self.fslot replace fcreator when there is no creator
        if fslot == None:
            self.fslot = fcreator.fslot
        else:
            self.fslot = fslot
        self.hp = const.bug_hp[level-1]
        super().__init__(x, y, str(self.hp), self.fslot.value.get("color"), self.fslot.value.get("name")+" bug v"+str(level), True, True, const.RenderOrder.ACTOR)
        self.level = level
        self.reset_nb_atk()
        self.atk = const.bug_atk[level-1]
        self.speed_atk = const.bug_speed_atk[level-1]
        self.speed_mov = const.bug_speed_mov[level-1]
        self.fcreator = fcreator
        self.success_rate = const.monster_success_rate[self.level - 1]
        if self.fcreator:
            assert fcreator.n_bugs[self.level - 1] < const.n_bugs_max[fcreator.level - 1][self.level - 1]
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
                    return True
                    break
        elif dy == 0:
            for i in [0,-1,1]:
                if not (game_map.is_blocked(self.x + dx, self.y + dy + i) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y + dy + i)):
                    self.move(dx, dy + i)
                    return True
                    break
        else: # both dx and dy are non-null
            if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
                self.move(dx, dy)
                return True
            elif not (game_map.is_blocked(self.x + dx, self.y) or
                    get_blocking_entities_at_location(entities, self.x + dx, self.y)):
                self.move(dx, 0)
                return True
            elif not (game_map.is_blocked(self.x, self.y + dy) or
                    get_blocking_entities_at_location(entities, self.x, self.y + dy)):
                self.move(0, dy)
                return True
        return False

    def distance_to(self, other):
        # Manhattan distance
        # distance = 1 iff the two points are adjacent
        dx = other.x - self.x
        dy = other.y - self.y
        return max(abs(dx), abs(dy))

    def get_copy_map(self, game_map):
        """
        Overriden by mapgen bugs
        """
        return game_map.get_copy_map()

    def move_astar(self, target, entities, game_map, turns):
        if self.confusion_date:
            if self.confusion_date >= turns.current_date:
                return
            else:
                self.name = self.fslot.value.get("name")+" bug v"+str(self.level)
                self.confusion_date = None

        pathfinding_map = self.get_copy_map(game_map)

        # First, get a path without entities (for backup)

        astar = tcod.path.AStar(pathfinding_map)
        path = astar.get_path(self.x, self.y, target.x, target.y)
        backup_x = backup_y = None
        if path:
            backup_x, backup_y = path[0]

        # Then, get a path with entities

        for entity in entities:
            if entity.collision and entity != self and entity != target:
                pathfinding_map.transparent[entity.y,entity.x] = pathfinding_map.walkable[entity.y,entity.x] = False

        astar = tcod.path.AStar(pathfinding_map)
        path = astar.get_path(self.x, self.y, target.x, target.y)

        # if the path is to long, uses the backup strat
        if path and len(path) < 45:
            x, y = path[0]
            if x or y:
                self.x = x
                self.y = y
                return True
        else:
            if (backup_x or backup_y) and pathfinding_map.walkable[backup_y,backup_x]:
                self.x = backup_x
                self.y = backup_y
                return True
            else:
                # if you can't use astar, just go in straight line
                return self.move_towards(target.x, target.y, game_map, entities)

    def reset_nb_atk(self):
        self.nb_atk = const.nb_atk[self.level-1]

    def attack(self, player, turns):
        if self.confusion_date:
            if self.confusion_date >= turns.current_date:
                return {}
            else:
                self.name = self.fslot.value.get("name")+" bug v"+str(self.level)
                self.confusion_date = None
        if self.nb_atk == 0:
            return {}
        self.nb_atk -= 1
        if random.random() < self.success_rate:
            # compute damage w.r.t. the player resistance
            r = player.resistances[self.fslot]
            mul = const.resistance_mul[min(len(const.resistance_mul)-1, r)]
            delta_malus = round(self.atk*mul)
            return {"dmg": delta_malus}
        else:
            return {"missed": True}

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
        self.level = 3
        self.atk = 300
        self.speed_atk = 350
        self.speed_mov = 30
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
        return super().describe() + ["", "This v"+str(self.level)+" "+self.fslot.value.get("name")+" bug hits harder."]

class LootBug(Monster):
    """
    Loot bug have a higher stability reward
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        super().__init__(x, y, level, fcreator, fslot)
        self.stability_reward = 1.5 * self.stability_reward

    def describe(self):
        return super().describe() + ["", "This v"+str(self.level)+" "+self.fslot.value.get("name")+" bug stabilizes faster your feature."]


class RNGBug(Monster):
    """
    RNG bugs can't fail their attack
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        super().__init__(x, y, level, fcreator, fslot)
        self.success_rate = 1

    def describe(self):
        return super().describe() + ["", "This v"+str(self.level)+" "+self.fslot.value.get("name")+" bug cannot miss its attacks."]


class AnimationBug(Monster):
    """
    Animation bug don't show their HP
    """
    def __init__(self, x, y, level, fcreator, fslot=None):
        super().__init__(x, y, level, fcreator, fslot)
        self.char = "?"

    def update_symbol(self):
        pass

    def describe(self):
        return super().describe() + ["", "You cannot see the HP of this v"+str(self.level)+" "+self.fslot.value.get("name")+" bug."]


class MapGenBug(Monster):
    """
    Mapgen bug can phase
    """
    def get_copy_map(self, game_map):
        return game_map.get_copy_empty_map()

    def describe(self):
        return super().describe() + ["", "This v"+str(self.level)+" "+self.fslot.value.get("name")+" bug phases through walls."]


def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.collision and entity.x == destination_x and entity.y == destination_y:
            return entity
    return None
