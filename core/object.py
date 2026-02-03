import pygame

class Object:
    def __init__(self,asset, position, rotation, scale=(40, 40)):
        self.asset = pygame.image.load(asset)
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
        rotated_asset = pygame.transform.rotate(self.asset, self.rotation)
        w, h = rotated_asset.get_size()
        new_w = int(w * self.scale)
        new_h = int(h * self.scale)
        scaled_asset = pygame.transform.scale(rotated_asset, (new_w, new_h))
        surface.blit(scaled_asset, self.position - camera.position)