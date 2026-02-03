from weapons.weapon_module import Weapon

class Ranged(Weapon):
    def __init__(self, name, damage, max_range, ammo_type):
        super().__init__(name, damage)
        self.max_range = max_range
        self.ammo_type = ammo_type

    def shoot(self):
        pass