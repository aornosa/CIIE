from character_scripts.character import Character

ENEMY_TYPES = {
    "infected",
    "blindeye",
    "bigfoot",
}

class Enemy(Character):
    def __init__(self, asset, position=(0,0), rotation=0, scale=1, name="Enemy", health=50, strength=10):
        super().__init__(asset, position, rotation, scale, name, health)
        self.strength = strength
        self.behavior = None  # Placeholder for AI behavior

    def is_alive(self):
        return self.health > 0

