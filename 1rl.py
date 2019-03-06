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
import random_loot
import random
import sys
import os.path

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
    map_height = screen_height - log_height - 1

    # Popup size
    popup_width = int(2 * map_width / 3)
    popup_height = int(2 * map_height / 3)

    player = entity.Player(None, None)
    entities = [player]

    # tcod init
    tcod.console_set_custom_font(resource_path('font.png'), tcod.FONT_LAYOUT_ASCII_INROW)
    root_console = tcod.console_init_root(screen_width, screen_height, '1RL – 7DRL 2019')

    # map console
    con = tcod.console.Console(map_width, map_height)
    tcod.console_set_default_background(con, const.base03)
    tcod.console_clear(con)

    # description console
    des_panel = tcod.console.Console(log_width, 1)
    tcod.console_set_default_background(des_panel, const.base03)
    tcod.console_clear(des_panel)

    # log console
    log_panel = tcod.console.Console(log_width, log_height)
    tcod.console_set_default_background(log_panel, const.base03)
    tcod.console_clear(log_panel)

    # popup console
    popup_panel = tcod.console.Console(popup_width, popup_height)
    tcod.console_set_default_background(popup_panel, const.base03)
    tcod.console_clear(popup_panel)

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
    turns.add_turn(0, const.TurnType.MSG, log.Msg("They say the hardest part is actually choosing to make a game. So I guess I've already won?", const.desat_green))
    turns.add_turn(3600*24, const.TurnType.MSG, log.Msg("You have 6 days left.", const.desat_green))
    turns.add_turn(3600*24*2, const.TurnType.MSG, log.Msg("You have 5 days left. Keep going.", const.desat_green))
    turns.add_turn(3600*24*3, const.TurnType.MSG, log.Msg("You have 4 days left. Remember to sleep correctly.", const.desat_orange))
    turns.add_turn(3600*24*4, const.TurnType.MSG, log.Msg("You have 3 days left. That's less than half a week...", const.desat_orange))
    turns.add_turn(3600*24*5, const.TurnType.MSG, log.Msg("You have 2 days left. Don't panic.", const.desat_orange))
    turns.add_turn(3600*24*6, const.TurnType.MSG, log.Msg("You have 1 day left. OK, maybe it's time to panic.", const.desat_red))
    turns.add_turn(3600*24*6.5, const.TurnType.MSG, log.Msg("Only 12 hours left! You need to finish this now!", const.desat_red))
    turns.add_turn(3600*24*7 - 3600, const.TurnType.MSG, log.Msg("1 hour left! Quick!", const.desat_red))
    turns.add_turn(0, const.TurnType.PLAYER, player)
    turns.add_turn(3600*24*7, const.TurnType.GAME_OVER, None)
    i = 0
    for fslot in const.FeatureSlot:
        turns.add_turn(int(i), const.TurnType.SPAWN, fslot)
        i += const.spawn_interval/len(const.FeatureSlot)

    # map generation
    game_map = gmap.GameMap(map_width, map_height, con)
    # game_map.make_boss_map(turns, entities, player)
    game_map.make_map_bsp(turns, entities, player)

    # log init
    msglog = log.Log(log_width - 2, log_height - 2)

    # Splash
    img = tcod.image_load(resource_path("splash.png"))
    img.blit_2x(root_console, 0, 0)
    tcod.console_print_ex(root_console, 75, 10, tcod.BKGND_NONE, tcod.CENTER, "Press any key to create your\nfirst 7DRL game!")
    tcod.console_print_ex(root_console, 50, 47, tcod.BKGND_NONE, tcod.CENTER, "A cheap plastic imitation of a game dev, 2019")
    tcod.console_flush()

    again = True
    while again:
        for event in tcod.event.wait():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN" or event.type == "MOUSEBUTTONDOWN":
                again = False

    first_feature = random_loot.get_random_feature(turns, player)
    key = player.add_to_inventory(first_feature)
    # player.fequip(first_feature, key)

    first_weapon = None
    while first_weapon == None:
        first_weapon = random_loot.get_random_weapon(turns, player)
        # the player should not begin with a hack
        if first_weapon.wslot.value.get("instable"):
            first_weapon = None

    key = player.add_to_inventory(first_weapon)
    # player.wequip(first_weapon, key)

    menu_state = const.MenuState.STANDARD

    # initial render
    render.render_map(root_console, con, entities, player, game_map, screen_width, screen_height)
    render.render_log(root_console, log_panel, msglog, map_height)
    render.render_des(root_console, des_panel, map_height, "")
    render.render_sch(root_console, sch_panel, turns, map_width)
    render.render_inv(root_console, inv_panel, player, map_width, sch_height)
    menu_state = const.MenuState.POPUP
    render.render_popup(root_console, popup_panel, map_width, map_height, const.intro_strings)


    tcod.console_flush()
    fov_recompute = False
    render_inv = False
    force_log = False
    time_malus = 0
    new_turn = True
    enemy_moved = False
    last_player_date = 0
    mouse = (500,500) #OOB
    new_mouse = False
    boss = None
    while not tcod.console_is_window_closed():
        if new_turn:

            assert turns.nb_turns(const.TurnType.PLAYER) == 1, turns.nb_turns(const.TurnType.PLAYER)
            assert turns.nb_turns(const.TurnType.SPAWN) == 5, turns.nb_turns(const.TurnType.SPAWN)
            assert turns.nb_turns(const.TurnType.ENNEMY) == len([e for e in entities if isinstance(e, entity.Monster)]),(turns.nb_turns(const.TurnType.ENNEMY),len([e for e in entities if isinstance(e, entity.Monster)]),entities,turns.turns)

            current_turn = turns.get_turn()

            render.render_sch(root_console, sch_panel, turns, map_width)
            new_turn = False
            if current_turn.ttype == const.TurnType.PLAYER and time_malus > 0:
                msglog.add_log("You lose "+str(time_malus)+"s!")

        tcod.console_flush()
        if current_turn.ttype == const.TurnType.PLAYER:
            delta_time = int((turns.current_date - last_player_date) / 60)
            ticktock = ""
            if delta_time >= 10:
                msglog.add_log("Tick... Tock...")
            last_player_date = turns.current_date
            if fov_recompute:
                game_map.recompute_fov(player.x, player.y)
                for e in entities:
                    if not e.is_seen and game_map.is_visible(e.x, e.y):
                        e.is_seen = True
                        # if isinstance(e, entity.Monster):
            if fov_recompute or enemy_moved:
                new_mouse = True
                render.render_map(root_console, con, entities, player, game_map, screen_width, screen_height)
                enemy_moved = False

            if new_mouse and not boss:# and menu_state != const.MenuState.POPUP:
                render.render_des(root_console, des_panel, map_height, render.get_names_under_mouse(mouse, entities, game_map, log_width))
                new_mouse = False

            if boss:
                render.render_boss_hp(root_console, des_panel, map_height, boss)

            fov_recompute = False
            render.render_log(root_console, log_panel, msglog, map_height, force_log)
            force_log = False
            if render_inv:
                render.render_inv(root_console, inv_panel, player, map_width, sch_height)
                render_inv = False


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
                elif event.type == "MOUSEMOTION":
                    if event.tile != mouse:
                        mouse = event.tile
                        new_mouse = True
                    continue
                # elif event.type == "MOUSEBUTTONDOWN" and event.button == tcod.event.BUTTON_LEFT:
                #     if menu_state == const.MenuState.STANDARD:
                #         menu_state = const.MenuState.POPUP
                #         render.render_popup(root_console, popup_panel, screen_width, screen_height, ["Test 1","Test 2"])
                else:
                    continue

                if menu_state == const.MenuState.STANDARD:
                    action = keys.handle_player_turn_keys(key, modifiers)
                elif menu_state == const.MenuState.DROP:
                    action = keys.handle_drop_keys(key, modifiers)
                elif menu_state == const.MenuState.EQUIP:
                    action = keys.handle_equip_keys(key, modifiers)
                elif menu_state == const.MenuState.POPUP:
                    action = keys.handle_popup_keys(key, modifiers)
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
                        player.active_weapon.equip_log(msglog)
                        enemy_moved = True
                        render_inv = True
                        turns.add_turn(time_malus + const.time_equip_weapon, const.TurnType.PLAYER, player)
                        time_malus = 0
                        new_turn = True
                        break

                help_popup = action.get('help')
                if help_popup:
                    menu_state = const.MenuState.POPUP
                    render.render_popup(root_console, popup_panel, map_width, map_height, const.help_strings)

                descend = action.get('descend')
                if descend:
                    stairs = game_map.is_stairs(player.x, player.y)
                    boss_stairs = game_map.is_boss_stairs(player.x, player.y)
                    assert not (stairs and boss_stairs)
                    if stairs or boss_stairs:
                        if boss_stairs and not player.can_go_boss():
                            msglog.add_log("You can't release the game yet, you don't have five stable features!")
                        else:
                            msglog.add_log("You go down the stairs.")
                            for e in entities:
                                if isinstance(e, entity.Monster):
                                    e.dead(stabilize=False)
                                    turns.remove_turn(e)
                            entities = [player]
                            if stairs:
                                game_map.make_map_bsp(turns, entities, player)
                            else:
                                boss = game_map.make_boss_map(turns, entities, player)
                                msglog.add_log("To release your game, you need to fight your inner ennemy: self-doubt.", const.red)
                            turns.add_turn(time_malus + const.time_move, const.TurnType.PLAYER, player)
                            time_malus = 0
                            render.render_map(root_console, con, entities, player, game_map, screen_width, screen_height)
                            enemy_moved = True
                            new_turn = True
                            break
                    else:
                        msglog.add_log("You see no stairs.")

                grab = action.get('pickup')
                if grab:
                    if game_map.is_there_item_on_floor(player):
                        if game_map.is_weapon_on_floor_directly_equipable(player):
                            (item,key) = game_map.get_item_on_floor(player, entities)
                            player.wequip(item, key)
                            msglog.add_log("You equip a "+item.name+".")
                            render_inv = True
                        elif player.is_inventory_full():
                            msglog.add_log("Your inventory is full.")
                            assert not render_inv
                        else:
                            item,_ = game_map.get_item_on_floor(player, entities)
                            msglog.add_log("You pick up a "+item.name+".")
                            render_inv = True
                        if render_inv:
                            if isinstance(item, entity.Weapon):
                                l = item.wego.value.get("fego")
                                msglog.add_log("It is effective against "+l[0].value.get("name")+", "+l[1].value.get("name")+" and "+l[2].value.get("name")+" bugs.")
                            elif isinstance(item, entity.Feature):
                                wego = [wego for wego in const.WeaponEgo if item.fego in wego.value.get("fego")]
                                assert len(wego) == 1
                                wego = wego[0]
                                msglog.add_log("Its bugs are squashed by "+wego.value.get("name")+" weapons.")
                            else:
                                assert False
                            render_inv = True
                    else:
                        msglog.add_log("There is nothing on the floor to pick up.")

                drop = action.get('drop')
                if drop:
                    if player.is_inventory_empty():
                        msglog.add_log("Your inventory is empty.")
                    elif game_map.is_there_item_on_floor(player):
                        msglog.add_log("There is already something there.")
                    else:
                        msglog.add_log("What do you want to drop? [abcde]")
                        menu_state = const.MenuState.DROP

                equip = action.get('equip')
                if equip:
                    if player.is_inventory_empty():
                        msglog.add_log("Your inventory is empty.")
                    else:
                        msglog.add_log("What do you want to equip? [abcde]")
                        menu_state = const.MenuState.EQUIP

                drop_unknow = action.get('drop_unknow')
                if drop_unknow:
                    msglog.add_log("What do you want to drop? [abcde]")

                equip_unknow = action.get('equip_unknow')
                if equip_unknow:
                    msglog.add_log("What do you want to equip? [abcde]")

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
                        menu_state = const.MenuState.STANDARD
                        previous_active = player.active_weapon
                        if isinstance(item, entity.Feature):
                            out = player.fequip(item, equip_key)
                            synergy = out.get("synergy")
                            if synergy:
                                if synergy == 2:
                                    msglog.add_log("You feel a small synergy between your two "+item.fego.value.get("name")+" features.", color_active=const.green)
                                elif synergy == 3:
                                    msglog.add_log("You feel a good synergy between your three "+item.fego.value.get("name")+" features.", color_active=const.green)
                                elif synergy == 4:
                                    msglog.add_log("You feel a great synergy between your four "+item.fego.value.get("name")+" features!", color_active=const.green)
                                elif synergy == 5:
                                    msglog.add_log("You feel an insane synergy between your five "+item.fego.value.get("name")+" features!", color_active=const.green)
                                else:
                                    assert False

                        elif isinstance(item, entity.Weapon):
                            out = player.wequip(item, equip_key)
                            enemy_moved = True # update telepathy
                        else:
                            assert False
                        previous = out.get("unstable-previous")
                        level_problem_no_previous = out.get("level-problem-no-previous")
                        level_problem_previous = out.get("level-problem-previous")
                        inheritance = out.get("inheritance")
                        if inheritance:
                            msglog.add_log("You upgraded your "+item.fego.value.get("name")+" "+item.fslot.value.get("name")+": it is already quite stable!", color_active=const.green)
                            item.stability = max(item.stability, inheritance.stability)
                            render_inv = True
                            turns.add_turn(time_malus + const.time_equip, const.TurnType.PLAYER, player)
                            time_malus = 0
                            new_turn = True
                            break
                        elif level_problem_previous:
                            msglog.add_log("You can't equip a v"+str(item.level)+" feature on a v"+str(level_problem_previous.level)+" feature.")
                        elif level_problem_no_previous:
                            msglog.add_log("You need to equip a v1 "+item.fslot.value.get("name")+" feature first.")
                        elif not previous:
                            msglog.add_log("You equip a "+item.name+".")
                            if isinstance(item, entity.Weapon):
                                msglog.add_log("You can change your active weapon with [123].")
                                if not previous_active:
                                    enemy_moved = True
                                    player.active_weapon.equip_log(msglog)
                            render_inv = True
                            turns.add_turn(time_malus + const.time_equip, const.TurnType.PLAYER, player)
                            time_malus = 0
                            new_turn = True
                            break
                        else:
                            msglog.add_log("You try to equip the "+item.name+" but your "+previous.name+" is too unstable to be removed!")

                    else:
                        msglog.add_log("You don't have this item!")
                        menu_state = const.MenuState.STANDARD



                cancel = action.get('cancel')
                if cancel:
                    if menu_state == const.MenuState.POPUP:
                        render.render_map(root_console, con, entities, player, game_map, screen_width, screen_height)
                        render.render_log(root_console, log_panel, msglog, map_height)
                        if boss:
                            render.render_boss_hp(root_console, des_panel, map_height, boss)
                        else:
                            render.render_des(root_console, des_panel, map_height, "")
                        render.render_sch(root_console, sch_panel, turns, map_width)
                        render.render_inv(root_console, inv_panel, player, map_width, sch_height)
                    else:
                        msglog.add_log("Nevermind.")
                    menu_state = const.MenuState.STANDARD


                move = action.get('move')
                if move:
                    dx, dy = move

                    if (dx, dy) == (0, 0):
                        msglog.add_log("There is no time to lose!")
                        turns.add_turn(time_malus + const.time_move, const.TurnType.PLAYER, player)
                        time_malus = 0
                        new_turn = True
                        force_log = True
                        break
                    else:
                        destination_x = player.x + dx
                        destination_y = player.y + dy

                        target = entity.get_blocking_entities_at_location(entities, destination_x, destination_y)

                        if target and target != player:
                            weapon = player.active_weapon
                            if not weapon:
                                msglog.add_log("You have no weapon to attack with! Equip with w.")
                            else:
                                if target == boss and weapon.wslot.value.get("instable"):
                                    msglog.add_log("Your hack has no effect on "+boss.name)
                                    duration = weapon.duration
                                else:
                                    duration = attack(weapon, target, msglog, player, entities, turns)
                                    render_inv = True
                                turns.add_turn(time_malus + duration, const.TurnType.PLAYER, player)
                                time_malus = 0
                                new_turn = True
                                enemy_moved = True
                                break
                        elif not game_map.is_blocked(destination_x, destination_y):
                            player.move(dx, dy)
                            des = game_map.description_item_on_floor(player)
                            if des:
                                msglog.add_log("You see a "+des+" on the floor.")
                            turns.add_turn(time_malus + const.time_move, const.TurnType.PLAYER, player)
                            time_malus = 0
                            fov_recompute = True
                            new_turn = True
                            force_log = True
                            break

        elif current_turn.ttype == const.TurnType.ENNEMY:
            e = current_turn.entity
            assert e.hp > 0, e.hp
            if e in entities:
                if e.distance_to(player) >= 2:
                    e.move_astar(player, entities, game_map)
                    if game_map.is_visible(e.x, e.y) or (player.active_weapon and isinstance(player.active_weapon, entity.ConsciousWeapon)):
                        enemy_moved = True
                    turns.add_turn(e.speed_mov, const.TurnType.ENNEMY, e)
                else:
                    turns.add_turn(e.speed_atk, const.TurnType.ENNEMY, e)
                    d = e.attack(player, turns)
                    delta_malus = d.get("dmg")
                    invok = d.get("invok")
                    if invok:
                        msglog.add_log(e.name+" invoks "+invok.value.get("name")+" bugs!")
                        for level in range(1,4):
                            nb = const.boss_level_invok[level-1]
                            for n in range(nb):
                                new_e = game_map.spawn_boss(entities, invok, level)
                                if new_e:
                                    turns.add_turn(e.speed_mov, const.TurnType.ENNEMY, new_e)
                    elif delta_malus:
                        time_malus += delta_malus
                        if time_malus > const.malus_max:
                            time_malus = const.malus_max
                    else:
                        if player.active_weapon and isinstance(player.active_weapon, entity.BasicWeapon) and random.randint(1,3) == 1:
                            msglog.add_log("The "+e.name+" is burned by your caustic and "+player.active_weapon.name+"!")
                            attack(player.active_weapon, e, msglog, player, entities, turns, log_effective=False)
                            render_inv = True
                        # msglog.add_log("The "+e.name+" misses.")
            new_turn = True

        elif current_turn.ttype == const.TurnType.SPAWN:
            if not boss:
                creator = player.fequiped.get(current_turn.entity)
                if creator and not creator.is_stable() and sum(creator.n_bugs) < sum(creator.n_bugs_max):
                    chance = 1 - creator.stability / creator.max_stability / const.stability_threshold + 0.4
                    if random.random() < chance:
                        e = game_map.spawn(entities, creator)
                        if e:
                            turns.add_turn(e.speed_mov, const.TurnType.ENNEMY, e)
            turns.add_turn(const.spawn_interval, const.TurnType.SPAWN, current_turn.entity)
            new_turn = True

        elif current_turn.ttype == const.TurnType.MSG:
            msglog.add_log(current_turn.entity.string, current_turn.entity.color_active, current_turn.entity.color_inactive)
            new_turn = True

        elif current_turn.ttype == const.TurnType.GAME_OVER:
            msglog.add_log("Your self-doubt is too strong. You don't feel your game is worth showing to the world. Who said releasing a game was easy?", const.red, const.red)
            msglog.add_log("Game over.", const.red, const.red)
            render.render_log(root_console, log_panel, msglog, map_height)
            tcod.console_flush()
            break

        elif current_turn.ttype == const.TurnType.WIN:
            msglog.add_log("Congratulations! You defeated your self-doubt and completed your game!", const.green)
            msglog.add_log("You ascend to the status of RL game dev...", const.green)
            render.render_log(root_console, log_panel, msglog, map_height)
            tcod.console_flush()
            break

        if boss and boss.hp <= 0:
            render.render_boss_hp(root_console, des_panel, map_height, boss)
            turns.turns = []
            turns.add_turn(0, const.TurnType.WIN, None)

    time.sleep(3)
    for event in tcod.event.wait():
        pass
    again = True
    while again:
        for event in tcod.event.wait():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN" or event.type == "MOUSEBUTTONDOWN":
                again = False
            tcod.console_flush()


def attack(weapon, target, msglog, player, entities, turns, log_effective=True):
    (dmg,duration) = weapon.attack(target, msglog, turns)
    if weapon.wslot.value.get("instable"):
        if random.randint(1,2) == 0:
            msglog.add_log("Your "+target.fcreator.name+" is less stable!")
            target.fcreator.destabilize(target.stability_reward)
        player.update_resistance()
    if target.hp <= 0:
        enemy_moved = True
        if log_effective and weapon.is_effective_on(target.fslot):
            msglog.add_log("You squashed the "+target.name+"!")
        more_stable = target.dead()
        entities.remove(target)
        turns.remove_turn(target)
        player.update_resistance()
        # if more_stable:
            # msglog.add_log("Your "+target.fcreator.name+" is more stable.")
    return duration

def resource_path(relative):
    try:
        # in pyinstaller
        return os.path.join(sys._MEIPASS,relative)
    except AttributeError:
        # locally
        return relative

if __name__ == '__main__':
    main()
