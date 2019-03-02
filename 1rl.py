import tcod
import entity
import constants as const
import game_map as gmap
import time
import render
import log

def main():
    screen_width = 100
    screen_height = 48

    # Log
    log_height = 12
    log_width = screen_width

    # Size of the map
    map_width = screen_width
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

    # map generation
    game_map = gmap.GameMap(map_width, map_height, con)
    game_map.make_map_bsp(player)

    # log init
    msglog = log.Log(log_width - 2, log_height - 3)
    msglog.add_log("Test 1")
    msglog.add_log("Test 2")
    msglog.set_rendered()
    msglog.add_log("Test 3")
    msglog.add_log("Test 4")
    feature_test = entity.Feature(const.FeatureSlot.p, const.FeatureEgo.c3, 1, 2)
    for i in range(20):
        game_map.spawn(entities, feature_test)

    # initial render
    fov_recompute = True
    render.render_map(root_console, con, entities, player, game_map, fov_recompute, screen_width, screen_height)
    render.render_log(root_console, log_panel, msglog, map_height)
    tcod.console_flush()

    time.sleep(2)
    tcod.console_flush()
    time.sleep(2)

if __name__ == '__main__':
    main()
