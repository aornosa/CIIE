from item.item_module import Item

class AmmoClipItem(Item):
    def __init__(self, asset, position=(0, 0), rotation=0, scale=1, name="", description="", ammo_type="", capacity=0):
        super().__init__(asset, position, rotation, scale, name, description)
        self.ammo_type = ammo_type
        self.capacity = capacity