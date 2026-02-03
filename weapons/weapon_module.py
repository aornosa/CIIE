import pygame
from core.object import Object

AMMO_TYPES = {
    "low_caliber": "assets/ammo/bullet_clip.png",
    "high_caliber": "assets/ammo/high_caliber_clip.png",
    "shell": "assets/ammo/shell.png",
}

class Weapon:
    def __init__(self, asset, name, damage):
        self.asset = pygame.image.load(asset)
        self.name = name
        self.damage = damage
        self.object = Object(asset, (0, 0), 0, 1)