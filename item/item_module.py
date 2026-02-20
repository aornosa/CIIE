from core.object import Object


class Item(Object):
    def __init__(self, asset, item_id, name, item_type, **attributes):
        super().__init__(asset, (0, 0), 0, 1)

        self.id = item_id
        self.name = name
        self.type = item_type
        self.attributes = attributes
            