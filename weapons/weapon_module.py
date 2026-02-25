import pygame

from core.audio.audio_emitter import AudioEmitter
from core.object import Object

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
        self.object = Object(asset, (0, 0), 0, 1)
        self.pullout_time = pullout_time    # Time in seconds to pull out the weapon

        # Will be set when equipped by a character
        self.parent = None
        self.audio_emitter = None