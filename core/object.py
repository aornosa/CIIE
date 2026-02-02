import pygame

class Object:
    def __init__(self,asset, position, rotation, scale=(40, 40)):
        self.asset = pygame.transform.scale(pygame.image.load(asset), scale)
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

    def draw(self, surface, camera):
        scaled_asset = pygame.transform.scale(self.asset, self.scale)
        rotated_asset = pygame.transform.rotate(scaled_asset, self.rotation)
        surface.blit(rotated_asset, self.position - camera.position)