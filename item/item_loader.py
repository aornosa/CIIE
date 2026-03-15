import json
import pygame.image
from core.monolite_behaviour import MonoliteBehaviour
from item.item_type_data import ItemDefinition, AmmoData

class ItemRegistry(MonoliteBehaviour):
    _items: dict[str, ItemDefinition] = {}

    def __init__(self):
        super().__init__()

    def start(self):
        self.load("assets/items/item_data.json")

    @classmethod
    def load(cls, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        for item_id, raw in data.items():
            item = ItemDefinition(
                id=item_id,
                asset=pygame.transform.scale(
                    pygame.image.load(raw["asset"]), (50, 50)).convert_alpha(),
                name=raw["name"],
                description=raw["description"],
                type=raw["type"],
                ammo=AmmoData(**raw["ammo"]) if "ammo" in raw else None,
                effect=raw.get("effect"),
                cooldown=raw.get("cooldown", 0.0),
                reusable=raw.get("reusable", False),
            )
            cls._items[item_id] = item

    @classmethod
    def get(cls, item_id: str) -> ItemDefinition:
        if item_id not in cls._items:
            raise ValueError(f"Item ID '{item_id}' not found in registry.")
        return cls._items[item_id]