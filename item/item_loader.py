import json
import copy
from item.item_module import Item

_items_cache = {}


def load_items(path="assets/items/items.json"):
    """
    Carga el JSON y crea instancias de Item (o subclases específicas).
    No vuelve a crear items ya presentes en _items_cache.
    """
    global _items_cache
    with open(path, 'r', encoding='utf-8') as f:
        items_data = json.load(f)

    for key, info in items_data.items():
        name = info.get("name", key)
        if name in _items_cache:
            continue

        item_type = info.get("type")
        if item_type == "ammo":
            # Caso específico para ammo; ajusta los argumentos según tu clase real
            try:
                from item.ammo_clip_item import AmmoClip
                item = AmmoClip(
                    info.get("asset"),
                    info.get("name"),
                    info.get("damage"),
                    info.get("ammo_type")
                )
            except Exception:
                # Si falla, caer a Item genérico (evita romper la carga)
                item = Item(info)
        else:
            # fallback genérico
            item = Item(info)

        _items_cache[name] = item

def get_item(name, as_copy=True):
    item = _items_cache.get(name)
    if item is None:
        return None
    return copy.deepcopy(item) if as_copy else item

def clear_cache():
    _items_cache.clear()
