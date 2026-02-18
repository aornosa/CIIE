LAYERS = {
    "default": 0,
    "terrain": 1,
    "player": 2,
    "enemy": 3,
    "projectile": 4,
}

def get_layer_value(name):
    return LAYERS.get(name, 0)

def get_layer_name(value):
    for name, val in LAYERS.items():
        if val == value:
            return name
    return "None"