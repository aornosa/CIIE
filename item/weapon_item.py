import pygame
from item.item_module import Item

class WeaponItem(Item):
    def __init__(self, asset, position=(0, 0), rotation=0, scale=1, name="", description="", damage=0, range=0):
        super().__init__(asset, position, rotation, scale, name, description)
        self.damage = damage
        self.range = range