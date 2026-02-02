import pygame
from pygame.transform import scale

DEFAULT_STATS = {
    "max_health": 100,
    "speed": 150,
}


class Character: # Make inherit from Object
    def __init__(self,asset, position, rotation, size_scale, name, health):
        self.asset = pygame.image.load(asset)
        self.position = pygame.Vector2(position)
        self.rotation = rotation
        self.scale = size_scale

        self.name = name

        self.health = health
        self.base_health = health

        self.base_stats = dict(DEFAULT_STATS)
        self.current_stats = dict(DEFAULT_STATS)

        self.effects = {}

    def attack(self, other, damage):
        other.take_damage(damage)
        return damage

    def is_alive(self):
        return self.health > 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > self.base_health:
            self.health = self.base_health

    def add_effect(self, effect):
        existing = self.effects.get(effect.name)
        if existing is None:
            self.effects[effect.name] = effect
        else:
            self.effects[effect.name] = effect
        self._recalculate_stats()

    def remove_effect(self, effect_name):
        if effect_name in self.effects:
            del self.effects[effect_name]
            self._recalculate_stats()

    def _recalculate_stats(self):
        self.current_stats = dict(self.base_stats)
        for effect in self.effects.values():
            for stat, value in effect.modifiers.items():
                self.current_stats[stat] = self.current_stats.get(stat, 0) + value
        # Limit stats
        self.current_stats["speed"] = max(50, self.current_stats.get("speed", 50))
        self.current_stats["max_health"] = max(1, self.current_stats.get("max_health", 1))

    def get_stat(self, key):
        return self.current_stats.get(key, 0)

    def update(self, delta_time):
        pass

    def draw(self, screen, camera):
        rotated_asset = pygame.transform.rotate(self.asset, self.rotation)
        w, h = rotated_asset.get_size()
        print(self.scale)
        new_w = int(w * self.scale)
        new_h = int(h * self.scale)
        scaled_asset = pygame.transform.scale(rotated_asset, (new_w, new_h))
        screen.blit(scaled_asset, self.position - camera.position)
