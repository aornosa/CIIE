import pygame
from core.collision.layers import LAYERS
from core.collision.quadtree import Rectangle
from settings import TILE_SIZE, CHUNK_SIZE
from core.collision.collider import Collider

class Chunk:
    def __init__(self, pos):
        self.pos = pos
        self.tiles_layers = []
        self.layer_names = []  

        self.full_cache = None  
        self.floor_only_cache = None 
        self.collision_cache = None
        self.has_buildings = False 
        self._baked_building_indices = None

    def _bake_collision(self):
        collision_cache = None
        self.collision_cache = collision_cache

    
    def _bake_chunk(self, tilesets_multi, building_layer_indices=None):
        if building_layer_indices is None:
            building_layer_indices = []
        self._baked_building_indices = tuple(building_layer_indices)

        size = (CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE)
        self.floor_only_cache = pygame.Surface(size, pygame.SRCALPHA)
        self.floor_only_cache.fill((0, 0, 0, 0))

        self.full_cache = pygame.Surface(size, pygame.SRCALPHA)
        self.full_cache.fill((0, 0, 0, 0))

        H_FLIP = 0x80000000
        V_FLIP = 0x40000000
        D_FLIP = 0x20000000
        MASK_FLAGS = H_FLIP | V_FLIP | D_FLIP 

        self.has_buildings = False
        for layer_idx, layer_matrix in enumerate(self.tiles_layers):
            target_surface = self.floor_only_cache if layer_idx not in building_layer_indices else self.full_cache

            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    raw_gid = layer_matrix[y][x]
                    if raw_gid != 0:
                        h_flip = bool(raw_gid & H_FLIP)
                        v_flip = bool(raw_gid & V_FLIP)
                        d_flip = bool(raw_gid & D_FLIP)
                        gid = raw_gid & ~MASK_FLAGS 

                        tile_surf = None
                        for firstgid, tile_dict in sorted(tilesets_multi.items(), reverse=True):
                            if gid >= firstgid:
                                local_id = gid - firstgid + 1
                                tile_surf = tile_dict.get(local_id)
                                break

                        if tile_surf:
                            if d_flip:
                                tile_surf = self.apply_diagonal_flip(tile_surf)
                            if h_flip or v_flip:
                                tile_surf = pygame.transform.flip(tile_surf, h_flip, v_flip)

                            pos = (x * TILE_SIZE, y * TILE_SIZE)
                            target_surface.blit(tile_surf, pos)
                            self.full_cache.blit(tile_surf, pos)
                            if layer_idx in building_layer_indices:
                                self.has_buildings = True
                            
    def apply_diagonal_flip(self, tile_surf):
        tile_surf = pygame.transform.rotate(tile_surf, 270)
        tile_surf = pygame.transform.flip(tile_surf, True, False)
        return tile_surf
    