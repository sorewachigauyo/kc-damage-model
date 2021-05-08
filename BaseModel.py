from typing import Union
from utils import fetch_ship_master, fetch_equip_master

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

        dmginst = data["damageInstance"]
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
        self._position = [data["position"], data["shipCount"]]

        self.master = fetch_ship_master(self.id)
        self.stype = self.master["api_stype"]

    def is_carrier(self):
        return self.stype in [7, 11, 18] # CVL, CV, CVB

    def health_modifier(self):
        return [0, 0.4, 0.7, 1, 1][self._hp_status] # sunk, taiha, chuuha, shouha, green

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
