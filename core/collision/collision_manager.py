import pygame

from core.collision.quadtree import QuadTree
from core.monolite_behaviour import MonoliteBehaviour
from settings import ENABLE_COLLISION_DEBUG


class CollisionManager(MonoliteBehaviour):
    static_colliders = set()
    dynamic_colliders = set()

    _active = None
    static_dirty = True

    def __init__(self, world_bounds, camera=None, set_active=True):
        MonoliteBehaviour.__init__(self)
        self.world_bounds = world_bounds

        self.static_qtree = QuadTree(self.world_bounds, 4)
        self.dynamic_qtree = QuadTree(self.world_bounds, 4)

        if set_active:
            CollisionManager._active = self

        self.camera = camera

    @classmethod
    def set_active(cls, instance):
        cls._active = instance

    @classmethod
    def active(cls):
        if cls._active is None:
            raise RuntimeError("No active CollisionManager instance is set")
        return cls._active

    @classmethod
    def add_collider(cls, collider):
        if collider.static:
            cls.static_colliders.add(collider)
            cls.active().static_qtree.insert(collider)
            cls.static_dirty = True
            collider.sync_with_owner()
        else:
            cls.dynamic_colliders.add(collider)
            cls.active().dynamic_qtree.insert(collider)

    def update(self):
        self.dynamic_qtree.clear()
        for c in self.dynamic_colliders:
            # collider should be in bounds
            self.dynamic_qtree.insert(c)
            c.sync_with_owner() # TODO: Move later into character update loop

        if self.static_dirty:
            self.static_qtree.clear()
            for c in self.static_colliders:
                self.static_qtree.insert(c)
            self.static_dirty = False

        if ENABLE_COLLISION_DEBUG:
            self.draw_debug_boxes(pygame.display.get_surface(), self.camera)

    def draw_debug_boxes(self, surface, camera=None):
        self._draw_node(surface, self.dynamic_qtree,(255, 0, 255), camera)
        self._draw_node(surface, self.static_qtree, (255, 255, 0), camera)
        if self.dynamic_colliders:
            for c in self.dynamic_colliders:
                r = c.rect.to_rect()
                if camera is not None:
                    r = r.move(-camera.position[0], -camera.position[1])
                pygame.draw.rect(surface, (255, 0, 0), r, 1)

        if self.static_colliders:
            for c in self.static_colliders:
                r = c.rect.to_rect()
                if camera is not None:
                    r = r.move(-camera.position[0], -camera.position[1])
                pygame.draw.rect(surface, (0, 150, 255), r, 1)


    def _draw_node(self, surface: pygame.Surface, node: QuadTree, color, camera=None):
        r = node.boundary.to_rect()
        if camera is not None:
            r = r.move(-camera.position.x, -camera.position.y)
        pygame.draw.rect(surface, color, r, 1)
        if node.is_divided:
            for child in (node.northeast, node.northwest, node.southeast, node.southwest):
                if child:
                    self._draw_node(surface, child, color, camera)

    @classmethod
    def query_collider(cls, collider):
        return (cls.active().dynamic_qtree.query(collider.rect) +
                cls.active().static_qtree.query(collider.rect))

    @classmethod
    def get_collisions_active(cls, collider, *, layers=None, tags=None, include_self=False):
        return cls.active().get_collisions(collider, layers=layers, tags=tags, include_self=include_self)

    @classmethod
    def collides_any_active(cls, collider, *, layers=None, tags=None, include_self=False):
        return cls.active().collides_any(collider, layers=layers, tags=tags, include_self=include_self)

    def get_collisions(self, collider, *, layers=None, tags=None, include_self=False):
        results = []

        if collider.static:
            candidates = self.dynamic_qtree.query(collider.rect)
        else:
            candidates = (self.dynamic_qtree.query(collider.rect) +
                          self.static_qtree.query(collider.rect))

        for other in candidates:
            # Skip self unless explicitly included
            if not include_self and other is collider:
                continue

            # Layer filtering
            if layers is not None:
                if isinstance(layers, (list, tuple, set)):
                    if other.layer not in layers:
                        continue
                else:
                    if other.layer != layers:
                        continue

            # Tag filtering
            if tags is not None:
                if isinstance(tags, (list, tuple, set)):
                    if other.tag not in tags:
                        continue
                else:
                    if other.tag != tags:
                        continue

            # Narrow-phase precise check (rectangle intersection)
            if (
                    collider.rect.contains(other.rect)
                    or collider.rect.fully_contains(other.rect)
                    or other.rect.contains(collider.rect)
            ):
                results.append(other)

        return results

    def collides_any(self, collider, *, layers=None, tags=None, include_self=False):
        if collider.static:
            candidates = self.dynamic_qtree.query(collider.rect)
        else:
            candidates = (
                    self.dynamic_qtree.query(collider.rect) +
                    self.static_qtree.query(collider.rect)
            )

        #FIXME: Duplicated code
        for other in candidates:
            if not include_self and other is collider:
                continue

            if layers is not None:
                if isinstance(layers, (list, tuple, set)):
                    if other.layer not in layers:
                        continue
                else:
                    if other.layer != layers:
                        continue

            if tags is not None:
                if isinstance(tags, (list, tuple, set)):
                    if other.tag not in tags:
                        continue
                else:
                    if other.tag != tags:
                        continue

            if (
                    collider.rect.contains(other.rect)
                    or collider.rect.fully_contains(other.rect)
                    or other.rect.contains(collider.rect)
            ):
                return True

        return False