import tcod as tcod

import constants as const
from enum import Enum
import entity
import math
import textwrap

def render_all(root_console, con, entities, player, game_map, fov_recompute, screen_width, screen_height):
    if fov_recompute:
        game_map.recompute_fov(player.x, player.y)
    # Draw all the tiles in the game map
        for y in range(game_map.height):
            for x in range(game_map.width):
                clear_cell(con, x, y, game_map)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(con, entity, game_map)

    con.blit(dest=root_console)

def render_description(root_console, mouse, panel, entities, game_map, screen_width, panel_height, panel_y):
    tcod.console_set_default_foreground(panel, tcod.light_gray)
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT,
                             get_names_under_mouse(mouse, entities, game_map,screen_width))
    panel.blit(dest=root_console, width=screen_width, height=panel_height, dest_y=panel_y)

def clear_all_entities(con, entities,game_map):
    for entity in entities:
        clear_cell(con, entity.x,entity.y,game_map)

def draw_entity(con, entity, game_map):
    if game_map.is_visible(entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

def clear_cell(con, x,y,game_map):
    wall = game_map.is_blocked(x,y)
    door = game_map.is_door(x,y)
    visible = game_map.is_visible(x,y)

    if visible:
        game_map.tiles[x][y].is_seen = True

    if game_map.tiles[x][y].is_seen:
        if visible:
            tcod.console_set_char_foreground(con, x, y, game_map.tiles[x][y].visible_color)
        else:
            tcod.console_set_char_foreground(con, x, y, game_map.tiles[x][y].hidden_color)
        tcod.console_set_char(con, x, y, game_map.tiles[x][y].char)
    else:
        tcod.console_set_char(con, x, y, ' ')
