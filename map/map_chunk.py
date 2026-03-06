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
        
        for layer_matrix in self.tiles_layers: 
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    gid = layer_matrix[y][x]  
                    if gid != 0:
                        tile_surf = None
                        for firstgid, tile_dict in sorted(tilesets_multi.items(), reverse=True):
                            if gid >= firstgid:
                                local_id = gid - firstgid + 1  
                                tile_surf = tile_dict.get(local_id)
                                break
                        
                        if tile_surf:
                            self.render_cache.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))
                            
    