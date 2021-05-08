from scipy.optimize import minimize
import json
import numpy as np
from DayAttack import DayAttackModel
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("-cases", type=int, default=200)

def obj(case, mod):
    model = DayAttackModel()
    model.load_from_data(case)

    bap = model.calculate_base_attack_power()
    precapped = model.calculate_precapped_power(bap)
    capped = model.calculate_capped_power(precapped)
    crit = model.calculate_critical_power(capped)
    postcap = model.calculate_postcap_power(crit) * mod
    min_armor = model._defender.armor * 0.7
    max_armor = min_armor + (model._defender.armor - 1) * 0.6

    max_damage = model.calculate_damage(postcap, min_armor)
    min_damage = model.calculate_damage(postcap, max_armor)
    true_damage = model._actual_damage
    if true_damage >= min_damage and true_damage <= max_damage:
        return 1
    else:
        return 0

def parse_data(case):
    model = DayAttackModel()
    model.load_from_data(case)

    bap = model.calculate_base_attack_power()
    precapped = model.calculate_precapped_power(bap)
    capped = model.calculate_capped_power(precapped)
    crit = model.calculate_critical_power(capped)
    postcap = model.calculate_postcap_power(crit)
    armor = model._defender.armor
    min_armor = armor * 0.7
    max_armor = min_armor + (armor - 1) * 0.6
    
    return (postcap, model._actual_damage, model._attacker.ammo_mod, min_armor, max_armor)

def calc_damage(postcap, armor, ammo_mod):
    return int((postcap - armor) * ammo_mod)

def opt(mod, *args):
    samples = args[0]
    res = 0
    for case in samples:
        postcap, true_damage, ammo_mod, min_armor, max_armor = case
        min_dam = calc_damage(postcap * mod, max_armor, ammo_mod)
        max_dam = calc_damage(postcap * mod, min_armor, ammo_mod)
        if not(true_damage >= min_dam and true_damage <= max_dam):
            res += 1
    return res

if __name__ == '__main__':
    args = parser.parse_args()
    filename = args.file
    cases = args.cases
    with open(filename) as r:
        data = json.load(r)
    cases = min(cases, len(data))
    x = list(range(cases))
    samples = [parse_data(data[i]) for i in x]
    guess = 1
    
    res = minimize(opt, guess, args=(samples,), method="Nelder-Mead", options={'fatol':5/100 * cases})
    print(res.x[0])
