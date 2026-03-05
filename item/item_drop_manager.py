import pygame

from core.monolite_behaviour import MonoliteBehaviour
from item.item_instance import DroppedItem
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class DropManager(MonoliteBehaviour):
    def __init__(self):
        MonoliteBehaviour.__init__(self)
        self.dropped_items = []
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def drop_item(self, item, position, velocity=None):
        dropped_item = DroppedItem(item, position, velocity)
        dropped_item.position = position
        if velocity is not None:
            dropped_item.velocity = velocity
        self.dropped_items.append(dropped_item)
        print("Dropped item: {} at position {}".format(item.name, position))
        return dropped_item

    def draw(self, screen, camera):
        for item in self.dropped_items:
            screen.blit(item.item_instance.asset, item.position - camera.position)
