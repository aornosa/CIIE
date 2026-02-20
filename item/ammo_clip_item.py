from item.item_module import Item

class AmmoClip(Item):
    def __init__(self, asset, item_id, name, ammo_type, capacity):
        super().__init__(asset, item_id, name)
        self.ammo_type = ammo_type
        self.capacity = capacity