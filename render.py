import tcod as tcod

import constants as const
from enum import Enum
import entity
import math
import textwrap

def render_map(root_console, con, entities, player, game_map, fov_recompute, screen_width, screen_height):
    """
    Render the map
    """
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

def render_log(root_console, log_panel, msglog, map_height):
    """
    Render the bottom panel (log)
    """
    tcod.console_clear(log_panel)
    tcod.console_set_default_foreground(log_panel, const.base0)
    log_panel.print_frame(0, 1, log_panel.width, log_panel.height-1, string="Log")
    y = log_panel.height - 3 - len(msglog.messages)
    for msg in msglog.messages:
        if y >= msglog.last:
            tcod.console_set_default_foreground(log_panel, const.base2)
        log_panel.print(1, y + 2, msg)
        y += 1
    msglog.set_rendered()
    log_panel.blit(dest=root_console, dest_y=map_height)

def render_feature(inv_panel, feature, default_fore, y):
    max_stab_width = 10
    start_stab = inv_panel.width - 1 - max_stab_width

    tcod.console_set_default_foreground(inv_panel, default_fore)
    tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, feature.fego.value.get("name"))
    y += 1
    tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, feature.fslot.value.get("name")+" v"+str(feature.level))

    tcod.console_set_default_foreground(inv_panel, const.base3)
    stable = (feature.stability / feature.max_stability) >= const.stability_threshold
    if stable:
        tcod.console_print_ex(inv_panel, start_stab, y, tcod.BKGND_NONE, tcod.LEFT, "Stable")
    else:
        tcod.console_print_ex(inv_panel, start_stab, y, tcod.BKGND_NONE, tcod.LEFT, "Unstable")
    stab_width = round(feature.stability / feature.max_stability * max_stab_width)
    for x in range(start_stab, start_stab + stab_width):
        tcod.console_set_char_background(inv_panel, x, y, const.green if stable else const.red, tcod.BKGND_SET)
    for x in range(start_stab + stab_width, start_stab + max_stab_width):
        tcod.console_set_char_background(inv_panel, x, y, const.base02, tcod.BKGND_SET)

def render_weapon(inv_panel, weapon, default_fore, y, active_weapon):
    x = len(weapon.wego.value.get("name")) + 4
    for fslot in weapon.fslot_effective:
        # tcod.console_set_char_background(inv_panel, x, y, fslot.value.get("color"), tcod.BKGND_SET)
        tcod.console_set_default_foreground(inv_panel, fslot.value.get("color"))
        tcod.console_put_char(inv_panel, x, y, "!", tcod.BKGND_NONE)
        x += 1
    tcod.console_set_default_foreground(inv_panel, default_fore)
    if active_weapon:
        tcod.console_set_default_foreground(inv_panel, const.base2)
    else:
        tcod.console_set_default_foreground(inv_panel, default_fore)
    tcod.console_print_ex(inv_panel, 1, y, tcod.BKGND_NONE, tcod.LEFT, weapon.wslot.value.get("key")+" "+weapon.wego.value.get("name"))
    y += 1
    tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, weapon.wslot.value.get("name")+" v"+str(weapon.level))
    string = weapon.stat_string()
    tcod.console_print_ex(inv_panel, inv_panel.width-1, y, tcod.BKGND_NONE, tcod.RIGHT, string)


def render_inv(root_console, inv_panel, player, map_width):
    """
    Render the right panel (time, features, weapons, inventory)
    """
    tcod.console_clear(inv_panel)
    default_fore = const.base0
    tcod.console_set_default_foreground(inv_panel, default_fore)
    w = inv_panel.width

    # Time
    y = 0
    inv_panel.print_frame(0, y, w, 3, string="Time")
    tcod.console_set_default_foreground(inv_panel, const.red)
    inv_panel.print(int(w / 2), y + 1, "TODO", alignment=tcod.CENTER)

    # Features
    y = 3
    tcod.console_set_default_foreground(inv_panel, default_fore)
    inv_panel.print_frame(0, y, w, 5 * 3 + 1, string="Features")
    for fslot in const.FeatureSlot:
        y += 1
        feature = player.fequiped.get(fslot)
        tcod.console_set_char_background(inv_panel, 1, y, fslot.value.get("color"), tcod.BKGND_SET)
        if feature:
            render_feature(inv_panel, feature, default_fore, y)
            y += 1
        else:
            tcod.console_set_default_foreground(inv_panel, const.base02)
            tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, "(none)")
            y += 1
            tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, fslot.value.get("name"))

    y += 1

    y += 1
    tcod.console_set_default_foreground(inv_panel, default_fore)

    inv_panel.print_frame(0, y, w, 3, string="Resistance")
    y += 1
    x = 2
    for fslot in const.FeatureSlot:
        tcod.console_set_char_background(inv_panel, x, y, fslot.value.get("color"), tcod.BKGND_SET)
        x += 1
        tcod.console_print_ex(inv_panel, x, y, tcod.BKGND_NONE, tcod.LEFT, ":"+str(player.resistances.get(fslot)))
        x += 4

    tcod.console_set_default_foreground(inv_panel, default_fore)
    y += 2
    inv_panel.print_frame(0, y, w, 3 * 3 + 1, string="Weapons")

    for wslot in const.WeaponSlot:
        y += 1
        weapon = player.wequiped.get(wslot)
        if weapon:
            render_weapon(inv_panel, weapon, default_fore, y, weapon == player.active_weapon)
            y += 1
        else:
            tcod.console_set_default_foreground(inv_panel, const.base02)
            tcod.console_print_ex(inv_panel, 1, y, tcod.BKGND_NONE, tcod.LEFT, wslot.value.get("key")+" (none)")
            y += 1
            tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, wslot.value.get("name"))
            string = str(round(wslot.value.get("success_rate_base") * 100))+"% "+str(wslot.value.get("duration_base"))+"mn"
            if wslot.value.get("instable"):
                string = "Stab- "+string
            tcod.console_print_ex(inv_panel, w-1, y, tcod.BKGND_NONE, tcod.RIGHT, string)
        y += 1

    y += 1

    tcod.console_set_default_foreground(inv_panel, default_fore)
    inv_panel.print_frame(0, y, w, 5*3+1, string="Inventory")

    for k in player.inventory:
        y += 1
        item = player.inventory.get(k)
        if item:
            if isinstance(item, entity.Weapon):
                render_weapon(inv_panel, item, default_fore, y, False)
                tcod.console_put_char(inv_panel, 1, y, k, tcod.BKGND_NONE)
            else:
                render_feature(inv_panel, item, default_fore, y)
            tcod.console_set_default_foreground(inv_panel, default_fore)
            tcod.console_put_char(inv_panel, 1, y, k, tcod.BKGND_NONE)
        else:
            tcod.console_set_default_foreground(inv_panel, const.base02)
            tcod.console_print_ex(inv_panel, 1, y, tcod.BKGND_NONE, tcod.LEFT, k+" (none)")
        y += 2

    inv_panel.blit(dest=root_console, dest_x=map_width)



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
