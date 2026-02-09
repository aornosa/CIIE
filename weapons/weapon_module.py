import pygame
from core.object import Object

AMMO_TYPES = {
    "low_caliber": "assets/ammo/9x19",
    "high_caliber": "assets/ammo/7.62",
    "shell": "assets/ammo/12Gauge",
}

class Weapon:
    def __init__(self, asset, name, damage, pullout_time=0):
        self.asset = pygame.image.load(asset)
        self.name = name
        self.damage = damage
        self.object = Object(asset, (0, 0), 0, 1)
        self.pullout_time = pullout_time    # Time in seconds to pull out the weapon