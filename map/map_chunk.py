import pygame
from settings import TILE_SIZE, CHUNK_SIZE

class Chunk:
    def __init__(self, pos):
        self.pos = pos
        self.tiles_layers = []

        self.render_cache = None
        self.collision_cache = None

    def _bake_collision(self):
        # Bake a collision box based on joint collision boxes
        collision_cache = None

        self.collision_cache = collision_cache
    
    def _bake_chunk(self, tilesets_multi):
        self.render_cache = pygame.Surface((CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE))
        self.render_cache.fill((0, 0, 0))

        H_FLIP = 0x80000000
        V_FLIP = 0x40000000
        D_FLIP = 0x20000000
        MASK_FLAGS = H_FLIP | V_FLIP | D_FLIP  # 0xE0000000, bit 28 ignorado en ortogonal

        for layer_matrix in self.tiles_layers:
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

                            self.render_cache.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))
                            
    def apply_diagonal_flip(self, tile_surf):
        tile_surf = pygame.transform.rotate(tile_surf, 270)
        tile_surf = pygame.transform.flip(tile_surf, True, False)
        return tile_surf
    