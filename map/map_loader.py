import json
from settings import TILE_SIZE, CHUNK_SIZE
from map.map import Map
import pygame

class MapLoader:
    def __init__(self):
        self.active_chunks = {}
        #nuevo
        self.map = None
        
    # Load map file
    @staticmethod
    def load_map(file_path: str) -> Map:

        with open(file_path, 'r') as f:
            data_json = json.load(f)
        width = data_json['width'] 
        height = data_json['height'] 
        tiles_flat = data_json['layers'][0]['data'] 
        tiles_2d = [tiles_flat[i*width : (i+1)*width] for i in range(height)]
        mapa = Map(width, height)
        mapa.process_data(tiles_2d) 
        return mapa

    # Save map file
    @staticmethod
    def save_map(map_object: Map, file_path):
        pass

    def get_active_chunks(self, player,screen, camera_offset, chunk_radius):
        view_center_x = camera_offset[0] + screen.get_width() // 2
        view_center_y = camera_offset[1] + screen.get_height() // 2
        cx = (view_center_x // TILE_SIZE) // CHUNK_SIZE
        cy = (view_center_y // TILE_SIZE) // CHUNK_SIZE
        
        self.active_chunks.clear()
        for dx in range(-chunk_radius, chunk_radius + 1):
            for dy in range(-chunk_radius, chunk_radius + 1):
                chunk_pos = (cx + dx, cy + dy)
                self.active_chunks[chunk_pos] = self.map.get_chunk(chunk_pos)
        return self.active_chunks
    
    def draw_active_chunks(self, screen, camera_offset, tile_images, player=None, chunk_radius=4):
        if player:
             self.active_chunks= self.get_active_chunks(player,screen, camera_offset, chunk_radius)
        for chunk_pos, chunk in self.active_chunks.items():
            if not chunk.render_cache:
                chunk._bake_chunk(tile_images)
            chunk_screen_pos = (chunk.pos[0] * (CHUNK_SIZE * TILE_SIZE) - camera_offset[0],
                    chunk.pos[1] * (CHUNK_SIZE * TILE_SIZE) - camera_offset[1])
            screen.blit(chunk.render_cache, chunk_screen_pos)
    
    def load_tileset_to_dict(tileset_path, tile_size=(32,32)):
        sheet = pygame.image.load(tileset_path).convert_alpha()
        w, h = sheet.get_size()
        tile_images = {} 
        
        tile_id = 1
        for y in range(0, h, tile_size[1]):
            for x in range(0, w, tile_size[0]):
                rect = pygame.Rect(x, y, *tile_size)
                tile = sheet.subsurface(rect).convert_alpha()  
                tile_images[tile_id] = tile 
                tile_id += 1
        return tile_images 
