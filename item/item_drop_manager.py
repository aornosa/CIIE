import pygame
from core.monolite_behaviour import MonoliteBehaviour
from item.item_instance import DroppedItem
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class DropManager(MonoliteBehaviour):
    def __init__(self):
        MonoliteBehaviour.__init__(self)
        self.dropped_items: list[DroppedItem] = []

    def drop_item(self, item, position, velocity=None):
        dropped = DroppedItem(item, position, velocity)
        self.dropped_items.append(dropped)
        print(f"[DROP] {item.name} en {position}")
        return dropped

    def draw(self, screen, camera):
        for item in self.dropped_items:
            item.draw(screen, camera)