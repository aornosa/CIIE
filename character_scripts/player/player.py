from character_scripts.character import Character, DEFAULT_STATS
from character_scripts.player.inventory import Inventory

DEFAULT_STATS = {
    **DEFAULT_STATS,
    "speed": 200,
    "headshot_chance": 0,
    "headshot_damage": 1.5,
    "defense": 0,
}

class Player(Character):
    def __init__(self, asset, position=(0,0), rotation=0, scale=0.3, name="Player", health=100):
        super().__init__(asset, position, rotation, scale, name, health)
        self.score = 0
        self.inventory = Inventory()

    def add_score(self, points):
        self.score += points

    def get_score(self):
        return self.score

    def get_inventory(self):
        return self.inventory
