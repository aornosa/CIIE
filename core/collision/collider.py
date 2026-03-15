from core.collision.collision_manager import CollisionManager

class Collider:
    def __init__(self, owner, rect, *, layer=0, tag=None, static=False):
        self.owner   = owner
        self.rect    = rect
        self.layer   = layer
        self.tag     = tag
        self._static = static
        CollisionManager.add_collider(self)

    @property
    def static(self): return self._static

    @static.setter
    def static(self, value):
        if self._static != value:
            self._static = value
            # Al cambiar de tipo, elimina del quadtree anterior y reinserta en el correcto
            if value:
                CollisionManager.dynamic_colliders.discard(self)
                CollisionManager.active().dynamic_qtree.clear()
            else:
                CollisionManager.static_colliders.discard(self)
                CollisionManager.active().static_qtree.remove(self)
            CollisionManager.add_collider(self)

    def sync_with_owner(self, sync_position=True, sync_rotation=False, sync_scale=True):
        pos_x = pos_y = None
        if hasattr(self.owner, 'position'):
            pos_x = self.owner.position[0]
            pos_y = self.owner.position[1]
            if sync_position:
                self.rect.x = pos_x
                self.rect.y = pos_y

        if sync_rotation and hasattr(self.owner, 'rotation'):
            pass

        # Alinea el collider con el sprite renderizado (ya escalado y con el mismo redondeo).
        # Rectangle guarda semiancho/semialto, por eso se divide entre 2.
        if sync_scale and hasattr(self.owner, 'scale'):
            if hasattr(self.owner, '_get_scaled_asset'):
                scaled = self.owner._get_scaled_asset()
                # Usa solo el area visible (no transparente) para evitar hitboxes infladas.
                vis = scaled.get_bounding_rect(min_alpha=1)
                if vis.width <= 0 or vis.height <= 0:
                    vis = scaled.get_rect()

                self.rect.w = vis.width / 2
                self.rect.h = vis.height / 2

                # Corrige el centro del collider si el contenido visible esta desplazado
                # dentro del sprite (padding transparente asimetrico).
                if sync_position and pos_x is not None and pos_y is not None:
                    off_x = vis.centerx - (scaled.get_width() / 2)
                    off_y = vis.centery - (scaled.get_height() / 2)
                    self.rect.x = pos_x + off_x
                    self.rect.y = pos_y + off_y
            else:
                s            = self.owner.scale
                self.rect.h  = s * self.owner.asset.get_height() * 0.5
                self.rect.w  = s * self.owner.asset.get_width()  * 0.5

    def check_collision(self, layers=None, tags=None, include_self=False):
        return CollisionManager.get_collisions_active(
            self, layers=layers, tags=tags, include_self=include_self)