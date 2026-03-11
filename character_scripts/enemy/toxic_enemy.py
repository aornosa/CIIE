"""
ToxicEnemy
----------
Enemigo de tamaño normal que va dejando charcos tóxicos (ToxicPuddle)
en el suelo mientras se mueve.

Parámetros configurables:
- puddle_interval   : segundos entre charcos
- puddle_radius     : radio del charco
- puddle_damage     : daño por tick
- puddle_damage_interval : segundos entre ticks del charco
- puddle_lifetime   : duración del charco
"""
from __future__ import annotations
from character_scripts.enemy.enemy_base import Enemy
from character_scripts.enemy.toxic_puddle import ToxicPuddle


class ToxicEnemy(Enemy):
    # ── Parámetros por defecto ──────────────────────────────────────────────────
    DEFAULT_HEALTH   = 100
    DEFAULT_SPEED    = 100
    DEFAULT_SCALE    = 0.05
    DEFAULT_STRENGTH = 10
    ASSET_PATH       = "assets/enemies/green.png"

    # Charcos
    DEFAULT_PUDDLE_INTERVAL        = 0.6   # cada cuántos segundos deja un charco
    DEFAULT_PUDDLE_RADIUS          = ToxicPuddle.DEFAULT_RADIUS
    DEFAULT_PUDDLE_DAMAGE          = ToxicPuddle.DEFAULT_DAMAGE
    DEFAULT_PUDDLE_DAMAGE_INTERVAL = ToxicPuddle.DEFAULT_DAMAGE_INTERVAL
    DEFAULT_PUDDLE_LIFETIME        = ToxicPuddle.DEFAULT_LIFETIME

    def __init__(
        self,
        position=(0, 0),
        rotation=0,
        health:                 int   = DEFAULT_HEALTH,
        speed:                  float = DEFAULT_SPEED,
        scale:                  float = DEFAULT_SCALE,
        strength:               int   = DEFAULT_STRENGTH,
        asset:                  str   = ASSET_PATH,
        puddle_interval:        float = DEFAULT_PUDDLE_INTERVAL,
        puddle_radius:          int   = DEFAULT_PUDDLE_RADIUS,
        puddle_damage:          int   = DEFAULT_PUDDLE_DAMAGE,
        puddle_damage_interval: float = DEFAULT_PUDDLE_DAMAGE_INTERVAL,
        puddle_lifetime:        float = DEFAULT_PUDDLE_LIFETIME,
    ):
        super().__init__(
            asset    = asset,
            position = position,
            rotation = rotation,
            scale    = scale,
            name     = "Toxic",
            health   = health,
            strength = strength,
            speed    = speed,
        )
        self._puddle_interval        = puddle_interval
        self._puddle_radius          = puddle_radius
        self._puddle_damage          = puddle_damage
        self._puddle_damage_interval = puddle_damage_interval
        self._puddle_lifetime        = puddle_lifetime

        self._puddle_timer  = 0.0        # acumulador
        self._puddle_list   = None       # referencia a la lista global de charcos

    def register_puddle_list(self, puddle_list: list) -> None:
        """La escena debe llamar esto para que el enemigo pueda añadir charcos."""
        self._puddle_list = puddle_list

    def update(self, delta_time: float) -> None:
        """Llama esto cada frame para gestionar la generación de charcos."""
        self._puddle_timer += delta_time
        if self._puddle_timer >= self._puddle_interval:
            self._puddle_timer -= self._puddle_interval
            self._drop_puddle()

    def _drop_puddle(self) -> None:
        if self._puddle_list is None:
            return
        puddle = ToxicPuddle(
            position         = (self.position.x, self.position.y),
            radius           = self._puddle_radius,
            damage           = self._puddle_damage,
            damage_interval  = self._puddle_damage_interval,
            lifetime         = self._puddle_lifetime,
        )
        self._puddle_list.append(puddle)
