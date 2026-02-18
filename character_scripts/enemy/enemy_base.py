import json
from character_scripts.character import Character
from core.collision.layers import LAYERS

# Substitute with JSON type object
ENEMY_TYPES = {
    "infected",
    "blindeye",
    "bigfoot",
}

class Enemy(Character):
    def __init__(self, asset, data, brain, position=(0,0), rotation=0, scale=1):
        self.data = json.loads(data)
        super().__init__(asset, position, rotation, scale, data["name"], data["health"])
        self.brain = brain

    # Nonjson
    def __init__(self, asset, position=(0,0), rotation=0, scale=1, name="Enemy", strength=10, health=100):
        super().__init__(asset, position, rotation, scale, name, health)
        self.strength = strength
        self.behavior = None  # Placeholder for AI behavior
        self.collider.layer = LAYERS["enemy"]

    def is_alive(self):
        return self.health > 0