from character_scripts.character import Character
from core.collision.collision_manager import CollisionManager
from core.collision.layers import LAYERS

class Enemy(Character):
    def __init__(self, asset, position=(0, 0), rotation=0, scale=1,
                 name="Enemy", health=100, strength=10, speed=100):
        super().__init__(asset, position, rotation, scale, name, health)
        self.strength = strength
        self.speed    = speed
        self.brain    = None
        self.collider.layer = LAYERS["enemy"]
        self._hit_flash_timer    = 0.0
        self._HIT_FLASH_DURATION = 0.12
        self._player_ref         = None
        self._attack_timer       = 0.0

    def is_alive(self) -> bool: return self.health > 0

    def can_attack(self, delta_time: float) -> bool:
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False

    def die(self):
        CollisionManager.dynamic_colliders.discard(self.collider)
        # no_reward se asigna externamente en enemigos que no deben dar score ni loot
        if self._player_ref is not None and not getattr(self, "no_reward", False):
            try:
                from runtime.loot_table import on_enemy_killed
                on_enemy_killed(self, self._player_ref)
            except Exception:
                pass
        super().die()

    def take_damage(self, amount: int):
        super().take_damage(amount)
        self._hit_flash_timer = self._HIT_FLASH_DURATION