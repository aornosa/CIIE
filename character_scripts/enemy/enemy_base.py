from character_scripts.character import Character
from core.collision.layers import LAYERS


class Enemy(Character):
    def __init__(self, asset, position=(0, 0), rotation=0, scale=1,
                 name="Enemy", health=100, strength=10, speed=100):
        super().__init__(asset, position, rotation, scale, name, health)
        self.strength = strength
        self.speed = speed
        self.brain = None
        self.collider.layer = LAYERS["enemy"]

        self._player_ref = None

    def is_alive(self):
        return self.health > 0

    def die(self):
        print(f"{self.name} has died.")
        from core.collision.collision_manager import CollisionManager
        CollisionManager.dynamic_colliders.discard(self.collider)

        if self._player_ref is not None:
            try:
                from runtime.loot_table import on_enemy_killed
                on_enemy_killed(self, self._player_ref)
            except Exception as e:
                print(f"[LOOT] Error en on_enemy_killed: {e}")