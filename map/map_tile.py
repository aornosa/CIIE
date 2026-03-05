class Tile:
    def __init__(self, pos, tile_sheet, walkable=True, collision=False):
        self.position = pos
        self.tile_sheet = tile_sheet

        self.walkable = walkable
        self.collision = collision

    def __repr__(self):
        return f"Tile(x={self.position[0]}, y={self.position[[1]]}, tile_sheet='{self.tile_sheet}')"