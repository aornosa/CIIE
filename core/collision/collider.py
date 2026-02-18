import pygame

from core.collision.collision_manager import CollisionManager


class Collider:
    def __init__(self, owner, rect, *, layer=0, tag=None, static=False):
        self.owner = owner
        self.rect = rect
        self.layer = layer
        self.tag = tag

        self._static = static

        CollisionManager.add_collider(self)

    @property
    def static(self):
        return self._static

    @static.setter
    def static(self, value):
        if self._static != value:
            self._static = value
            # Reinsert into the correct quadtree
            if value:
                CollisionManager.dynamic_colliders.discard(self)
                CollisionManager.active().dynamic_qtree.clear()
            else:
                CollisionManager.static_colliders.discard(self)
                CollisionManager.active().static_qtree.remove(self)
            CollisionManager.add_collider(self)


    def sync_with_owner(self, sync_position=True, sync_rotation=False, sync_scale=True):
        # Sync the collider's position with its owner's position
        if sync_position and hasattr(self.owner, 'position'):
            self.rect.x = self.owner.position[0]
            self.rect.y = self.owner.position[1]
        if sync_rotation and hasattr(self.owner, 'rotation'):
            pass
        if sync_scale and hasattr(self.owner, 'scale'):
            s = self.owner.scale
            self.rect.h = s * self.owner.asset.get_height() * 0.5
            self.rect.w = s * self.owner.asset.get_width() * 0.5

    def check_collision(self, layers=None, tags=None, include_self=False):
        return CollisionManager.get_collisions_active(self, layers=layers, tags=tags, include_self=include_self)