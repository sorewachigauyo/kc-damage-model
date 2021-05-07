import json
import copy
from BaseModel import BaseAttackModel
from GearBonus import calculate_bonus_gear_stats, data, fill_synergy, fill_count, fill_stars

with open("./tests/example.json") as r:
    sample = json.load(r)[0]

model = BaseAttackModel()
model.load_from_data(sample)
ship = model._attacker

def test_synergy_load():
    bonus_accum = copy.deepcopy(data)
    synergy = bonus_accum["synergyGears"]
    fill_synergy(ship, synergy)
    assert(synergy["surfaceRadar"] == 1 and synergy["airRadar"] == 1)

def test_gear_load():
    bonus_accum = copy.deepcopy(data)
    fill_count(ship, bonus_accum)
    assert(bonus_accum["266"]["count"] == 2 and bonus_accum["129"]["count"] == 1)

def test_gear_bonus():
    res = calculate_bonus_gear_stats(ship)
    assert res == {
        'houg': 8,
        'souk': 0,
        'raig': 5,
        'houk': 3,
        'tyku': 0,
        'tais': 2,
        'saku': 1,
        'houm': 0,
        'leng': 0,
        'soku': 0
    }

