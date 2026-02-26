import pygame

from core.audio.audio_emitter import AudioEmitter
from core.object import Object
from core.collision.collider import Collider
from core.collision.quadtree import Rectangle

DEFAULT_STATS = {
    "max_health": 100,
    "speed": 200,
}


class Character(Object):
    def __init__(self, asset, position, rotation, scale, name, health):
        super().__init__(asset, position, rotation, scale)

        self.name = name

        self.health = health
        self.base_health = health

        self.base_stats = dict(DEFAULT_STATS)
        self.current_stats = dict(DEFAULT_STATS)

        self.effects = {}
        self.collider = Collider(self, Rectangle.from_rect(self.asset.get_rect()))
        self.audio_emitter = AudioEmitter(self, position, None)

    def is_alive(self):
        return self.health > 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        if self.health == 0:
            self.die()

    def die(self):
        # Placeholder for death logic (e.g., play animation, drop loot)
        print(f"{self.name} has died.")
        pass

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
