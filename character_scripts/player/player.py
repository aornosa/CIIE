from character_scripts.character import Character, DEFAULT_STATS
from character_scripts.player.inventory import Inventory
from core.audio.audio_listener import AudioListener
from core.collision.layers import LAYERS

DEFAULT_STATS = {
    **DEFAULT_STATS,
    "speed":           400,
    "headshot_chance": 0,
    "headshot_damage": 1.5,
    "defense":         0,
}

class Player(Character):
    def __init__(self, asset, position=(0, 0), rotation=0, scale=0.3, name="Player", health=100):
        super().__init__(asset, position, rotation, scale, name, health)
        self.score           = 0
        self.coins           = 200
        self.inventory       = Inventory()
        self.inventory.owner = self
        self.collider.layer  = LAYERS["player"]
        self.audio_listener = AudioListener(self)
        self._recalculate_stats()

    def add_coins(self, amount: int):     self.coins += amount
    def add_score(self, points: int):     self.score += points
    def get_score(self) -> int:           return self.score
    def get_inventory(self) -> Inventory: return self.inventory

    def spend_coins(self, amount: int) -> bool:
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def update(self, delta_time: float):
        self.inventory.update(delta_time)