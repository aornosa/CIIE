import pygame
from settings import TILE_SIZE, CHUNK_SIZE

class Chunk:
    chunk_width = 16
    chunk_height = 16

    def __init__(self, pos):
        self.pos = pos
        self.tiles = [[0 for _ in range(self.chunk_width)] for _ in range(self.chunk_height)]

        self.render_cache = None
        self.collision_cache = None

    def _bake_collision(self):
        # Bake a collision box based on joint collision boxes
        collision_cache = None

        self.collision_cache = collision_cache

    def _bake_chunk(self, tile_images):
        # Tile optimization: Combine adjacent tiles into larger rectangles for efficient rendering
        #render_cache = None
        #self.render_cache = render_cache
        self.render_cache = pygame.Surface((16*TILE_SIZE, 16*TILE_SIZE))

        for y in range(16):
            for x in range(16):
                tile_id = self.tiles[y][x]
                if tile_id:
                    img = tile_images[tile_id]
                    self.render_cache.blit(img, (x*TILE_SIZE, y*TILE_SIZE))
    
    def draw_chunk(self, surface, camera_pos, tile_images):
        """Draw optimizado con cache"""
        if self.render_cache is None:
            self._bake_chunk(tile_images)
        
        screen_x = self.pos[0] * 16 * TILE_SIZE - camera_pos.x
        screen_y = self.pos[1] * 16 * TILE_SIZE - camera_pos.y
        
        surface.blit(self.render_cache, (screen_x, screen_y))