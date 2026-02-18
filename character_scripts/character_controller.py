import pygame

from core.collision.collision_manager import CollisionManager
from core.collision.layers import LAYERS


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
        delta = self.velocity * delta_time

        if not hasattr(self.character, "collider"):
            self.character.position += delta
            return

        coll = self.character.collider
        old_pos = pygame.Vector2(self.character.position)

        coll.sync_with_owner()

        # Handle x axis
        self.character.position = pygame.Vector2(old_pos.x + delta.x, old_pos.y)
        coll.sync_with_owner()

        if CollisionManager.collides_any_active(coll, layers=[LAYERS["terrain"]], include_self=False):
            self.character.position = old_pos
            coll.sync_with_owner()

        # Handle y axis
        current_x = self.character.position.x
        self.character.position = pygame.Vector2(current_x, old_pos.y + delta.y)
        coll.sync_with_owner()

        if CollisionManager.collides_any_active(coll, layers=[LAYERS["terrain"]], include_self=False):
            self.character.position = pygame.Vector2(current_x, old_pos.y)
            coll.sync_with_owner()

    def rotate(self, angle):
        self.character.rotation += angle