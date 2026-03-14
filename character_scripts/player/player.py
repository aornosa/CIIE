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

_DASH_DISTANCE = 150.0
_DASH_COOLDOWN = 3.0


class Player(Character):
    def __init__(self, asset, position=(0, 0), rotation=0, scale=0.3, name="Player", health=100):
        super().__init__(asset, position, rotation, scale, name, health)
        self.score           = 0
        self.coins           = 200
        self.inventory       = Inventory()
        self.inventory.owner = self
        self.collider.layer  = LAYERS["player"]

        # Mejoras de armas acumuladas desde la tienda
        self.weapon_upgrades = {
            "ranged_damage":      0,
            "ranged_clip":        0,
            "ranged_fire_rate":   0.0,
            "ranged_reload_time": 0.0,
            "melee_damage":       0,
            "melee_attack_speed": 0.0,
        }

        # Habilidad de dash — se desbloquea en la tienda
        self.has_dash          = False
        self._dash_cooldown    = 0.0
        self._dash_direction   = None

        self.base_stats["speed"] = 370
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

    def try_dash(self, weapon_controller=None) -> bool:
        if not self.has_dash:
            return False
        if self._dash_cooldown > 0:
            return False
        # No dashear si se está recargando o atacando
        if weapon_controller:
            active = self.inventory.get_weapon(self.inventory.active_weapon_slot)
            from weapons.ranged.ranged import Ranged
            from weapons.melee.melee import Melee
            if isinstance(active, Ranged) and active.is_reloading():
                return False
            if isinstance(active, Melee) and active._is_attacking:
                return False

        direction = self._dash_direction
        if direction is None or direction.length() < 0.01:
            import pygame
            direction = pygame.Vector2(0, -1).rotate(-self.rotation)
        else:
            direction = direction.normalize()

        self.position       += direction * _DASH_DISTANCE
        self._dash_cooldown  = _DASH_COOLDOWN
        return True

    def update(self, delta_time: float):
        self.inventory.update(delta_time)
        if self._dash_cooldown > 0:
            self._dash_cooldown = max(0.0, self._dash_cooldown - delta_time)