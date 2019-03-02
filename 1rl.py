import tcod
import entity
import constants as const
import game_map as gmap
import time
import render
import log
import scheduling as sch

def main():
    screen_width = 100
    screen_height = 44

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
    turns.add_turn(sch.Turn(0, const.TurnType.PLAYER, player))

    t = turns.get_turn()
    print(t.ttype)

    # map generation
    game_map = gmap.GameMap(map_width, map_height, con)
    game_map.make_map_bsp(player)

    # log init
    msglog = log.Log(log_width - 2, log_height - 3)

    # Test
    msglog.add_log("Test 1")
    msglog.add_log("Test 2")
    msglog.set_rendered()
    msglog.add_log("Test 3")
    msglog.add_log("Test 4")
    feature_test1 = entity.Feature(const.FeatureSlot.p, const.FeatureEgo.c3, 1, 2, 3)
    feature_test2 = entity.Feature(const.FeatureSlot.l, const.FeatureEgo.p3, 2, 6, 7)
    player.fequip(feature_test1)
    player.fequip(feature_test1)
    player.fequip(feature_test2)
    player.add_to_inventory(feature_test1)
    player.add_to_inventory(feature_test2)

    weapon_test1 = entity.Weapon(const.WeaponSlot.slow, 0.7, 5, const.WeaponEgo.c, 2)
    weapon_test2 = entity.Weapon(const.WeaponSlot.hack, 0.7, 5, const.WeaponEgo.m, 2)
    player.wequip(weapon_test1)
    player.wequip(weapon_test2)
    player.add_to_inventory(weapon_test1)
    player.add_to_inventory(weapon_test2)

    for i in range(20):
        game_map.spawn(entities, feature_test1)

    # initial render
    fov_recompute = True
    render.render_map(root_console, con, entities, player, game_map, fov_recompute, screen_width, screen_height)
    render.render_log(root_console, log_panel, msglog, map_height)
    render.render_sch(root_console, sch_panel, turns, map_width)
    render.render_inv(root_console, inv_panel, player, map_width, sch_height)
    tcod.console_flush()

    time.sleep(2)
    tcod.console_flush()
    time.sleep(2)

if __name__ == '__main__':
    main()
