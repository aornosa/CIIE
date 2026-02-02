from character import Character, DEFAULT_STATS

DEFAULT_STATS = {
    **DEFAULT_STATS,
    "speed": 200,
    "headshot_chance": 0,
    "headshot_damage": 1.5,
    "defense": 0,
}

class Player(Character):
    def __init__(self, asset, position=(0,0), rotation=0, name="Player", health=100):
        super().__init__(asset, position, rotation, name, health)
        self.score = 0
        self.inventory = []

    def add_score(self, points):
        self.score += points

    def get_score(self):
        return self.score

    def get_inventory(self):
        return self.inventory

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
