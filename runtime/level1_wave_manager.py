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
        rest_time: float = DEFAULT_REST_TIME,
        enemy_speed: float = 110.0,
        puddle_list: list | None = None,
        # ── Dificultad inicial: la primera oleada será start_wave ──────────────
        start_wave: int = 1,
        # ── Escalado de vida: +hp_scale_per_wave por oleada (0.0 = sin escalado)
        hp_scale_per_wave: float = 0.0,
    ):
        self.arena_cx, self.arena_cy = arena_center
        self.arena_half       = arena_half
        self.rest_time        = rest_time
        self.enemy_speed      = enemy_speed
        self.puddle_list      = puddle_list if puddle_list is not None else []
        self.hp_scale_per_wave = hp_scale_per_wave

        self.total_waves   = "∞"
        # current_wave empieza en start_wave-1; _start_next_wave() lo incrementa.
        self.current_wave  = start_wave - 1
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

    def _build_spawn_queue(self, total: int) -> list[str]:
        """Construye una cola de oleada basándose en probabilidades requeridas por ronda."""
        # 50% normal, 10% tank, 20% toxic, 30% shooter
        # Como suman 110, se usarán como proporciones sobre el total.
        num_tank    = max(0, int(total * (10 / 110)))
        num_toxic   = max(0, int(total * (20 / 110)))
        num_shooter = max(0, int(total * (30 / 110)))
        num_normal  = total - (num_tank + num_toxic + num_shooter)
        
        queue = (
            ["tank"] * num_tank +
            ["toxic"] * num_toxic +
            ["shooter"] * num_shooter +
            ["normal"] * num_normal
        )
        random.shuffle(queue)
        return queue

    def _start_next_wave(self):
        self.current_wave += 1

        total = 20 + 5 * self.current_wave
        spawn_duration = 8.0 + 0.5 * self.current_wave

        self._spawn_queue    = self._build_spawn_queue(total)
        self._spawn_timer    = 0.0
        self._spawn_interval = spawn_duration / total if total > 0 else 0.0
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
        """Spawnea un enemigo en un punto válido dentro de la arena (lejos de paredes)."""
        # margin_wall: separación mínima respecto a la pared visual.
        # margin_center: zona mínima desde el centro que se evita para no
        #   spawnear encima del jugador.
        margin_wall   = 200 if kind == "tank" else 140
        margin_center = 200   # radio de exclusión alrededor del centro

        lo = -self.arena_half + margin_wall
        hi =  self.arena_half - margin_wall

        for _ in range(20):   # máx intentos antes de aceptar la posición
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

            dx = ex - self.arena_cx
            dy = ey - self.arena_cy
            if (dx * dx + dy * dy) >= margin_center * margin_center:
                break   # posición válida encontrada

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

        # ── Escalado de vida por ronda ──────────────────────────────────────
        # Fórmula: HP_base × (1 + hp_scale_per_wave × (ronda_actual - 1))
        # Ejemplo con hp_scale_per_wave=0.10: ronda 7 → ×1.6, ronda 8 → ×1.7
        if self.hp_scale_per_wave > 0.0 and self.current_wave > 1:
            factor = 1.0 + self.hp_scale_per_wave * (self.current_wave - 1)
            enemy.health      = int(enemy.health      * factor)
            enemy.base_health = int(enemy.base_health * factor)

        self.enemies.append(enemy)

    def _cleanup_dead(self):
        self.enemies[:] = [e for e in self.enemies if e.is_alive()]

    def _on_wave_cleared(self):
        print(f"[LEVEL1] Oleada {self.current_wave} completada.")
        self._state      = "resting"
        self._rest_timer = self.rest_time

    def _finish(self):
        self._state = "finished"
        if self._on_complete:
            self._on_complete()
