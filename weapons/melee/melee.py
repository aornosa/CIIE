from weapons.weapon_module import Weapon

class Melee(Weapon):
    def __init__(self, asset, name, damage, reach):
        super().__init__(asset, name, damage)
        self.reach = reach

    def attack(self):
        pass