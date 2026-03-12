import pygame
from core.collision.layers import LAYERS
from core.collision.quadtree import Rectangle
from settings import TILE_SIZE, CHUNK_SIZE
from core.collision.collider import Collider

class Chunk:
    def __init__(self, pos):
        self.pos = pos
        self.tiles_layers = []
        self.layer_names = []  # Optional: store layer names to differentiate terrain vs buildings

        self.render_cache = None
        self.building_cache = None
        self.collision_cache = None
        self.has_buildings = False  # cache whether this chunk has any building tiles

    def _bake_collision(self):
        # Bake a collision box based on joint collision boxes
        collision_cache = None
        self.collision_cache = collision_cache

    
    def _bake_chunk(self, tilesets_multi, building_layer_indices=None):
        """Bake the chunk into surfaces.

        - `render_cache` contains all layers except the building layer(s).
        - `building_cache` contains only the building layer(s) so we can apply a transparency mask around the player.
        """
        if building_layer_indices is None:
            building_layer_indices = []

        size = (CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE)
        self.render_cache = pygame.Surface(size, pygame.SRCALPHA)
        self.render_cache.fill((0, 0, 0, 0))

        self.building_cache = pygame.Surface(size, pygame.SRCALPHA)
        self.building_cache.fill((0, 0, 0, 0))

        #self._bake_collision()

        H_FLIP = 0x80000000
        V_FLIP = 0x40000000
        D_FLIP = 0x20000000
        MASK_FLAGS = H_FLIP | V_FLIP | D_FLIP  # 0xE0000000, bit 28 ignorado en ortogonal

        self.has_buildings = False
        for layer_idx, layer_matrix in enumerate(self.tiles_layers):
            target_surface = self.building_cache if layer_idx in building_layer_indices else self.render_cache

            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    raw_gid = layer_matrix[y][x]
                    if raw_gid != 0:
                        # Extraer flags ANTES de limpiar
                        h_flip = bool(raw_gid & H_FLIP)
                        v_flip = bool(raw_gid & V_FLIP)
                        d_flip = bool(raw_gid & D_FLIP)
                        gid = raw_gid & ~MASK_FLAGS  # Limpia flags para buscar tile base

                        tile_surf = None
                        for firstgid, tile_dict in sorted(tilesets_multi.items(), reverse=True):
                            if gid >= firstgid:
                                local_id = gid - firstgid + 1
                                tile_surf = tile_dict.get(local_id)
                                break

                        if tile_surf:
                            # Aplicar transforms: diagonal PRIMERO (swap + rot), luego flips
                            if d_flip:
                                tile_surf = self.apply_diagonal_flip(tile_surf)
                                # IMPORTANTE: swap flags post-diagonal
                                #h_flip, v_flip = v_flip, h_flip  # X/Y se invierten[web:39]
                            if h_flip or v_flip:
                                tile_surf = pygame.transform.flip(tile_surf, h_flip, v_flip)

                            target_surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))
                            if target_surface is self.building_cache:
                                self.has_buildings = True
                            
    def apply_diagonal_flip(self, tile_surf):
        tile_surf = pygame.transform.rotate(tile_surf, 270)
        tile_surf = pygame.transform.flip(tile_surf, True, False)
        return tile_surf
    