import json
import os

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
