from map_chunk import Chunk


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]

    def is_walkable(self, x, y):
        return self.tiles[y][x] == 0

    def set_tile(self, x, y, value):
        self.tiles[y][x] = value

    def get_tile(self, x, y):
        return self.tiles[y][x]

    def set_chunk(self, chunk: Chunk, chunk_pos):
        pass

    def get_chunk(self, chunk_pos) -> Chunk:
        pass