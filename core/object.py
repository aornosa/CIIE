import pygame
from settings import *

class Object:
    def __init__(self, asset, position=(0,0), rotation=0, scale=1):
        self.asset = pygame.image.load(asset).convert_alpha()
        self.position = pygame.Vector2(position)
        self.rotation = rotation
        self.scale = scale

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = pygame.Vector2(position)

    def get_rotation(self):
        return self.rotation

    def set_rotation(self, rotation):
        self.rotation = rotation

    def get_scale(self):
        return self.scale

    def set_scale(self, scale):
        self.scale = scale

    def draw(self, surface, camera):
        rotated_asset = pygame.transform.rotate(self.asset, self.rotation)

        # Scaling
        w, h = rotated_asset.get_size()
        scaled_asset = pygame.transform.scale(
            rotated_asset,
            (int(w * self.scale), int(h * self.scale))
        )

        # Screen position (centered)
        screen_pos = self.position - camera.position
        rect = scaled_asset.get_rect(center=screen_pos)

        surface.blit(scaled_asset, rect)