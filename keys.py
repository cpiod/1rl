import constants as const

def is_shift(modifiers):
    return 'tcod.event.KMOD_LSHIFT' in modifiers or 'tcod.event.KMOD_RSHIFT' in modifiers

def handle_player_turn_keys(key, modifiers):
    if key == None:
        return {}

    # Movement keys
    if key == "tcod.event.K_UP" or key == 'k' or key == "tcod.event.K_KP_8":
        return {'move': (0, -1)}
    # elif key == "tcod.event.K_DOWN" and is_shift(modifiers):
        # return {'move': (0, 2)}
    elif key == "tcod.event.K_DOWN" or key == 'j' or key == "tcod.event.K_KP_2":
        return {'move': (0, 1)}
    elif key == "tcod.event.K_LEFT" or key == 'h' or key == "tcod.event.K_KP_4":
        return {'move': (-1, 0)}
    elif key == "tcod.event.K_RIGHT" or key == 'l' or key == "tcod.event.K_KP_6":
        return {'move': (1, 0)}
    elif key == 'tcod.event.K_y' or key == "tcod.event.K_KP_7":
        return {'move': (-1, -1)}
    elif key == 'tcod.event.K_u' or key == "tcod.event.K_KP_9":
        return {'move': (1, -1)}
    elif key == 'tcod.event.K_b' or key == "tcod.event.K_KP_1":
        return {'move': (-1, 1)}
    elif key == 'tcod.event.K_n' or key == "tcod.event.K_KP_3":
        return {'move': (1, 1)}
    elif key == 'tcod.event.K_PERIOD' or key == "tcod.event.K_KP_5":
        return {'move': (0, 0)}

    elif key == 'tcod.event.K_RETURN':
        return {'descend': True}

    elif key == 'tcod.event.K_1':
        return {'use_weapon': const.WeaponSlot.fast}
    elif key == 'tcod.event.K_2':
        return {'use_weapon': const.WeaponSlot.slow}
    elif key == 'tcod.event.K_3':
        return {'use_weapon': const.WeaponSlot.hack}

    elif key == 'tcod.event.K_QUESTION' \
    or (key == 'tcod.event.K_QUOTE' and is_shift(modifiers))\
    or (key == 'tcod.event.K_SLASH' and is_shift(modifiers))\
    or (key == 'tcod.event.K_COMMA' and is_shift(modifiers)):
        return {'help': True}

    elif key == 'tcod.event.K_g':
        return {'pickup': True}

    elif key == 'tcod.event.K_ESCAPE':
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}


