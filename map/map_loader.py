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
    def load_chunks_from_json(map_data, mapa):
        tile_layers = [layer for layer in map_data['layers'] if layer['type'] == 'tilelayer']
        for tile_layer in tile_layers:
            chunks     = tile_layer['chunks']
            layer_name = tile_layer.get('name', '')
            for chunk_data in chunks:
                x          = chunk_data['x']
                y          = chunk_data['y']
                width      = chunk_data['width']
                height     = chunk_data['height']
                tiles_flat = chunk_data['data']
                tiles_2d   = [tiles_flat[i*width:(i+1)*width] for i in range(height)]
                cx         = x // CHUNK_SIZE
                cy         = y // CHUNK_SIZE
                chunk      = mapa.get_chunk((cx, cy))
                chunk.layer_names.append(layer_name)
                layer_matrix = [[0] * CHUNK_SIZE for _ in range(CHUNK_SIZE)]
                for ly in range(height):
                    for lx in range(width):
                        layer_matrix[ly][lx] = tiles_2d[ly][lx]
                chunk.tiles_layers.append(layer_matrix)

    @staticmethod
    def load_colliders_from_json(map_data, offset_x=0, offset_y=0) -> dict:
        """
        Carga todos los colliders de la capa 'colliders'.
        offset_x/offset_y trasladan las coordenadas del .tmj al espacio del juego.
        Devuelve dict con colliders de puerta: {'door_north': Collider, 'door_exit': Collider}
        """
        door_colliders = {}

        for layer in map_data.get('layers', []):
            if layer.get('type') == 'objectgroup' and layer.get('name') == 'colliders':
                objects = layer.get('objects', [])
                for obj in objects:
                    # Aplica offset para convertir coordenadas Tiled → coordenadas del juego
                    world_x = obj['x'] + offset_x
                    world_y = obj['y'] + offset_y
                    width   = obj['width']
                    height  = obj['height']

                    center_x = world_x + width  / 2
                    center_y = world_y + height / 2
                    half_w   = width  / 2
                    half_h   = height / 2

                    rect     = Rectangle(center_x, center_y, half_h, half_w)
                    collider = Collider(
                        object(), rect,
                        layer=get_layer_value("terrain"),
                        static=True
                    )

                    for prop in obj.get('properties', []):
                        if prop.get('name') == 'type':
                            door_colliders[prop['value']] = collider

                print(f"✅ Cargados {len(objects)} colliders estáticos desde Tiled.")
                break

        return door_colliders

    @staticmethod
    def save_map(map_object: Map, file_path):
        pass

    def get_active_chunks(self, player, screen, camera_offset, chunk_radius):
        view_center_x = camera_offset[0] + screen.get_width()  // 2
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
        for chunk in self.active_chunks.values():
            if chunk.layer_names:
                for idx, name in enumerate(chunk.layer_names):
                    lname = (name or "").lower()
                    if "building" in lname or "edificio" in lname or "tile layer 2" in lname:
                        building_layer_indices.append(idx)
                break
        if not building_layer_indices:
            first = next(iter(self.active_chunks.values()), None)
            if first and len(first.tiles_layers) > 1:
                building_layer_indices = [1]

        if getattr(self, '_buildings_surface', None) is None or \
                self._buildings_surface.get_size() != screen.get_size():
            self._buildings_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        buildings_surface = self._buildings_surface
        buildings_surface.fill((0, 0, 0, 0))

        player_screen_pos = None
        if player:
            player_screen_pos = (int(player.position[0] - camera_offset[0]),
                                 int(player.position[1] - camera_offset[1]))
            self.building_mask_radius      = getattr(self, 'building_mask_radius', TILE_SIZE * 1.5)
            self.building_mask_inner_alpha = getattr(self, 'building_mask_inner_alpha', 80)
            cache_key = (self.building_mask_radius, self.building_mask_inner_alpha)
            if getattr(self, '_building_mask_cache', None) is None:
                self._building_mask_cache = {}
            if cache_key not in self._building_mask_cache:
                diameter = int(self.building_mask_radius * 2)
                self._building_mask_cache[cache_key] = self._build_building_mask(
                    (diameter, diameter),
                    (int(self.building_mask_radius), int(self.building_mask_radius)),
                    self.building_mask_radius,
                    self.building_mask_inner_alpha,
                )
            self._building_mask = self._building_mask_cache[cache_key]

        for chunk_pos, chunk in self.active_chunks.items():
            if not chunk.render_cache:
                chunk._bake_chunk(tile_images, building_layer_indices=building_layer_indices)
            chunk_screen_pos = (chunk.pos[0] * (CHUNK_SIZE * TILE_SIZE) - camera_offset[0],
                                chunk.pos[1] * (CHUNK_SIZE * TILE_SIZE) - camera_offset[1])
            screen.blit(chunk.render_cache, chunk_screen_pos)
            if getattr(chunk, 'has_buildings', False) and getattr(chunk, 'building_cache', None):
                buildings_surface.blit(chunk.building_cache, chunk_screen_pos)

        if player_screen_pos is not None and getattr(self, '_building_mask', None) is not None:
            mask_top_left = (int(player_screen_pos[0] - self.building_mask_radius),
                             int(player_screen_pos[1] - self.building_mask_radius))
            buildings_surface.blit(self._building_mask, mask_top_left,
                                   special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(buildings_surface, (0, 0))

    def _build_building_mask(self, size, center, radius, inner_alpha):
        mask = pygame.Surface(size, pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        pygame.draw.circle(mask, (255, 255, 255, inner_alpha), center, radius)
        dot_spacing    = max(8, radius // 16)
        max_dot_radius = max(1, dot_spacing // 2)
        ring_inner     = radius * 0.7
        ring_outer     = radius
        cx, cy = center
        for y in range(int(cy - radius), int(cy + radius), dot_spacing):
            for x in range(int(cx - radius), int(cx + radius), dot_spacing):
                dx   = x - cx
                dy   = y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if ring_inner < dist < ring_outer:
                    t          = (dist - ring_inner) / (ring_outer - ring_inner)
                    dot_alpha  = int(inner_alpha + (255 - inner_alpha) * t)
                    dot_radius = int(max_dot_radius * (1 - t) * 0.75) + 1
                    pygame.draw.circle(mask, (255, 255, 255, dot_alpha), (x, y), dot_radius)
        return mask

    @staticmethod
    def load_tileset_to_dict(tileset_path, tile_size=(32, 32)):
        sheet = pygame.image.load(tileset_path).convert_alpha()
        w, h  = sheet.get_size()
        tile_images = {}
        tile_id = 1
        for y in range(0, h, tile_size[1]):
            for x in range(0, w, tile_size[0]):
                rect = pygame.Rect(x, y, *tile_size)
                tile_images[tile_id] = sheet.subsurface(rect).convert_alpha()
                tile_id += 1
        return tile_images

    @staticmethod
    def load_all_tilesets(map_json):
        tilesets_multi = {}
        png_cache      = {}
        tsx_to_png = {
            '../tilesets/1.tsx':  '1.png',  '../tilesets/2.tsx':  '2.png',
            '../tilesets/3.tsx':  '3.png',  '../tilesets/4.tsx':  '4.png',
            '../tilesets/5.tsx':  '5.png',  '../tilesets/6.tsx':  '6.png',
            '../tilesets/7.tsx':  '7.png',  '../tilesets/8.tsx':  '8.png',
            '../tilesets/9.tsx':  '9.png',  '../tilesets/10.tsx': '10.png',
            '../tilesets/11.tsx': '11.png', '../tilesets/12.tsx': '12.png',
        }
        for ts in map_json['tilesets']:
            if 'source' in ts:
                png_name = tsx_to_png.get(ts['source'])
                if png_name is None:
                    continue
                firstgid = ts['firstgid']
                if png_name not in png_cache:
                    png_cache[png_name] = MapLoader.load_tileset_to_dict(
                        f'assets/tilesets/{png_name}')
                tilesets_multi[firstgid] = png_cache[png_name]
        return tilesets_multi