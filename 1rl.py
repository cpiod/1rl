import tcod
import tcod.event
import keys
import entity
import constants as const
import game_map as gmap
import time
import render
import log
import scheduling as sch

def main():
    screen_width = 100
    screen_height = 48

    sch_height = 3
    sch_width = 27

    # Inventory
    inv_height = screen_height - sch_height
    inv_width = sch_width

    # Log
    log_height = 10
    log_width = screen_width - inv_width

    # Size of the map
    map_width = screen_width - inv_width
    map_height = screen_height - log_height

    player = entity.Player(None, None)
    entities = [player]

    # tcod init
    tcod.console_set_custom_font('font.png', tcod.FONT_LAYOUT_ASCII_INROW)
    root_console = tcod.console_init_root(screen_width, screen_height, '1RL – 7DRL 2019')

    # map console
    con = tcod.console.Console(map_width, map_height)
    tcod.console_set_default_background(con, const.base03)
    tcod.console_clear(con)

    # log console
    log_panel = tcod.console.Console(log_width, log_height)
    tcod.console_set_default_background(log_panel, const.base03)
    tcod.console_clear(log_panel)

    # scheduling console
    sch_panel = tcod.console.Console(sch_width, sch_height)
    tcod.console_set_default_background(sch_panel, const.base03)
    tcod.console_clear(sch_panel)

    # inventory console
    inv_panel = tcod.console.Console(inv_width, inv_height)
    tcod.console_set_default_background(inv_panel, const.base03)
    tcod.console_clear(inv_panel)

    # scheduling
    turns = sch.Scheduling()
    turns.add_turn(0, const.TurnType.PLAYER, player)

    # map generation
    game_map = gmap.GameMap(map_width, map_height, con)
    game_map.make_map_bsp(player)

    # log init
    msglog = log.Log(log_width - 2, log_height - 3)

    # Test
    feature_test1 = entity.Feature(const.FeatureSlot.p, const.FeatureEgo.c3, 3, 2, 10)
    feature_test2 = entity.Feature(const.FeatureSlot.l, const.FeatureEgo.p3, 2, 6, 10)
    feature_test3 = entity.Feature(const.FeatureSlot.i, const.FeatureEgo.m2, 2, 6, 10)
    feature_test4 = entity.Feature(const.FeatureSlot.p, const.FeatureEgo.m2, 2, 6, 10)
    key = player.add_to_inventory(feature_test1)
    player.fequip(feature_test1, key)
    player.add_to_inventory(feature_test2)
    player.add_to_inventory(feature_test4)

    weapon_test1 = entity.Weapon(const.WeaponSlot.slow, 0.7, 5, const.WeaponEgo.c, 1)
    weapon_test2 = entity.Weapon(const.WeaponSlot.hack, 1, 3, const.WeaponEgo.m, 1)
    key = player.add_to_inventory(weapon_test1)
    player.wequip(weapon_test1, key)
    player.add_to_inventory(weapon_test2)

    menu_state = const.MenuState.STANDARD

    for i in range(20):
        game_map.spawn(entities, feature_test1)
    game_map.tiles[player.x][player.y].put_item(feature_test3, entities)

    # initial render
    render.render_map(root_console, con, entities, player, game_map, screen_width, screen_height)
    render.render_log(root_console, log_panel, msglog, map_height)
    render.render_sch(root_console, sch_panel, turns, map_width)
    render.render_inv(root_console, inv_panel, player, map_width, sch_height)
    tcod.console_flush()
    fov_recompute = False
    render_inv = False
    force_log = False
    time_malus = 0
    new_turn = True
    while not tcod.console_is_window_closed():
        if fov_recompute:
            game_map.recompute_fov(player.x, player.y)
            for e in entities:
                if not e.is_seen and game_map.is_visible(e.x, e.y):
                    e.is_seen = True
                    if isinstance(e, entity.Monster):
                        turns.add_turn(e.speed, const.TurnType.ENNEMY, e)
        render.render_log(root_console, log_panel, msglog, map_height, force_log)
        force_log = False
        render.render_map(root_console, con, entities, player, game_map, screen_width, screen_height)
        render.render_sch(root_console, sch_panel, turns, map_width)
        if render_inv:
            render.render_inv(root_console, inv_panel, player, map_width, sch_height)

        if new_turn:
            current_turn = turns.get_turn()
            new_turn = False
            # print("Turn "+str(current_turn.date)+": "+current_turn.ttype.name)
            if current_turn.ttype == const.TurnType.PLAYER and time_malus > 0:
                msglog.add_log("Bugs make you lose time. You next action cost "+str(time_malus)+"m.")

        fov_recompute = False

        tcod.console_flush()
        if current_turn.ttype == const.TurnType.PLAYER:
            for event in tcod.event.wait():
                key = None
                modifiers = []
                if event.type == "QUIT":
                    raise SystemExit()
                elif event.type == "KEYDOWN":
                    for m in tcod.event_constants._REVERSE_MOD_TABLE:
                        if m & event.mod != 0:
                            modifiers.append(tcod.event_constants._REVERSE_MOD_TABLE[m])
                    key = tcod.event_constants._REVERSE_SYM_TABLE.get(event.sym)
                else:
                    continue
                if menu_state == const.MenuState.STANDARD:
                    action = keys.handle_player_turn_keys(key, modifiers)
                elif menu_state == const.MenuState.DROP:
                    action = keys.handle_drop_keys(key, modifiers)
                elif menu_state == const.MenuState.EQUIP:
                    action = keys.handle_equip_keys(key, modifiers)
                else:
                    assert False

                exit_game = action.get("exit")
                if exit_game:
                    return True

                use_weapon = action.get('use_weapon')
                if use_weapon:
                    previous_active = player.active_weapon
                    new_active = player.wequiped.get(use_weapon)
                    if not new_active:
                        msglog.add_log("You don't have this weapon")
                    elif previous_active == new_active:
                        msglog.add_log("This weapon is already wielded")
                    else:
                        player.active_weapon = new_active
                        render_inv = True
                        turns.add_turn(time_malus + const.time_equip_weapon, const.TurnType.PLAYER, player)
                        time_malus = 0
                        new_turn = True

                grab = action.get('pickup')
                if grab:
                    if player.is_inventory_full():
                        msglog.add_log("Your inventory is full.")
                    else:
                        if game_map.is_there_item_on_floor(player):
                            item = game_map.get_item_on_floor(player, entities)
                            msglog.add_log("You pick up a "+item.name+".")
                            render_inv = True
                        else:
                            msglog.add_log("There is nothing on the floor to pick up.")

                drop = action.get('drop')
                if drop:
                    if game_map.is_there_item_on_floor(player):
                        msglog.add_log("There is already something there.")
                    else:
                        msglog.add_log("What do you want to drop? Press a, b, c, d or e.")
                        menu_state = const.MenuState.DROP

                equip = action.get('equip')
                if equip:
                    if player.is_inventory_empty():
                        msglog.add_log("You inventory is empty.")
                    else:
                        msglog.add_log("What do you want to equip? Press a, b, c, d or e.")
                        menu_state = const.MenuState.EQUIP

                drop_key = action.get('drop_key')
                if drop_key:
                    item = player.inventory.get(drop_key)
                    if item:
                        msglog.add_log("You drop a "+item.name)
                        game_map.drop_item_on_floor(player, entities, item, drop_key)
                        menu_state = const.MenuState.STANDARD
                        render_inv = True
                    else:
                        msglog.add_log("You don't have this item!")
                        menu_state = const.MenuState.STANDARD

                equip_key = action.get('equip_key')
                if equip_key:
                    item = player.inventory.get(equip_key)
                    if item:
                        msglog.add_log("You equip a "+item.name)
                        if isinstance(item, entity.Feature):
                            player.fequip(item, equip_key)
                        elif isinstance(item, entity.Weapon):
                            player.wequip(item, equip_key)
                        else:
                            assert False
                        menu_state = const.MenuState.STANDARD
                        render_inv = True
                    else:
                        msglog.add_log("You don't have this item!")
                        menu_state = const.MenuState.STANDARD



                cancel = action.get('cancel')
                if cancel:
                    msglog.add_log("Nevermind.")
                    menu_state = const.MenuState.STANDARD


                move = action.get('move')
                if move:
                    dx, dy = move

                    if (dx, dy) == (0, 0):
                        msglog.add_log("There is no time to lose!")
                    else:
                        destination_x = player.x + dx
                        destination_y = player.y + dy

                        if not game_map.is_blocked(destination_x, destination_y):
                            target = entity.get_blocking_entities_at_location(entities, destination_x, destination_y)

                            if target and target != player:
                                weapon = player.active_weapon
                                if not weapon:
                                    msglog.add_log("You have no weapon to attack with! Equip with 1, 2 or 3.")
                                else:
                                    dmg = weapon.attack(target, msglog)
                                    target.hp -= dmg
                                    target.update_symbol()
                                    if weapon.wslot.value.get("instable"):
                                        msglog.add_log("You hack the "+target.name+": your "+target.fcreator.name+" is less stable!")
                                        target.fcreator.destabilize(target.level)
                                        player.update_resistance()
                                    if target.hp <= 0:
                                        entities.remove(target)
                                        more_stable = target.fcreator.stabilize(target.level)
                                        player.update_resistance()
                                        if more_stable:
                                            msglog.add_log(target.name.capitalize()+" is defeated: your "+target.fcreator.name+" is more stable.")
                                        else:
                                            msglog.add_log(target.name.capitalize()+" is defeated but your "+target.fcreator.name+" is already stable.")
                                    render_inv = True
                                    turns.add_turn(time_malus + player.active_weapon.duration, const.TurnType.PLAYER, player)
                                    time_malus = 0
                                    new_turn = True
                            else:
                                player.move(dx, dy)
                                turns.add_turn(time_malus + const.time_move, const.TurnType.PLAYER, player)
                                time_malus = 0
                                fov_recompute = True
                                new_turn = True
                                force_log = True

        elif current_turn.ttype == const.TurnType.ENNEMY:
            e = current_turn.entity
            if e in entities:
                if e.distance_to(player) >= 2:
                    e.move_astar(player, entities, game_map)
                else:
                    delta_malus = max(0, e.atk - player.resistances[e.fslot])
                    time_malus += delta_malus
                    if time_malus > const.malus_max:
                        time_malus = const.malus_max
                turns.add_turn(e.speed, const.TurnType.ENNEMY, e)
            new_turn = True

if __name__ == '__main__':
    main()
