import json
import copy
from DayAttack import DayAttackModel

with open("./tests/example.json") as r:
    sample = json.load(r)[0]

model = DayAttackModel()
model.load_from_data(sample)

def test_bap():
    bap = model.calculate_base_attack_power()
    assert(bap == 92.47213595499957)

def test_precap():
    bap = model.calculate_base_attack_power()
    precapped = model.calculate_precapped_power(bap)
    assert(precapped == 110.96656314599949)

def test_cap():
    bap = model.calculate_base_attack_power()
    precapped = model.calculate_precapped_power(bap)
    capped = model.calculate_capped_power(precapped)
    assert(capped == 110)

def test_crit():
    bap = model.calculate_base_attack_power()
    precapped = model.calculate_precapped_power(bap)
    capped = model.calculate_capped_power(precapped)
    crit = model.calculate_critical_power(capped)
    assert(crit == 110)

def test_postcap():
    bap = model.calculate_base_attack_power()
    precapped = model.calculate_precapped_power(bap)
    capped = model.calculate_capped_power(precapped)
    crit = model.calculate_critical_power(capped)
    postcap = model.calculate_postcap_power(crit)
    assert(postcap == 110)

def test_damage():
    bap = model.calculate_base_attack_power()
    precapped = model.calculate_precapped_power(bap)
    capped = model.calculate_capped_power(precapped)
    crit = model.calculate_critical_power(capped)
    postcap = model.calculate_postcap_power(crit)
    min_armor = model._defender.armor * 0.7
    max_armor = min_armor + (model._defender.armor - 1) * 0.6

    max_damage = model.calculate_damage(postcap, min_armor)
    min_damage = model.calculate_damage(postcap, max_armor)
    true_damage = model._actual_damage
    assert(true_damage >= min_damage and true_damage <= max_damage)
