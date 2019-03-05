import tcod as tcod

import constants as const
from enum import Enum
import entity as ent
import math
import textwrap

def render_map(root_console, con, entities, player, game_map, screen_width, screen_height):
    """
    Render the map
    """
    # Draw all the tiles in the game map
    for y in range(game_map.height):
        for x in range(game_map.width):
            clear_cell(con, x, y, game_map)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(con, entity, game_map, player)

    con.blit(dest=root_console)

def render_popup(root_console, popup_panel, map_width, map_height, strings):
    tcod.console_clear(popup_panel)
    tcod.console_set_default_foreground(popup_panel, const.base2)
    popup_panel.print_frame(0, 0, popup_panel.width, popup_panel.height)
    y = int(popup_panel.height /2 - len(strings) / 2)
    for s in strings:
        tcod.console_print_ex(popup_panel, int(popup_panel.width / 2), y, tcod.BKGND_NONE, tcod.CENTER, s)
        y += 1
    popup_panel.blit(dest=root_console, dest_x = int(map_width/6), dest_y=int(map_height/6), bg_alpha=0.8)

def render_boss_hp(root_console, des_panel, map_height, boss):
    """
    render the boss hp bar
    """
    tcod.console_set_default_foreground(des_panel, const.base3)
    tcod.console_print_ex(des_panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, boss.name)
    x_start = 1
    x_width = des_panel.width - 2
    hp_width = round((boss.hp / boss.max_hp * x_width))

    for x in range(x_start, x_start+x_width):
        tcod.console_set_char_background(des_panel, x, 0, const.base02, tcod.BKGND_SET)
    for x in range(x_start, x_start + hp_width):
        tcod.console_set_char_background(des_panel, x, 0, const.red, tcod.BKGND_SET)

    des_panel.blit(dest=root_console, dest_y=map_height)

def render_des(root_console, des_panel, map_height, string):
    tcod.console_set_default_foreground(des_panel, const.base2)
    tcod.console_print_ex(des_panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, string)
    des_panel.blit(dest=root_console, dest_y=map_height)

def render_log(root_console, log_panel, msglog, map_height, force=False):
    """
    Render the bottom panel (log)
    """
    if force or msglog.is_there_new():
        tcod.console_clear(log_panel)
        tcod.console_set_default_foreground(log_panel, const.base0)
        log_panel.print_frame(0, 0, log_panel.width, log_panel.height, string="Log")
        y = log_panel.height - 2 - len(msglog.messages)
        for msg in msglog.messages:
            if y >= msglog.last:
                tcod.console_set_default_foreground(log_panel, msg.color_active)
            else:
                tcod.console_set_default_foreground(log_panel, msg.color_inactive)
            log_panel.print_(1, y + 1, msg.string)
            y += 1
        msglog.set_rendered()
        log_panel.blit(dest=root_console, dest_y=map_height + 1)

def render_feature(inv_panel, feature, default_fore, y, player):
    max_stab_width = 10
    start_stab = inv_panel.width - 1 - max_stab_width

    tcod.console_set_default_foreground(inv_panel, default_fore)
    effective_string = ""
    if feature.is_in_inventory:
        for wslot in player.wequiped:
            weapon = player.wequiped.get(wslot)
            if weapon and weapon.is_effective_on_fego(feature.fego):
                effective_string = " *"
                break

    tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, feature.fego.value.get("name") + effective_string)
    y += 1
    tcod.console_print_ex(inv_panel, 3, y, tcod.BKGND_NONE, tcod.LEFT, feature.fslot.value.get("name") + " v" + str(feature.level))

    tcod.console_set_default_foreground(inv_panel, const.base3)
    stable = feature.is_stable()
    if stable:
        tcod.console_print_ex(inv_panel, start_stab, y, tcod.BKGND_NONE, tcod.LEFT, "Stable")
    else:
        tcod.console_print_ex(inv_panel, start_stab, y, tcod.BKGND_NONE, tcod.LEFT, "Unstable")
    stab_width = round(feature.stability / feature.max_stability * max_stab_width)
    if stable:
        color = const.green
    else:
        color = const.green*(feature.stability/feature.max_stability/const.stability_threshold) + const.red*(1 - feature.stability/feature.max_stability/const.stability_threshold)
    for x in range(start_stab, start_stab + stab_width):
        tcod.console_set_char_background(inv_panel, x, y, color, tcod.BKGND_SET)
    for x in range(start_stab + stab_width, start_stab + max_stab_width):
        tcod.console_set_char_background(inv_panel, x, y, const.base02, tcod.BKGND_SET)

def render_weapon(inv_panel, weapon, default_fore, y, active_weapon):
    x = len(weapon.wego.value.get("name")) + 4
    for fslot in weapon.fslot_effective:
        # tcod.console_set_char_background(inv_panel, x, y, fslot.value.get("color"), tcod.BKGND_SET)
        tcod.console_set_default_foreground(inv_panel, fslot.value.get("color"))
        tcod.console_put_char(inv_panel, x, y, "*", tcod.BKGND_NONE)
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

def render_sch(root_console, sch_panel, turns, map_width):
    # Time
    (remaining_d, remaining_h, remaining_m, remaining_s) = turns.get_remaining()
    w = sch_panel.width
    tcod.console_set_default_foreground(sch_panel, const.base0)
    sch_panel.print_frame(0, 0, w, 3, string="Remaining time")
    if remaining_d <= 1:
        tcod.console_set_default_foreground(sch_panel, const.red)
    elif remaining_d <= 3:
        tcod.console_set_default_foreground(sch_panel, const.orange)
    sch_panel.print_(int(w / 2), 1, str(remaining_d)+"d "+str(remaining_h)+"h "+str(remaining_m)+"m "+str(remaining_s)+"s", alignment=tcod.CENTER)
    sch_panel.blit(dest=root_console, dest_x=map_width)

def render_inv(root_console, inv_panel, player, map_width, sch_height):
    """
    Render the right panel (time, features, weapons, inventory)
    """
    tcod.console_clear(inv_panel)
    default_fore = const.base0
    tcod.console_set_default_foreground(inv_panel, default_fore)
    w = inv_panel.width

    # Features
    y = 0
    tcod.console_set_default_foreground(inv_panel, default_fore)
    inv_panel.print_frame(0, y, w, 5 * 3 + 1, string="Features")
    for fslot in const.FeatureSlot:
        y += 1
        feature = player.fequiped.get(fslot)
        tcod.console_set_char_background(inv_panel, 1, y, fslot.value.get("color"), tcod.BKGND_SET)
        if feature:
            render_feature(inv_panel, feature, default_fore, y, player)
            y += 2
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
    at_least_one = False
    for fslot in const.FeatureSlot:
        r = player.resistances.get(fslot)
        if r > 0:
            at_least_one = True
            tcod.console_set_char_background(inv_panel, x, y, fslot.value.get("color"), tcod.BKGND_SET)
            x += 1
            tcod.console_print_ex(inv_panel, x, y, tcod.BKGND_NONE, tcod.LEFT, ":"+str(r))
            x += 4
        else:
            x += 5
    if not at_least_one:
        tcod.console_set_default_foreground(inv_panel, const.base02)
        tcod.console_print_ex(inv_panel, int(w / 2), y, tcod.BKGND_NONE, tcod.CENTER, "(none)")

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
            string = str(round(wslot.value.get("success_rate_base") * 100))+"% "+str(wslot.value.get("duration_base"))+"s"
            if wslot.value.get("instable"):
                string = "Stab- "+string
            tcod.console_print_ex(inv_panel, w-1, y, tcod.BKGND_NONE, tcod.RIGHT, string)
        y += 1

    y += 1

    tcod.console_set_default_foreground(inv_panel, default_fore)
    inv_panel.print_frame(0, y, w, 5 * 3 + 1, string="Inventory")

    for k in player.inventory:
        y += 1
        item = player.inventory.get(k)
        if item:
            if isinstance(item, ent.Weapon):
                render_weapon(inv_panel, item, default_fore, y, False)
                tcod.console_put_char(inv_panel, 1, y, k, tcod.BKGND_NONE)
            else:
                render_feature(inv_panel, item, default_fore, y, player)
            tcod.console_set_default_foreground(inv_panel, default_fore)
            tcod.console_put_char(inv_panel, 1, y, k, tcod.BKGND_NONE)
        else:
            tcod.console_set_default_foreground(inv_panel, const.base02)
            tcod.console_print_ex(inv_panel, 1, y, tcod.BKGND_NONE, tcod.LEFT, k+" (none)")
        y += 2

    inv_panel.blit(dest=root_console, dest_x=map_width, dest_y=sch_height)

# def clear_all_entities(con, entities,game_map, player):
    # for entity in entities:
        # clear_cell(con, entity.x,entity.y,game_map,player)

def draw_entity(con, entity, game_map, player):
    visible = game_map.is_visible(entity.x, entity.y)
    if visible\
    or (entity.is_seen and (isinstance(entity, ent.Weapon) or isinstance(entity, ent.Feature)))\
    or (isinstance(entity, ent.Monster) and isinstance(player.active_weapon, ent.ConsciousWeapon)):
        if visible:
            tcod.console_set_char_foreground(con, entity.x, entity.y, entity.visible_color)
        else:
            tcod.console_set_char_foreground(con, entity.x, entity.y, entity.hidden_color)
        tcod.console_set_char(con, entity.x, entity.y, entity.char)

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

def get_object_under_mouse(mouse, entities, game_map, screen_width): # TODO
    (x, y) = mouse
    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and game_map.is_visible(entity.x, entity.y)]

    names = ', '.join(names)
    # space padding to remove the precedent description
    names = names.ljust(screen_width, ' ')

    return names.capitalize()

def get_names_under_mouse(mouse, entities, game_map, screen_width):
    (x, y) = mouse
    if game_map.is_over_map(x,y) and game_map.is_visible(x,y):
        entities_in_render_order = sorted([entity for entity in entities
                if entity.x == x and entity.y == y], key=lambda x: x.render_order.value, reverse=True)
        names = [e.name for e in entities_in_render_order]
        string = game_map.tiles[x][y].name
        if string:
            names.append(string)
        names = ', over a '.join(names)
        # space padding to remove the precedent description
        names = names.ljust(screen_width, ' ')

        return  "%s%s" % (names[0].upper(), names[1:]) # fist letter in capital
    else:
        return "".ljust(screen_width, ' ')
