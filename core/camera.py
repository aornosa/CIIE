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

    def clamp_to_bounds(self, offset_x, offset_y, width, height, screen_width, screen_height, padding=0):
        if width > screen_width:
            min_x = offset_x + padding
            max_x = offset_x + width - screen_width
            self.position.x = max(min_x, min(self.position.x, max_x))
        else:
            self.position.x = offset_x

        if height > screen_height:
            min_y = offset_y + padding
            max_y = offset_y + height - screen_height
            self.position.y = max(min_y, min(self.position.y, max_y))
        else:
            self.position.y = offset_y
