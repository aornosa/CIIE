from weapons.weapon_module import Weapon

class Melee(Weapon):
    def __init__(self, name, damage, weight, reach):
        super().__init__(name, damage, weight)
        self.reach = reach

    def attack(self):
        return f"Swinging {self.name} for {self.damage} damage within {self.reach} meters!"