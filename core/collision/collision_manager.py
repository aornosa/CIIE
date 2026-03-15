import pygame
from core.collision.layers import LAYERS, get_layer_name
from core.collision.quadtree import QuadTree
from core.monolite_behaviour import MonoliteBehaviour
from settings import ENABLE_COLLISION_DEBUG

class CollisionManager(MonoliteBehaviour):
    static_colliders  = set()
    dynamic_colliders = set()

    _active      = None
    static_dirty = True

    def __init__(self, world_bounds, camera=None, set_active=True):
        MonoliteBehaviour.__init__(self)
        self.world_bounds = world_bounds

        self.static_qtree  = QuadTree(self.world_bounds, 4)
        self.dynamic_qtree = QuadTree(self.world_bounds, 4)

        if set_active:
            CollisionManager._active = self

        self.camera = camera

    @classmethod
    def set_active(cls, instance): cls._active = instance

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
        # Reconstruye el quadtree dinámico cada frame con las posiciones actualizadas
        self.dynamic_qtree.clear()
        for c in self.dynamic_colliders:
            self.dynamic_qtree.insert(c)
            c.sync_with_owner()  # TODO: Move later into character update loop

        # El quadtree estático solo se reconstruye cuando algo cambia
        if self.static_dirty:
            self.static_qtree.clear()
            for c in self.static_colliders:
                self.static_qtree.insert(c)
            self.static_dirty = False

        if ENABLE_COLLISION_DEBUG:
            self.draw_debug_boxes(pygame.display.get_surface(), self.camera)

    def draw_debug_boxes(self, surface, camera=None):
        self._draw_node(surface, self.dynamic_qtree, (255, 0, 255), camera)
        self._draw_node(surface, self.static_qtree,  (255, 255, 0), camera)
        for c in self.dynamic_colliders:
            r = c.rect.to_rect()
            if camera is not None:
                r = r.move(-camera.position[0], -camera.position[1])
            pygame.draw.rect(surface, (255, 0, 0), r, 1)
            self._draw_collider_label(surface, r, c)
        for c in self.static_colliders:
            r = c.rect.to_rect()
            if camera is not None:
                r = r.move(-camera.position[0], -camera.position[1])
            pygame.draw.rect(surface, (0, 150, 255), r, 1)
            self._draw_collider_label(surface, r, c)

    # Dibuja recursivamente los nodos del quadtree como rectángulos de debug
    def _draw_node(self, surface: pygame.Surface, node: QuadTree, color, camera=None):
        r = node.boundary.to_rect()
        if camera is not None:
            r = r.move(-camera.position.x, -camera.position.y)
        pygame.draw.rect(surface, color, r, 1)
        if node.is_divided:
            for child in (node.northeast, node.northwest, node.southeast, node.southwest):
                if child:
                    self._draw_node(surface, child, color, camera)

    @staticmethod
    def _draw_collider_label(surface: pygame.Surface, rect: pygame.Rect, collider):
        text = f"L:{get_layer_name(collider.layer)}"
        img  = pygame.font.SysFont("consolas", 16).render(text, True, (255, 255, 255))
        pad  = 2
        bg   = img.get_rect(topleft=(rect.x, rect.y - img.get_height() - pad))
        bg.inflate_ip(pad * 2, pad * 2)
        pygame.draw.rect(surface, (0, 0, 0), bg)
        surface.blit(img, (bg.x + pad, bg.y + pad))

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

    def _get_candidates(self, collider):
        # Los colisores estáticos solo colisionan contra dinámicos, no entre sí
        if collider.static:
            return self.dynamic_qtree.query(collider.rect)
        return (self.dynamic_qtree.query(collider.rect) +
                self.static_qtree.query(collider.rect))

    def _filter_candidates(self, collider, candidates, layers, tags, include_self):
        for other in candidates:
            if not include_self and other is collider:
                continue
            if layers is not None:
                target = layers if isinstance(layers, (list, tuple, set)) else (layers,)
                if other.layer not in target:
                    continue
            if tags is not None:
                target = tags if isinstance(tags, (list, tuple, set)) else (tags,)
                if other.tag not in target:
                    continue
            # Fase estrecha: comprueba intersección real tras el filtrado broadphase del quadtree
            if (collider.rect.contains(other.rect)
                    or collider.rect.fully_contains(other.rect)
                    or other.rect.contains(collider.rect)):
                yield other

    def get_collisions(self, collider, *, layers=None, tags=None, include_self=False):
        return list(self._filter_candidates(
            collider, self._get_candidates(collider), layers, tags, include_self))

    def collides_any(self, collider, *, layers=None, tags=None, include_self=False):
        return next(self._filter_candidates(
            collider, self._get_candidates(collider), layers, tags, include_self), None) is not None