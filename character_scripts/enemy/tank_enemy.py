"""
TankEnemy
---------
Un enemigo grande, lento y con mucha vida.
Todos los parámetros son configurables en el constructor.
"""
from character_scripts.enemy.enemy_base import Enemy


class TankEnemy(Enemy):
    # ── Parámetros por defecto — cámbialo aquí o en el constructor ──────────────
    DEFAULT_HEALTH   = 800
    DEFAULT_SPEED    = 55        # px/s  — mucho más lento
    DEFAULT_SCALE    = 0.12      # más grande visualmente
    DEFAULT_STRENGTH = 20
    ASSET_PATH       = "assets/enemies/yellow.png"

    def __init__(
        self,
        position=(0, 0),
        rotation=0,
        health:   int   = DEFAULT_HEALTH,
        speed:    float = DEFAULT_SPEED,
        scale:    float = DEFAULT_SCALE,
        strength: int   = DEFAULT_STRENGTH,
        asset:    str   = ASSET_PATH,
    ):
        super().__init__(
            asset    = asset,
            position = position,
            rotation = rotation,
            scale    = scale,
            name     = "Tank",
            health   = health,
            strength = strength,
            speed    = speed,
        )
