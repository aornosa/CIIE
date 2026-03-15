import pygame
from core.collision.collision_manager import CollisionManager
from core.collision.layers import LAYERS

class CharacterController:
    def __init__(self, speed, character):
        self.character = character
        self.speed     = speed
        self.velocity  = pygame.Vector2(0, 0)

    def get_position(self):
        return self.character.position

    def move(self, direction, delta_time):
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * self.speed
        delta         = self.velocity * delta_time

        if not hasattr(self.character, "collider"):
            self.character.position += delta
            return

        coll    = self.character.collider
        old_pos = pygame.Vector2(self.character.position)
        coll.sync_with_owner()

        # Resolución de colisiones por eje separado para permitir deslizamiento en esquinas
        self.character.position.x += delta.x
        coll.sync_with_owner()
        if CollisionManager.collides_any_active(coll, layers=[LAYERS["terrain"]], include_self=False):
            self.character.position.x = old_pos.x
            coll.sync_with_owner()

        self.character.position.y += delta.y
        coll.sync_with_owner()
        if CollisionManager.collides_any_active(coll, layers=[LAYERS["terrain"]], include_self=False):
            self.character.position.y = old_pos.y
            coll.sync_with_owner()

    def rotate(self, angle):
        self.character.rotation += angle