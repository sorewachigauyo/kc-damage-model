import json
import os

fighter_bomber_ids = [60, 154, 219]
sec_gun_filter = [11, 134, 135]
t2_fp_list = [1, 2, 18, 19, 21, 24, 29, 42, 36, 37, 39, 46]

with open("./data/api_mst_ship.json", encoding="utf-8") as r:
    ship_master = json.load(r)

with open("./data/api_mst_slotitem.json", encoding="utf-8") as r:
    equip_master = json.load(r)

with open("./data/KC3RemodelDB.json", encoding="utf-8") as r:
    remodel_db = json.load(r)

def fetch_ship_master(ship_id):
    return next(ship for ship in ship_master if ship["api_id"] == ship_id)

def fetch_equip_master(equip_id):
    return next(equip for equip in equip_master if equip["api_id"] == equip_id)

def find_ship_origin(ship_id):
    return remodel_db["originOf"][str(ship_id)]

def find_remodel_group(ship_id):
    original_id = find_ship_origin(ship_id)
    return remodel_db["remodelGroups"][str(original_id)]["group"]

def calculate_equip_stat(equip_id, api_stat):
    if equip_id == -1:
        return 0
    master = fetch_equip_master(equip_id)
    return master["api_" + api_stat]

def calculate_all_equipment_stat(equip_list, api_stat):
    num = 0
    for equip_id in equip_list:
        num += calculate_equip_stat(equip_id, api_stat)
    return num

def get_gear_improvement_stats(ship):
    result = {
        "fp": 0,
        "asw": 0,
        "tp": 0,
        "yasen": 0
    }
    for idx, equip_id in enumerate(ship.equips):
        improvement = ship.stars[idx]
        if equip_id == -1 or improvement <= 0:
            continue
        master = fetch_equip_master(equip_id)
        type2 = master.api_type[2]

        # FP
        # Large Gun
        if type2 == 3:
            result["fp"] += 1.5 * np.sqrt(improvement)
        # Secondary Gun
        elif type2 == 4:
            if equip_id in sec_gun_filter:
                result["fp"] += np.sqrt(improvement)
            else:
                mod = 0.2 if master.api_type[3] == 16 else 0.3
                result["fp"] += mod * improvement
        # F/B and Jet F/B
        elif (type2 == 7 or type2 == 57) and equip_id in fighter_bomber_ids:
            result["fp"] += 0.5 * np.sqrt(improvement)
        # TB and Jet TB
        elif type2 == 8 or type2 == 58:
            result["fp"] += 0.2 * improvement
        # Sonar and large sonar
        elif type2 == 14 or type2 == 40:
            result["fp"] += 0.75 * np.sqrt(improvement)
        # Depth Charge Projector
        elif type2 == 15 and not equip_id in [226, 227]:
            result["fp"] += 0.75 * np.sqrt(improvement)
        elif type2 in t2_fp_list:
            result["fp"] += np.sqrt(improvement)
        
        # TP
        if type2 in [5, 21, 32]:
            result["tp"] += 1.2 * np.sqrt(improvement)

        # ASW
        if type2 in [14, 15, 40]:
            result["asw"] += np.sqrt(improvement)
        elif (type2 == 7 or type2 == 57) and equip_id not in fighter_bomber_ids:
            result["asw"] += 0.2 * improvement
        elif type2 == 8 or type2 == 58:
            result["asw"] += 0.2 * improvement
        elif type2 == 25:
            mod = 0.3 if master.api_tais > 10 else 0.2
            result["asw"] += mod * improvement

    return result
