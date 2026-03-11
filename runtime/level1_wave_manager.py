"""
Level1WaveManager
-----------------
Sistema de oleadas para el Nivel 1.
Compatible con ui_manager.draw_overlay a través de get_hud_info().

Configuración
~~~~~~~~~~~~~
wave_config      : list[int | dict]
                   Cada elemento puede ser:
                   - Un int  → N enemigos básicos (Enemy)
                   - Un dict → composición explícita, ej.:
                       {
                         "normal": 15,   # Enemy básico
                         "tank":   3,    # TankEnemy
                         "toxic":  5,    # ToxicEnemy
                       }

rest_time        : float — segundos de descanso entre oleadas
spawn_duration   : float — segundos para distribuir el spawn de una oleada
enemy_speed      : float — velocidad base para el Enemy básico
puddle_list      : list  — lista compartida donde ToxicEnemy añade charcos
"""
from __future__ import annotations

import random
import pygame

from character_scripts.enemy.enemy_base import Enemy
from character_scripts.enemy.tank_enemy import TankEnemy
from character_scripts.enemy.toxic_enemy import ToxicEnemy
from character_scripts.enemy.shooter_enemy import ShooterEnemy
from character_scripts.character_controller import CharacterController

# ── Configuración por defecto ──────────────────────────────────────────────────
DEFAULT_WAVE_CONFIG    = [20, 25, 30, 40, 50]
DEFAULT_REST_TIME      = 5.0
DEFAULT_SPAWN_DURATION = 8.0


class Level1WaveManager:
    """
    Gestiona las oleadas de arena del Nivel 1.

    Soporta tres tipos de enemigos: normal, tank, toxic.
    wave_config acepta enteros (oleada 100 % normal) o dicts con composición.
    """

    def __init__(
        self,
        arena_center: tuple[int, int],
        arena_half: int,
        wave_config: list | None = None,
        rest_time: float = DEFAULT_REST_TIME,
        spawn_duration: float = DEFAULT_SPAWN_DURATION,
        enemy_speed: float = 110.0,
        puddle_list: list | None = None,
    ):
        self.arena_cx, self.arena_cy = arena_center
        self.arena_half    = arena_half
        self.wave_config   = wave_config or list(DEFAULT_WAVE_CONFIG)
        self.rest_time     = rest_time
        self.spawn_duration = spawn_duration
        self.enemy_speed   = enemy_speed
        self.puddle_list   = puddle_list if puddle_list is not None else []

        self.total_waves   = len(self.wave_config)
        self.current_wave  = 0
        self.enemies: list = []

        # ── Estado interno ────────────────────────────────────────────────────
        self._state           = "idle"
        self._rest_timer      = 0.0

        # Cola de tipos a spawnear en la oleada actual: lista de strings
        # ("normal" | "tank" | "toxic")
        self._spawn_queue: list[str] = []
        self._spawn_timer     = 0.0
        self._spawn_interval  = 0.0

        self._on_complete = None

        self._start_next_wave()

    # ── API pública ─────────────────────────────────────────────────────────────

    def set_on_complete(self, callback):
        self._on_complete = callback

    def update(self, delta_time: float):
        if self._state == "spawning":
            self._tick_spawn(delta_time)
            self._cleanup_dead()

        elif self._state == "fighting":
            self._cleanup_dead()
            if len(self.enemies) == 0:
                self._on_wave_cleared()

        elif self._state == "resting":
            self._rest_timer -= delta_time
            if self._rest_timer <= 0:
                if self.current_wave >= self.total_waves:
                    self._finish()
                else:
                    self._start_next_wave()

    def get_hud_info(self) -> dict:
        enemies_displayed = len(self.enemies) + len(self._spawn_queue)
        hud_state = "resting" if self._state == "resting" else "fighting"
        return {
            "wave":         self.current_wave,
            "total_waves":  self.total_waves,
            "enemies_left": enemies_displayed,
            "state":        hud_state,
            "rest_timer":   max(0.0, self._rest_timer),
        }

    # ── Lógica interna ──────────────────────────────────────────────────────────

    def _build_spawn_queue(self, cfg) -> list[str]:
        """Convierte la entrada de wave_config en una lista mezclada de tipos."""
        if isinstance(cfg, int):
            queue = ["normal"] * cfg
        else:
            queue = []
            for kind, count in cfg.items():
                queue.extend([kind] * count)
        random.shuffle(queue)
        return queue

    def _start_next_wave(self):
        self.current_wave += 1
        cfg = self.wave_config[self.current_wave - 1]
        self._spawn_queue    = self._build_spawn_queue(cfg)
        self._spawn_timer    = 0.0
        total = len(self._spawn_queue)
        self._spawn_interval = self.spawn_duration / total if total > 0 else 0.0
        self._state = "spawning"
        print(f"[LEVEL1] Oleada {self.current_wave}/{self.total_waves} — {total} enemigos")

    def _tick_spawn(self, delta_time: float):
        self._spawn_timer += delta_time
        while self._spawn_queue and self._spawn_timer >= self._spawn_interval:
            self._spawn_timer -= self._spawn_interval
            kind = self._spawn_queue.pop(0)
            self._spawn_one(kind)

        if not self._spawn_queue:
            self._state = "fighting"

    def _spawn_one(self, kind: str = "normal"):
        """Spawnea un enemigo del tipo indicado en un borde aleatorio de la arena."""
        # Los enemigos grandes necesitan más margen para no quedar atrapados en muros
        margin = 120 if kind == "tank" else 60
        lo = -self.arena_half + margin
        hi =  self.arena_half - margin

        edge = random.randint(0, 3)
        if edge == 0:
            ex = self.arena_cx + random.uniform(lo, hi)
            ey = self.arena_cy + lo
        elif edge == 1:
            ex = self.arena_cx + random.uniform(lo, hi)
            ey = self.arena_cy + hi
        elif edge == 2:
            ex = self.arena_cx + lo
            ey = self.arena_cy + random.uniform(lo, hi)
        else:
            ex = self.arena_cx + hi
            ey = self.arena_cy + random.uniform(lo, hi)

        pos = (ex, ey)

        if kind == "tank":
            enemy = TankEnemy(position=pos)
            enemy._controller = CharacterController(TankEnemy.DEFAULT_SPEED, enemy)
        elif kind == "toxic":
            enemy = ToxicEnemy(position=pos)
            enemy._controller = CharacterController(ToxicEnemy.DEFAULT_SPEED, enemy)
            enemy.register_puddle_list(self.puddle_list)
        elif kind == "shooter":
            enemy = ShooterEnemy(position=pos)
            enemy._controller = CharacterController(ShooterEnemy.DEFAULT_SPEED, enemy)
        else:
            enemy = Enemy("assets/icon.png", pos, 0, 0.05)
            enemy._controller = CharacterController(self.enemy_speed, enemy)

        self.enemies.append(enemy)

    def _cleanup_dead(self):
        self.enemies[:] = [e for e in self.enemies if e.is_alive()]

    def _on_wave_cleared(self):
        print(f"[LEVEL1] Oleada {self.current_wave} completada.")
        if self.current_wave >= self.total_waves:
            self._finish()
        else:
            self._state      = "resting"
            self._rest_timer = self.rest_time

    def _finish(self):
        self._state = "finished"
        if self._on_complete:
            self._on_complete()
