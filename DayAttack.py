from typing import Union
import numpy as np
from BaseModel import BaseAttackModel, calculate_base_asw_power
from utils import fetch_equip_master, calculate_all_equipment_stat, get_gear_improvement_stats
from GearBonus import calculate_bonus_gear_stats
from static import engagement_modifiers, formation_modifiers_shelling, formation_modifiers_asw, day_shelling_cap, asw_cap

class DayAttackModel(BaseAttackModel):
    """
    Model that describes an attack carried out in daytime
    """

    def calculate_base_attack_power(self):
        """
        Calculates base attack power for daytime shelling
        """
        ship = self._attacker
        improvements = get_gear_improvement_stats(ship)
        bonus_stats = calculate_bonus_gear_stats(ship)
        cf_factor = calculate_combined_fleet_factor(ship, self._defender)
        enemy = self._defender
        # ASW attack
        if enemy.is_submarine():
            base_attack_power = calculate_base_asw_power(ship, improvements)

        # Carrier shelling
        elif ship.is_carrier():
            eq_bomb = calculate_all_equipment_stat(ship.equip, "baku")
            eq_tp = calculate_all_equipment_stat(ship.equip, "raig")
            eq_fp = calculate_all_equipment_stat(ship.equip, "houg")

            fp = ship.stats["fp"] + improvements["fp"] + bonus_stats["houg"] + eq_fp
            tp = eq_tp + improvements["tp"]

            base_attack_power = 50 + 1.5 * (fp + tp + int(1.3 * eq_bomb) + cf_factor)

        else:
            eq_fp = calculate_all_equipment_stat(ship.equip, "houg")
            base_attack_power = ship.stats["fp"] + improvements["fp"] + bonus_stats["houg"] + eq_fp + cf_factor
        return base_attack_power

    def calculate_precapped_power(self, base_attack_power):
        """
        Calculates precapped power. For day shelling attacks, the factors are health, formation, engagement and hidden equipment fits
        """
        ship = self._attacker
        health_mod = ship.health_modifier()
        engagement_mod = engagement_modifiers[self._engagement]
        formation_mod = (formation_modifiers_asw if self._defender.is_submarine() else formation_modifiers_shelling)[ship.formation]
        if not isinstance(formation_mod, float):
            formation_mod = formation_mod(*ship._position)
        
        num = 0
        # CL single/twin mount hidden attack bonus
        if ship.stype in [2, 3, 21] and not self._defender.is_submarine():
            num_single = 0
            num_twin = 0
            for equip_id in ship.equip:
                if equip_id in [4, 11]:
                    num_single += 1
                if equip_id in [65, 119, 139, 303, 310, 359, 360, 361, 407]:
                    num_twin += 1
            num += np.sqrt(num_single) + 2 * np.sqrt(num_twin)
        
        # Zara class 203mm fit bonus
        if ship.ctype == 64:
            num_203 = 0
            for equip_id in ship.equip:
                if equip_id == 163:
                    num_203 += 1
            num += np.sqrt(num_203)

        return base_attack_power * health_mod * formation_mod * engagement_mod + num

    def calculate_capped_power(self, precapped_power):
        cap = asw_cap if self._defender.is_submarine() else day_shelling_cap
        if precapped_power < cap:
            return int(precapped_power)
        else:
            return int(cap + np.sqrt(precapped_power - cap))

    def calculate_critical_power(self, capped_power, mult=1):
        if self._is_critical:
            crit_mod = 1
            ship = self._attacker
            if ship.is_carrier() and not self._defender.is_submarine():
                if ship._cutin == 7:
                    crit_mod = 1.25 # lazy
                else:
                    crit_mod = ship.crit_modifier()

            return capped_power * 1.5 * crit_mod * mult

        else:
            return capped_power

    def calculate_postcap_power(self, postcrit_power, add=0, mult=1):
        """
        Calculates postcap power. For day shelling attacks, the modifiers are arty spotting mod and AP shell modifier
        """
        ship = self._attacker
        arty_spot_mod = ship.arty_spotting_modifier()
        AP_shell_mod = ship.ap_shell_modifier()
        return (postcrit_power * arty_spot_mod * AP_shell_mod + add) * mult
        

def calculate_combined_fleet_factor(attacker, defender):
    defender_combined = defender.formation >= 10
    player_combined = attacker.combined
    main_fleet = attacker.main_fleet
    if not defender_combined:
        if player_combined == 1: # CTF
            return 2 if main_fleet else 10
        if player_combined == 2: # STF
            return 10 if main_fleet else -5
        if player_combined == 3: # TCF
            return -5 if main_fleet else 10
    else:
        if player_combined == 1: # CTF
            return 2 if main_fleet else -5
        if player_combined == 2: # STF
            return 10 if main_fleet else -5
        if player_combined == 3: # TCF
            return -5 if main_fleet else -5
    return 5
