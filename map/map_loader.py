import json
from settings import TILE_SIZE, CHUNK_SIZE
from map.map import Map
import pygame
from core.collision.collider import Collider
from core.collision.quadtree import Rectangle
from core.collision.layers import get_layer_value

class MapLoader:
    def __init__(self):
        self.active_chunks = {}
        self.map = None

    @staticmethod
    def load_map(file_path: str) -> dict:
        with open(file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def calculate_map_bounds(map_data: dict) -> tuple[float, float, float, float]:
        tile_size = map_data['tilewidth']
        min_tile_x, min_tile_y = float('inf'), float('inf')
        max_tile_x, max_tile_y = float('-inf'), float('-inf')

        for layer in map_data.get('layers', []):
            if 'chunks' not in layer:
                continue

            for chunk in layer['chunks']:
                c_x = chunk['x']
                c_y = chunk['y']
                c_w = chunk['width']
                chunk_data = chunk['data']

                for i, gid in enumerate(chunk_data):
                    if gid == 0:
                        continue

                    local_x = i % c_w
                    local_y = i // c_w
                    global_x = c_x + local_x
                    global_y = c_y + local_y

                    if global_x < min_tile_x:
                        min_tile_x = global_x
                    if global_x > max_tile_x:
                        max_tile_x = global_x
                    if global_y < min_tile_y:
                        min_tile_y = global_y
                    if global_y > max_tile_y:
                        max_tile_y = global_y

        if min_tile_x == float('inf'):
            return 0.0, 0.0, 0.0, 0.0

        real_offset_x = min_tile_x * tile_size
        real_offset_y = min_tile_y * tile_size
        real_width = (max_tile_x - min_tile_x + 1) * tile_size
        real_height = (max_tile_y - min_tile_y + 1) * tile_size
        return real_offset_x, real_offset_y, real_width, real_height
        
    @staticmethod
    def load_chunks_from_json(map_data, mapa):
        tile_layers = [layer for layer in map_data['layers'] if layer['type'] == 'tilelayer']
        
        for tile_layer in tile_layers:
            chunks = tile_layer['chunks']
            layer_name = tile_layer.get('name', '')

            for chunk_data in chunks:
                x = chunk_data['x']  
                y = chunk_data['y']
                width = chunk_data['width']
                height = chunk_data['height']
                tiles_flat = chunk_data['data']
                
                tiles_2d = [tiles_flat[i*width : (i+1)*width] for i in range(height)]
                
                cx = x // CHUNK_SIZE
                cy = y // CHUNK_SIZE
                
                chunk = mapa.get_chunk((cx, cy))

                chunk.layer_names.append(layer_name)

                layer_matrix = [[0] * CHUNK_SIZE for _ in range(CHUNK_SIZE)]
                for ly in range(height):
                    for lx in range(width):
                        layer_matrix[ly][lx] = tiles_2d[ly][lx]        
                chunk.tiles_layers.append(layer_matrix)
                print(f"Chunk ({cx},{cy}): layer_matrix non-zero GIDs: {sum(sum(1 for c in row if c!=0) for row in layer_matrix)}")
                print(f"Ejemplo GIDs: {layer_matrix[0][:5]}...")
                
    @staticmethod
    def load_colliders_from_json(map_data):
        for layer in map_data.get('layers', []):
            if layer.get('type') == 'objectgroup' and layer.get('name') == 'colliders':
                
                for obj in layer.get('objects', []):
                    tiled_x = obj['x']
                    tiled_y = obj['y']
                    width = obj['width']
                    height = obj['height']
                    
                    center_x = tiled_x + (width / 2)
                    center_y = tiled_y + (height / 2)
                    half_w = width / 2
                    half_h = height / 2

                    rect = Rectangle(center_x, center_y, half_h, half_w)
                    
                    Collider(
                        owner=None, 
                        rect=rect, 
                        layer=get_layer_value("terrain"), 
                        static=True
                    )

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
    
    def draw_active_chunks(self, screen, camera_offset, tile_images, player=None, chunk_radius=2):
        if player:
            self.active_chunks = self.get_active_chunks(player, screen, camera_offset, chunk_radius)

        building_layer_indices = []
        reference_chunk = None
        for chunk in self.active_chunks.values():
            if chunk and chunk.tiles_layers:
                reference_chunk = chunk
            if chunk.layer_names:
                for idx, name in enumerate(chunk.layer_names):
                    lname = (name or "").lower()
                    if "building" in lname or "edificio" in lname or "tile layer 2" in lname or "build" in lname:
                        building_layer_indices.append(idx)
                break
        if not building_layer_indices:
            if reference_chunk and len(reference_chunk.tiles_layers) > 1:
                building_layer_indices = [1]

        player_screen_pos = None
        patch_rect = None
        if player:
            player_screen_pos = (int(player.position[0] - camera_offset[0]),
                                 int(player.position[1] - camera_offset[1]))

            self.patch_radius = getattr(self, 'patch_radius', TILE_SIZE * 1.5)  

            patch_size = self.patch_radius * 2
            patch_radius = self.patch_radius
            patch_rect = pygame.Rect(player_screen_pos[0] - patch_radius, player_screen_pos[1] - patch_radius, patch_size, patch_size)

            if getattr(self, '_patch_surface', None) is None or self._patch_surface.get_size() != (patch_size, patch_size):
                self._patch_surface = pygame.Surface((patch_size, patch_size), pygame.SRCALPHA)
            patch_surface = self._patch_surface
            patch_surface.fill((0, 0, 0, 0))

            cache_key = ('patch', patch_radius)
            if getattr(self, '_patch_mask_cache', None) is None:
                self._patch_mask_cache = {}
            if cache_key not in self._patch_mask_cache:
                self._patch_mask_cache[cache_key] = self._build_patch_mask(
                    (patch_size, patch_size),
                    (patch_radius, patch_radius),
                    patch_radius,
                )

            self._patch_mask = self._patch_mask_cache[cache_key]

        expected_building_signature = tuple(building_layer_indices)

        for chunk_pos, chunk in self.active_chunks.items():
            if (not chunk.full_cache) or getattr(chunk, "_baked_building_indices", None) != expected_building_signature:
                chunk._bake_chunk(tile_images, building_layer_indices=building_layer_indices)
            chunk_screen_pos = (chunk.pos[0] * (CHUNK_SIZE * TILE_SIZE) - camera_offset[0],
                                chunk.pos[1] * (CHUNK_SIZE * TILE_SIZE) - camera_offset[1])
            screen.blit(chunk.full_cache, chunk_screen_pos)

            if patch_rect and getattr(chunk, 'floor_only_cache', None):
                chunk_rect = pygame.Rect(chunk_screen_pos[0], chunk_screen_pos[1], CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE)
                if chunk_rect.colliderect(patch_rect):
                    intersect = chunk_rect.clip(patch_rect)
                    src_x = intersect.x - chunk_rect.x
                    src_y = intersect.y - chunk_rect.y
                    src_rect = pygame.Rect(src_x, src_y, intersect.w, intersect.h)
                    dst_x = intersect.x - patch_rect.x
                    dst_y = intersect.y - patch_rect.y
                    patch_surface.blit(chunk.floor_only_cache, (dst_x, dst_y), src_rect)

        if patch_rect and getattr(self, '_patch_mask', None) is not None:
            patch_surface.blit(self._patch_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(patch_surface, patch_rect.topleft)
                
    def _draw_buildings_to_surface(self, chunk, surface, offset, tilesets_multi, building_layer_indices):
        """Draw building tiles directly to the surface for masking."""
        H_FLIP = 0x80000000
        V_FLIP = 0x40000000
        D_FLIP = 0x20000000
        MASK_FLAGS = H_FLIP | V_FLIP | D_FLIP

        for layer_idx, layer_matrix in enumerate(chunk.tiles_layers):
            if layer_idx in building_layer_indices:
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
                                    tile_surf = pygame.transform.rotate(tile_surf, 270)
                                    tile_surf = pygame.transform.flip(tile_surf, True, False)
                                if h_flip or v_flip:
                                    tile_surf = pygame.transform.flip(tile_surf, h_flip, v_flip)

                                surface.blit(tile_surf, (offset[0] + x * TILE_SIZE, offset[1] + y * TILE_SIZE))
    
    @staticmethod
    def _build_patch_mask(size, center, radius):
        mask = pygame.Surface(size, pygame.SRCALPHA)
        mask.fill((255, 255, 255, 0))

        # Solid circle (opaque inside)
        pygame.draw.circle(mask, (255, 255, 255, 255), center, radius)

        return mask

    @staticmethod
    def load_tileset_to_dict(tileset_path, tile_size=(32,32)):
        sheet = pygame.image.load(tileset_path).convert_alpha()
        w, h = sheet.get_size()
        tile_images = {} 
        
        tile_id = 1
        for y in range(0, h, tile_size[1]):
            for x in range(0, w, tile_size[0]):
                rect = pygame.Rect(x, y, *tile_size)
                tile = sheet.subsurface(rect).convert_alpha()  
                #scaled_tile = pygame.transform.smoothscale(tile, (16, 16))
                tile_images[tile_id] = tile
                tile_id += 1
        return tile_images 
    
    @staticmethod
    def load_all_tilesets(map_json):
        tilesets_multi = {}
        png_cache = {} 
        
        tsx_to_png = {
            '../tilesets/1.tsx': '1.png',
            '../tilesets/2.tsx': '2.png',
            '../tilesets/3.tsx': '3.png',
            '../tilesets/4.tsx': '4.png',
            '../tilesets/5.tsx': '5.png',
            '../tilesets/6.tsx': '6.png',
            '../tilesets/7.tsx': '7.png',
            '../tilesets/8.tsx': '8.png',
            '../tilesets/9.tsx': '9.png',
            '../tilesets/10.tsx': '10.png',
            '../tilesets/11.tsx': '11.png',
            '../tilesets/12.tsx': '12.png'
        }
        
        for ts in map_json['tilesets']:
            if 'source' in ts:
                png_name = tsx_to_png[ts['source']]
                firstgid = ts['firstgid']
                
                if png_name not in png_cache:
                    png_cache[png_name] = MapLoader.load_tileset_to_dict(f'assets/tilesets/{png_name}')
                
                tilesets_multi[firstgid] = png_cache[png_name]  
                print("✅ CARGADOS tilesets_multi keys:", list(tilesets_multi.keys()))
        return tilesets_multi