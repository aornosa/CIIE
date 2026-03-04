from map.map_chunk import Chunk
from settings import CHUNK_SIZE

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]
        self.chunks = {}

    def is_walkable(self, x, y):
        return self.tiles[y][x] == 0

    def set_tile(self, x, y, value):
        self.tiles[y][x] = value

    def get_tile(self, x, y):
        return self.tiles[y][x]

    def set_chunk(self, chunk: Chunk, chunk_pos):
        self.chunks[chunk_pos] = chunk

    def get_chunk(self, chunk_pos) -> Chunk:
        if chunk_pos not in self.chunks:
            self.chunks[chunk_pos] = Chunk(chunk_pos)
        return self.chunks[chunk_pos]

