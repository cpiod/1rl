import random
import entity
import constants as const

def get_random_loot(turns):
    if random.randint(0,2) > 0:
        return get_random_feature(turns)
    else:
        return get_random_weapon(turns)

def get_random_feature(turns):
    (remaining_d, _, _, _) = turns.get_remaining()
    rand = sum([random.randint(1,6) for i in range(8-remaining_d)])
    level = int(max(1,min(3, rand/10)))
    fego = random.choice(list(const.FeatureEgo))
    fslot = random.choice(list(const.FeatureSlot))
    return entity.Feature(fslot, fego, level)

def get_random_weapon(turns):
    (remaining_d, _, _, _) = turns.get_remaining()
    rand = sum([random.randint(1,10) for i in range(8-remaining_d)])
    # Weapon are stronger than feature
    level = int(max(1,min(5, rand/10)))
    wego = random.choice(list(const.WeaponEgo))
    wslot = random.choice(list(const.WeaponSlot))
    return entity.Weapon(wslot, wego, level)

