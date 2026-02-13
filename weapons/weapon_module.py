import pygame
from core.object import Object

AMMO_TYPES = {
    "pistol": "assets/ammo/9x19/data.json",
    "rifle": "assets/ammo/7.62/data.json",
    "shell": "assets/ammo/12Gauge/data.json",
}

class Weapon:
    def __init__(self, asset, name, damage, pullout_time=0):
        self.asset = pygame.image.load(asset)
        self.name = name
        self.damage = damage
        self.object = Object(asset, (0, 0), 0, 1)
        self.pullout_time = pullout_time    # Time in seconds to pull out the weapon