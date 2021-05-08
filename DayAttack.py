from typing import Union
from BaseModel import BaseAttackModel
from utils import fetch_equip_master, calculate_all_equipment_stat, get_gear_improvement_stats
from GearBonus import calculate_bonus_gear_stats

class DayAttackModel(BaseAttackModel):
    """
    Model that describes an attack carried out in daytime
    """

    def calculate_base_attack_power(self) -> Union[float, int]:
        """
        Calculates base attack power for daytime
        """
        ship = self._attacker
        improvements = get_gear_improvement_stats(ship)
        bonus_stats = calculate_bonus_gear_stats(ship)

        enemy = self._defender
        if enemy.is_submarine():
            eq_asw = calculate_all_equipment_stat(ship.equip, "tais")
            stype_const = 8 if ship.stype in [6, 10, 16, 17] else 13
            base_attack_power = (2 * np.sqrt(ship.stats["as"]) + improvements["asw"] + 1.5 * eq_asw + stype_const)
        else:
            eq_fp = calculate_all_equipment_stat(ship.equip, "houg")
            base_attack_power = ship.stats["fp"] + improvements["fp"] + bonus_stats["houg"] + eq_fp
        return base_attack_power

    def calculate_precapped_power(self, base_attack_power) -> Union[float, int]:
        raise NotImplementedError()

    def calculate_capped_power(self, precapped_power) -> int:
        raise NotImplementedError()

    # add and mult for flooring
    def calculate_critical_power(self, capped_power, add=0, mult=1) -> int:
        raise NotImplementedError()

    # add and mult for flooring
    def calculate_postcap_power(self, crit_cap_power, add=0, mult=1) -> Union[float, int]:
        raise NotImplementedError()
