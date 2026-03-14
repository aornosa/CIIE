import pygame

from core.audio.audio_emitter import AudioEmitter

AMMO_TYPES = {
    "9x19": "assets/ammo/9x19/data.json",
    "7.62": "assets/ammo/7.62/data.json",
    "12gauge": "assets/ammo/12Gauge/data.json",
}


class Weapon:
    def __init__(self, asset, name, damage, pullout_time=0):
        self.asset = pygame.image.load(asset)
        self.name = name
        self.damage = damage
        self.pullout_time = pullout_time
        self.parent = None
        self.audio_emitter = None

    def update(self):
        pass

    def get_name(self) -> str:
        return self.name

    def get_damage(self) -> int:
        return self.damage

    def get_asset(self):
        return self.asset

    def on_equipped(self, parent):
        self.parent = parent
        if parent and hasattr(parent, "audio_emitter"):
            self.audio_emitter = parent.audio_emitter

    def on_unequipped(self):
        self.parent = None
        self.audio_emitter = None