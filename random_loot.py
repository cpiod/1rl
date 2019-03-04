import random
import entity
import constants as const

def get_random_loot(turns, player):
    if random.randint(0,2) > 0:
        return get_random_feature(turns, player)
    else:
        return get_random_weapon(turns, player)

def get_random_feature(turns, player):
    (remaining_d, _, _, _) = turns.get_remaining()
    flevel = player.flevel()
    rand = 8*flevel + 1 * (7 - remaining_d) + sum([random.randint(1,6) for i in range(1)])
    level = int(max(1,min(3, rand/10+1)))
    fego = random.choice(list(const.FeatureEgo))
    fslot = random.choice(list(const.FeatureSlot))
    return entity.Feature(fslot, fego, level)

def get_random_weapon(turns, player):
    (remaining_d, _, _, _) = turns.get_remaining()
    flevel = player.flevel()
    # Weapon are stronger than feature
    rand = 10*flevel + 2 * (7 - remaining_d) + sum([random.randint(1,6) for i in range(1)])
    level = int(max(1,min(5, rand/10+1)))
    wego = random.choice(list(const.WeaponEgo))
    wslot = random.choice(list(const.WeaponSlot))
    return entity.Weapon(wslot, wego, level)

