from rich.table import Table
from rich import box
from itertools import chain
from ffx_search_tool.src.utilities.filter_monsters import filter_monsters
from ffx_search_tool.src.data import monsters, monster_arena, remiem_temple
from ffx_search_tool.src.utilities.constants import DUPLICATES, SYNONYMS, LOCATIONS, CELL_NAMES, TABLE_WIDTH
from ffx_search_tool.src.utilities.format_monster_data import format_monster_data
from ffx_search_tool.src.utilities.misc import initialize_table, console, make_selection, format_num
from ffx_search_tool.src.utilities.ronso_calc import *



def monster_search(monster_name, single=False):
    if monster_name in SYNONYMS:
        monster_name = SYNONYMS[monster_name][0]
    
    if monster_name in DUPLICATES:
        options = DUPLICATES[monster_name]
        choice = make_selection(options, "Multiple options found.", "Choose a monster by number: ")
        monster_name = options[choice]

    if monster_name not in monsters:
        location_choice = location = make_selection(LOCATIONS, "Monster not found.", "Choose a location by number to display options: ")
        location = LOCATIONS[location_choice]

        options = list(chain(*filter_monsters(location, "location")))
        monster_choice = make_selection(options, None, "Now choose a monster by number: ")
        monster_name = options[monster_choice]
    
    monster = monsters[monster_name]
    
    if monster["has_allies"] and not single:
        get_ally_tables(monster_name)
    else:
        get_monster_table(monster_name)



def get_monster_table(monster_name, kimahri_hp=0, kimahri_str=0, kimahri_mag=0, kimahri_agl=0):
    monster = monsters[monster_name]
    title = get_monster_table_title(monster_name)

    table = Table(pad_edge=False, box=box.MINIMAL_HEAVY_HEAD, width=TABLE_WIDTH, padding=1)
    table.add_column(title)
    table.add_row(get_stat_table(monster_name, kimahri_hp, kimahri_str, kimahri_mag, kimahri_agl))
    table.add_row(get_element_table(monster_name))
    table.add_row(get_status_resist_table(monster_name))
    table.add_row(get_item_table(monster_name))

    if monster["items"]["bribe"] is not None:
        table.add_row(get_bribe_table(monster_name))

    if monster["equipment"]["drop_rate"] != 0:
        table.add_row(get_equipment_table(monster_name))

    if monster_name in monster_arena:
        table.add_row(get_arena_table(monster_name))

    if monster_name in remiem_temple:
        table.add_row(get_remiem_table(monster_name))

    console.print(table)


def get_monster_table_title(monster_name):
    monster = monsters[monster_name]
    locations = ", ".join(monster["location"]).title()
    title = f"{monster_name.title()} - {locations}"

    if monster["is_catchable"]:
        title += " - Can be captured"

    return title


def get_ally_tables(monster_name):
    monster = monsters[monster_name]
    allies = monster["allies"]
    monster_in_multiple_fights = isinstance(allies[0], list)

    if monster_in_multiple_fights:
        choice = make_selection(allies, "Monster appears in multiple boss fights.", "Specify the fight by number: ")
        monster_search(allies[choice][0])
        return
        
    if monster_name == "biran ronso" or monster_name == "yenke ronso":
        kimahri_hp, kimahri_str, kimahri_mag, kimahri_agl = get_kimahri_stats()

    for ally in allies:
        if monster_name == "biran ronso" or monster_name == "yenke ronso":
            get_monster_table(ally, kimahri_hp=kimahri_hp, kimahri_str=kimahri_str, kimahri_mag=kimahri_mag, kimahri_agl=kimahri_agl)
        else:
            get_monster_table(ally)



def get_stat_table(monster_name, kimahri_hp, kimahri_str, kimahri_mag, kimahri_agl):
    monster = monsters[monster_name]
    stats = monster.copy()["stats"]
    stat_keys = list(stats.keys())
    stat_cell_names = CELL_NAMES["stats"]

    stat_table = initialize_table("Stats", 4, tab_header=False)

    if monster_name == "biran ronso" or monster_name == "yenke ronso":
        stats["hp"] = get_ronso_hp(monster_name, kimahri_str, kimahri_mag)
        stats["strength"] = get_ronso_strength(monster_name, kimahri_hp)
        stats["magic"] = get_ronso_magic(monster_name, kimahri_hp)
        stats["agility"] = get_ronso_agility(monster_name, kimahri_agl)

    for i in range(0, len(stats), 2):
        left_stat = stat_cell_names[i]
        right_stat = stat_cell_names[i+1]
        left_val = format_monster_data(stat_keys[i], monster_name)
        right_val = format_monster_data(stat_keys[i+1], monster_name)
        
        stat_table.add_row(left_stat, left_val, right_stat, right_val)

    return stat_table



def get_element_table(monster_name):
    monster = monsters[monster_name]
    elements = monster["elem_resists"]
    element_keys = list(elements.keys())
    element_cell_names = CELL_NAMES["elements"]

    col_names = ["Element", "Resistance"]
    element_table = initialize_table("Elemental Resistances", 4, column_names=col_names)

    for i in range(0, len(elements), 2):
        left_element = element_cell_names[i]
        right_element = element_cell_names[i+1]
        left_resist = format_monster_data(element_keys[i], monster_name)
        right_resist = format_monster_data(element_keys[i+1], monster_name)

        element_table.add_row(left_element, left_resist, right_element, right_resist)

    return element_table
     


def get_status_resist_table(monster_name):
    monster = monsters[monster_name]
    statusses = monster["stat_resists"]
    status_keys = list(statusses.keys())
    status_cell_names = CELL_NAMES["statusses"]

    col_names = ["Status", "Resistance"]
    status_table = initialize_table("Status Resistances", 4, column_names=col_names)

    for i in range(0, len(statusses), 2):
        left_status = status_cell_names[i]
        right_status = status_cell_names[i+1]
        left_resist = format_monster_data(status_keys[i], monster_name)
        right_resist = format_monster_data(status_keys[i+1], monster_name)
        
        status_table.add_row(left_status, left_resist, right_status, right_resist)

    return status_table



def get_item_table(monster_name):
    item_table = initialize_table("Items and Loot", 2, tab_header=False)
    item_table.add_row("AP (Overkill)", format_monster_data("ap", monster_name))
    item_table.add_row("Gil", format_monster_data("gil", monster_name))
    item_table.add_row("Ronso Rage", format_monster_data("ronso_rage", monster_name))

    monster = monsters[monster_name]
    items = monster["items"]
    item_keys = list(items.keys())
    item_cell_names = CELL_NAMES["items"]

    for i in range(len(items)):
        action = item_cell_names[i]
        key = item_keys[i]

        if items[key] is None:
            continue

        item = format_monster_data(key, monster_name)
        item_table.add_row(action, item)

    return item_table



def get_bribe_table(monster_name):
    monster = monsters[monster_name]
    
    hp = monster["stats"]["hp"][0]
    hp_factor = 10
    probability = 25

    col_names = ["Amount in Gil", "Success Rate"]
    bribe_table = initialize_table("Bribe Success Rate", 2, column_names=col_names)

    while probability <= 100:
        bribe_amount = format_num(hp * hp_factor)
        bribe_table.add_row(f"{bribe_amount}", f"{probability}%")
        hp_factor += 5
        probability += 25

    return bribe_table



def get_equipment_table(monster_name):
    monster = monsters[monster_name]    
    equipment = monster["equipment"]
    equipment_keys = list(equipment.keys())
    equipment_cell_names = CELL_NAMES["equipment"]

    equipment_table = initialize_table("Equipment", 2, tab_header=False)

    for i in range(len(equipment)):
        name = equipment_cell_names[i]
        data = format_monster_data(equipment_keys[i], monster_name)
        equipment_table.add_row(name, data)

    return equipment_table



def get_arena_table(monster_name):
    monster = monster_arena[monster_name]
    arena_table = initialize_table("Monster Arena Reward", 2, tab_header=False)

    arena_table.add_row("Unlock Condition", format_monster_data("condition", monster_name))

    if "monsters" in monster:
        arena_table.add_row("Monsters To Catch", format_monster_data("monsters", monster_name))

    arena_table.add_row("Reward", format_monster_data("reward", monster_name))

    return arena_table



def get_remiem_table(monster_name):
    remiem_table = initialize_table("Battle Rewards", 2, tab_header=False)
    remiem_table.add_row("First Victory Reward", format_monster_data("first reward", monster_name))
    remiem_table.add_row("Recurring Victory Reward", format_monster_data("recurring reward", monster_name))

    return remiem_table
