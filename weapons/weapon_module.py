import pygame
from core.object import Object


class Weapon:
    def __init__(self, asset, name, damage):
        self.asset = pygame.image.load(asset)
        self.name = name
        self.damage = damage
        # self.object = Object(self.asset, (0, 0), 0, (40, 40))
