"""
Level1WaveManager
-----------------
Sistema de oleadas para el Nivel 1.
Compatible con ui_manager.draw_overlay a través de get_hud_info().

Configuración
~~~~~~~~~~~~~
wave_config      : list[int]  — número de enemigos por oleada, ej. [20, 25, 30, 40, 50]
rest_time        : float      — segundos de descanso entre oleadas (por defecto 5 s)
spawn_duration   : float      — tiempo total en segundos para spawnear todos los
                                enemigos de una oleada de forma progresiva
enemy_speed      : float      — velocidad de movimiento de los enemigos (px/s)
"""
from __future__ import annotations

import random
import pygame

from character_scripts.enemy.enemy_base import Enemy
from character_scripts.character_controller import CharacterController

# ── Configuración por defecto ──────────────────────────────────────────────────
DEFAULT_WAVE_CONFIG    = [20, 25, 30, 40, 50]
DEFAULT_REST_TIME      = 5.0    # segundos de descanso entre oleadas
DEFAULT_SPAWN_DURATION = 8.0    # segundos para distribuir el spawn completo de una oleada


class Level1WaveManager:
    """
    Gestiona las oleadas de arena del Nivel 1.

    - Spawnea instancias de Enemy desde bordes aleatorios de la arena.
    - Spawn progresivo: distribuye los enemigos uniformemente a lo largo de
      `spawn_duration` segundos.
    - Período de descanso configurable entre oleadas.
    - Implementa get_hud_info() para compatibilidad con el HUD existente
      (mismo contrato que WaveManager.get_hud_info()).

    Parameters
    ----------
    arena_center   : (cx, cy) — centro de la arena en coordenadas de mundo
    arena_half     : semilado de la arena cuadrada (píxeles)
    wave_config    : lista de conteos de enemigos, un elemento por oleada
    rest_time      : segundos de descanso entre oleadas
    spawn_duration : segundos para distribuir el spawn de UNA oleada completa
    enemy_speed    : velocidad de los enemigos spawneados (px/s)
    """

    def __init__(
        self,
        arena_center: tuple[int, int],
        arena_half: int,
        wave_config: list[int] | None = None,
        rest_time: float = DEFAULT_REST_TIME,
        spawn_duration: float = DEFAULT_SPAWN_DURATION,
        enemy_speed: float = 110.0,
    ):
        self.arena_cx, self.arena_cy = arena_center
        self.arena_half    = arena_half
        self.wave_config   = wave_config or list(DEFAULT_WAVE_CONFIG)
        self.rest_time     = rest_time
        self.spawn_duration = spawn_duration
        self.enemy_speed   = enemy_speed

        self.total_waves   = len(self.wave_config)
        self.current_wave  = 0
        self.enemies: list = []

        # ── Estado interno ─────────────────────────────────────────────────────
        # "spawning"  → se están spawneando enemigos de forma progresiva
        # "fighting"  → todos spawneados, esperando que mueran
        # "resting"   → oleada limpiada, esperando el timer de descanso
        # "finished"  → todas las oleadas completadas
        self._state           = "idle"
        self._rest_timer      = 0.0

        self._spawn_remaining = 0     # enemigos pendientes de spawnear esta oleada
        self._spawn_timer     = 0.0   # acumulador hacia el siguiente spawn
        self._spawn_interval  = 0.0   # segundos entre spawns individuales

        self._on_complete = None      # callback() llamado al terminar todas las oleadas

        # Arrancar la primera oleada
        self._start_next_wave()

    # ── API pública ────────────────────────────────────────────────────────────

    def set_on_complete(self, callback):
        """Registra un callback sin argumentos que se llama cuando terminan todas las oleadas."""
        self._on_complete = callback

    def update(self, delta_time: float):
        """Debe llamarse una vez por frame desde la escena."""
        if self._state == "spawning":
            self._tick_spawn(delta_time)
            self._cleanup_dead()          # limpiar muertos también durante el spawn

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
        """
        Devuelve el mismo formato que WaveManager.get_hud_info() para que
        ui_manager.draw_overlay pueda mostrarlo sin modificaciones.
        """
        # Mostrar enemigos vivos + pendientes de spawnear
        enemies_displayed = len(self.enemies) + self._spawn_remaining
        # El HUD muestra "resting" solo cuando hay descanso activo
        hud_state = "resting" if self._state == "resting" else "fighting"
        return {
            "wave":         self.current_wave,
            "total_waves":  self.total_waves,
            "enemies_left": enemies_displayed,
            "state":        hud_state,
            "rest_timer":   max(0.0, self._rest_timer),
        }

    # ── Lógica interna ─────────────────────────────────────────────────────────

    def _start_next_wave(self):
        self.current_wave += 1
        count = self.wave_config[self.current_wave - 1]
        self._spawn_remaining = count
        self._spawn_timer     = 0.0
        # Intervalo entre spawns: distribuir 'count' enemigos en 'spawn_duration' segundos
        self._spawn_interval  = self.spawn_duration / count if count > 0 else 0.0
        self._state = "spawning"
        print(f"[LEVEL1] Oleada {self.current_wave}/{self.total_waves} — {count} enemigos")

    def _tick_spawn(self, delta_time: float):
        """Spawnea como máximo 1 enemigo por frame para evitar picos de CPU."""
        self._spawn_timer += delta_time
        if self._spawn_remaining > 0 and self._spawn_timer >= self._spawn_interval:
            self._spawn_timer -= self._spawn_interval
            self._spawn_remaining -= 1
            self._spawn_one()

        # Cuando se spawnearon todos, pasar a fase de combate
        if self._spawn_remaining == 0:
            self._state = "fighting"

    def _spawn_one(self):
        """Spawnea un Enemy en un punto aleatorio de un borde aleatorio de la arena."""
        margin = 60   # px dentro de la pared
        lo = -self.arena_half + margin
        hi =  self.arena_half - margin

        edge = random.randint(0, 3)
        if edge == 0:        # arriba
            ex = self.arena_cx + random.uniform(lo, hi)
            ey = self.arena_cy + lo
        elif edge == 1:      # abajo
            ex = self.arena_cx + random.uniform(lo, hi)
            ey = self.arena_cy + hi
        elif edge == 2:      # izquierda
            ex = self.arena_cx + lo
            ey = self.arena_cy + random.uniform(lo, hi)
        else:                # derecha
            ex = self.arena_cx + hi
            ey = self.arena_cy + random.uniform(lo, hi)

        enemy = Enemy("assets/icon.png", (ex, ey), 0, 0.05)
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
