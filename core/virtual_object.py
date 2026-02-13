import pygame

class VirtualObject:
    def __init__(self, position=(0, 0), rotation=0):
        self.position = pygame.Vector2(position)
        self.rotation = rotation

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = pygame.Vector2(position)

    def get_rotation(self):
        return self.rotation

    def set_rotation(self, rotation):
        self.rotation = rotation