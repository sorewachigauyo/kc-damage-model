from typing import Union
import numpy as np
from utils import fetch_ship_master, fetch_equip_master, bomber_type2_ids
from static import day_cutin_modifiers

class BaseAttackModel:
    def __init__(self):
        """
        A basic model for attacks, contains basic information that is needed to calculate damage
        """
        self._attacker = None
        self._defender = None
        self._is_critical = False
        self._actual_damage = 0
        self._engagement = 0

    def load_from_data(self, data: dict) -> None:
        self._attacker = Attacker(data["ship"])
        self._defender = Defender(data["enemy"])

        keys = data.keys()
        if "damageInstance" in keys:
            dmginst = data["damageInstance"]
        else:
            dmginst = data["damageinstance"]
        self._is_critical = dmginst["isCritical"]
        self._actual_damage = dmginst["actualDamage"]
        self._engagement = data["engagement"]

    def calculate_base_attack_power(self) -> Union[float, int]:
        raise NotImplementedError()

    def calculate_precapped_power(self, base_attack_power) -> Union[float, int]:
        raise NotImplementedError()

    def calculate_capped_power(self, precapped_power) -> int:
        raise NotImplementedError()

    # add and mult for flooring
    def calculate_critical_power(self, capped_power, add=0, mult=1) -> int:
        raise NotImplementedError()

    def calculate_postcap_power(self, crit_cap_power) -> Union[float, int]:
        raise NotImplementedError()

    def calculate_damage(self, postcap_power, armor, armor_reduction=0):
        return int((postcap_power - (armor - armor_reduction)) * self._attacker.ammo_mod)

class Attacker:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.stats = data["stats"]
        self.equip = data["equip"]
        self.slots = data["slots"]
        self.stars = data["improvements"]
        self.ammo_mod = data["rAmmoMod"]
        self.proficiency = data["proficiency"]
        self.formation = data["formation"]

        self._cutin = data["spAttackType"]
        self._cutin_equips = data["cutinEquips"]
        self._hp_status = data["damageStatus"]
        self._position = (data["position"], data["shipCount"])

        self.master = fetch_ship_master(self.id)
        self.stype = self.master["api_stype"]
        self.ctype = self.master["api_ctype"]
        self.combined = data["combinedFleet"]
        self.main_fleet = data["isMainFleet"]

    def is_carrier(self):
        return self.stype in [7, 11, 18] # CVL, CV, CVB

    def health_modifier(self):
        return [0, 0.4, 0.7, 1, 1][self._hp_status] # sunk, taiha, chuuha, shouha, green

    def crit_modifier(self):
        crit_mod = 1
        if not self.is_carrier():
            return crit_mod

        for idx, equip_id in enumerate(self.equip):
            rank = self.proficiency[idx]
            if equip_id == -1 or rank < 1:
                continue
            master = fetch_equip_master(equip_id)
            if (master["api_type"][2] in bomber_type2_ids and (master["api_raig"] > 0 or master["api_baku"] > 0)):
                exp = [0, 10, 25, 40, 55, 70, 80, 120][rank]
                mod = [0, 1, 2, 3, 4, 5, 7, 10][rank]
                crit_mod += int(np.sqrt(exp) + mod) / (100 if idx == 0 else 200)

        return crit_mod

    def arty_spotting_modifier(self):
        if self._cutin > 100 and self._cutin < 200:
            raise NotImplementedError("Touch-type attack have too many factors, though it may be possible to implement with data present")
        
        if self._cutin > 0:
            if self._cutin == 7:
                return self._cvci_modifier()
            else:
                return day_cutin_modifiers[str(self._cutin)]
        else:
            return 1
            

    def _cvci_modifier(self):
        if len(self._cutin_equips) == 2:
            return 1.1
        db = 0
        for equip_id in self.equip:
            if equip_id == -1:
                continue
            master = fetch_equip_master(equip_id)
            if (master["api_type"][2] == 7):
                db += 1
        if db == 2:
            return 1.2
        else:
            return 1.25

    def ap_shell_modifier(self):
        ap_shell = False
        main_gun = False
        secondary_gun = False
        radar = False

        for equip_id in self.equip:
            if equip_id == -1:
                continue
            master = fetch_equip_master(equip_id)
            type2 = master["api_type"][2]
            if type2 == 19:
                ap_shell = True
            elif type2 == 3:
                main_gun = True
            elif type2 == 4:
                secondary_gun = True
            elif type2 == 12 or type2 == 13:
                radar = True

        if ap_shell and main_gun:
            if radar and secondary_gun:
                return 1.3
            elif radar:
                return 1.25
            elif secondary_gun:
                return 1.2
            else:
                return 1.1
        return 1

class Defender:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.equip = data["equip"]
        self.hp = data["hp"]
        self.armor = data["armor"]
        self.formation = data["formation"]
        self.master = fetch_ship_master(self.id)
        self.stype = self.master["api_stype"]

    def is_installation(self):
        return self.master["api_soku"] == 0

    def is_submarine(self):
        return self.stype == 13 or self.stype == 14

    def is_armour_piercing_target(self):
        return self.stype in [5, 6, 8, 9, 10, 11, 18] # CA, CAV, FBB, BB, BBV, CV, CVB

def calculate_base_asw_power(ship, improvements):
    from utils import calculate_all_equipment_stat
    eq_asw = calculate_all_equipment_stat(ship.equip, "tais")
    stype_const = 8 if ship.stype in [6, 10, 16, 17] else 13
    base_attack_power = (2 * np.sqrt(ship.stats["as"]) + improvements["asw"] + 1.5 * eq_asw + stype_const)

    flag1 = False # sonar
    flag2 = False # DCP
    flag3 = False # DC
    flag4 = False # legacy
    flag5 = False # legacy

    for equip_id in ship.equip:
        if equip_id == -1:
            continue
        master = fetch_equip_master(equip_id)
        type2 = master["api_type"][2]
        if type2 == 14:
            flag1 = True
        elif type2 == 15 and equip_id in [44, 45]:
            flag2 = True
        elif type2 == 15 and equip_id in [226, 227]:
            flag3 = True
        
        type3 = master["api_type"][3]
        if type3 == 18:
            flag4 = True
        elif type3 == 17:
            flag5 = True

    if flag4 and flag5:
        base_attack_power *= 1.15
    
    mod = 1
    if flag1 and flag3:
        mod += 0.15
    if flag2 and flag3:
        mod += 0.1
    
    return base_attack_power * mod
