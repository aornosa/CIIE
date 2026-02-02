from weapons.weapon_module import Weapon

class Ranged(Weapon):
    def __init__(self, name, damage, weight, max_range, ammo_type):
        super().__init__(name, damage, weight)
        self.max_range = max_range
        self.ammo_type = ammo_type

    def attack(self):
        pass