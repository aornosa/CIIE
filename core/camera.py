import pygame

class Camera:
    def __init__(self, position=(0, 0)):
        self.position = pygame.Vector2(position)
        self.zoom = 1.0

    def set_position(self, position):
        self.position = pygame.Vector2(position)

    def move(self, offset):
        self.position += pygame.Vector2(offset)

    def set_zoom(self, zoom):
        self.zoom = zoom

    def get_zoom(self):
        return self.zoom
