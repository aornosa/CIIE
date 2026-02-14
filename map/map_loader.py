from map import Map

class MapLoader:
    # Load map file
    @staticmethod
    def load_map(file_path) -> Map:
        pass

    # Save map file
    @staticmethod
    def save_map(map_object: Map, file_path):
        pass

    def __init__(self):
        self.active_chunks = {}
        self.chunks = []

    def get_active_chunks(self, camera, player):
        # Load every active chunk around the camera and player
        pass