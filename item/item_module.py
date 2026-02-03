from core.object import Object


class Item(Object):
    def __init__(self, asset, position=(0, 0), rotation=0, scale=1, name="", description=""):
        super().__init__(asset, position, rotation, scale)
        self.name = name
        self.description = description
            