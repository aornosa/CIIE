import pygame

from core.collision.quadtree import QuadTree
from core.monolite_behaviour import MonoliteBehaviour



class CollisionManager(MonoliteBehaviour):
    colliders = []

    def __init__(self, world_bounds, camera=None):
        MonoliteBehaviour.__init__(self)
        self.world_bounds = world_bounds
        self.quadtree = QuadTree(self.world_bounds, 4)

        self.camera = camera

    def update(self):
        self.quadtree.clear()
        for c in self.colliders:
            # make sure collider rect is inside world bounds; you may want to clamp or expand bounds instead
            self.quadtree.insert(c)
            c.sync_with_owner() # FIXME: Move later into character update loop
        self.draw_debug_boxes(pygame.display.get_surface(), self.camera)

    def draw_debug_boxes(self, surface, camera=None, color=(255, 0, 255)):
        self._draw_node(surface, self.quadtree, color, camera)
        if self.colliders:
            for c in self.colliders:
                r = c.rect.to_rect()
                if camera is not None:
                    r = r.move(-camera.position[0], -camera.position[1])
                pygame.draw.rect(surface, (255, 0, 0), r, 1)


    def _draw_node(self, surface: pygame.Surface, node: QuadTree, color, camera=None):
        r = node.boundary.to_rect()
        if camera is not None:
            r = r.move(-camera.position.x, -camera.position.y)
        pygame.draw.rect(surface, color, r, 1)
        if node.is_divided:
            for child in (node.northeast, node.northwest, node.southeast, node.southwest):
                if child:
                    self._draw_node(surface, child, color, camera)


    def query_colliders(self, collider):
        return self.quadtree.query(collider.rect)


    def get_collisions(self, collider, *, layers=None, tags=None, include_self=False):
        result = []
        seen = set()

        my_rect = collider.rect.to_rect()

        for rect in self.quadtree.query(collider.rect):
            other = self._rect_to_collider.get(id(rect))
            if other is None:
                continue

            if not include_self and other is collider:
                continue

            if layers is not None and other.layer not in layers:
                continue

            if tags is not None and other.tag not in tags:
                continue

            if my_rect.colliderect(other.rect.to_rect()):
                oid = id(other)
                if oid not in seen:
                    seen.add(oid)
                    result.append(other)

        return result

    def collides_any(self, collider, *, layers=None, tags=None, include_self=False):
        """Returns True if `collider` collides with at least one other collider."""
        my_rect = collider.rect.to_rect()

        for rect in self.quadtree.query(collider.rect):
            other = self._rect_to_collider.get(id(rect)) #FIXME: Retrieve collider
            if other is None:
                continue

            if not include_self and other is collider:
                continue

            if layers is not None and other.layer not in layers:
                continue

            if tags is not None and other.tag not in tags:
                continue

            if my_rect.colliderect(other.rect.to_rect()):
                return True

        return False