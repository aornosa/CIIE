import pygame

class CharacterController:
    def __init__(self, speed, character):
        self.character = character
        self.speed = speed
        self.velocity = pygame.Vector2(0, 0)

    def get_position(self):
        return self.character.position

    def move(self, direction, delta_time):
        # Normalize direction to prevent faster diagonal movement
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * self.speed
        self.character.position += self.velocity * delta_time

    def rotate(self, angle):
        self.character.rotation += angle