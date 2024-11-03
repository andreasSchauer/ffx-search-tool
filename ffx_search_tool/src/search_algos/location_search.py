from rich.table import Table
from rich import box
from ffx_search_tool.src.constants import LOCATIONS, TABLE_WIDTH, MONSTER_DATA
from ffx_search_tool.src.utilities import get_table_data, initialize_table, console


def select_location():
    for i, location in enumerate(LOCATIONS):
        print(f"{i + 1}: {location.title()}")
        
    choice = int(input("Invalid location. Choose by number: ")) - 1
    return LOCATIONS[choice]



def get_local_monsters(location_name):
    local_monsters = list(filter(lambda mon: location_name in MONSTER_DATA[mon]["location"], MONSTER_DATA))
    reoccuring_monsters = get_reoccuring_monsters(local_monsters)
    one_time_monsters = get_one_time_monsters(local_monsters)
    boss_monsters = get_boss_monsters(local_monsters)

    return reoccuring_monsters, one_time_monsters, boss_monsters
    

def get_reoccuring_monsters(local_monsters):
    return list(filter(lambda mon: MONSTER_DATA[mon]["is_reoccuring"], local_monsters))

def get_one_time_monsters(local_monsters):
    return list(filter(lambda mon: not MONSTER_DATA[mon]["is_reoccuring"] and not MONSTER_DATA[mon]["is_boss"], local_monsters))

def get_boss_monsters(local_monsters):
    boss_monsters = list(filter(lambda mon: MONSTER_DATA[mon]["is_boss"], local_monsters))
    boss_monsters_sorted = []

    for boss in boss_monsters:
        if MONSTER_DATA[boss]["has_allies"]:
            for ally in MONSTER_DATA[boss]["allies"]:
                if ally not in boss_monsters_sorted:
                    boss_monsters_sorted.append(ally)
        else:
            boss_monsters_sorted.append(boss)

    return boss_monsters_sorted



def get_location_table(location_name, monster_list, type):
    title = f"{location_name.title()} - {type}"
    table = Table(pad_edge=False, box=box.MINIMAL_HEAVY_HEAD, width=TABLE_WIDTH, padding=1)
    table.add_column(title)

    for monster_name in monster_list:
        monster = MONSTER_DATA[monster_name]
        table.add_row(get_short_mon_table(monster, monster_name))

    console.print(table)



def get_short_mon_table(monster, monster_name): 
    if monster["is_catchable"]:
        monster_name += " - Catchable"

    monster_table = initialize_table(monster_name.title(), 2, tab_header=False)

    monster_table.add_row("HP (Overkill)", get_table_data("hp", monster))
    monster_table.add_row("AP (Overkill)", get_table_data("ap", monster))
    monster_table.add_row("Gil", get_table_data("gil", monster))
    monster_table.add_row("Steal (Rare Steal)", get_table_data("steals", monster))
    monster_table.add_row("Drop (Rare Drop)", get_table_data("drops", monster))
    monster_table.add_row("Bribe (Max Amount)", get_table_data("bribe_max", monster))

    return monster_table

