"""
runtime/round_manager.py
--------------------------
Sistema de oleadas unificado para todos los niveles.

WaveManager gestiona:
  - Spawn progresivo con cola temporizada (los enemigos van apareciendo
    repartidos durante la oleada, no todos a la vez)
  - Loot y puntuación a través de loot_table.on_enemy_killed (via enemy_base.die)
  - Brain system: cada enemigo tiene su propio cerebro de IA
  - API get_hud_info() compatible con ui_manager.draw_overlay

Uso básico:
    wm = WaveManager(player, arena_center=(cx, cy), arena_half=1000)
    wm.update(delta_time)
    enemies = wm.enemies          # lista activa para render / colisiones
    info    = wm.get_hud_info()   # dict para el HUD

Configuración avanzada (oleadas infinitas de arena):
    wm = WaveManager(
        player,
        arena_center=(cx, cy),
        arena_half=1000,
        total_waves=None,          # None = infinito
        rest_time=8.0,
        puddle_list=scene_puddles,
        start_wave=1,
        hp_scale_per_wave=0.05,
    )
    wm.set_on_complete(callback)   # llamado al acabar total_waves
"""

from __future__ import annotations

import random
import pygame

from character_scripts.character_controller import CharacterController
from character_scripts.enemy.enemy_types import (
    InfectedCommon, InfectedSoldier, LabSubject,
    TankEnemy, ToxicEnemy, ShooterEnemy,
)
from character_scripts.enemy.enemy_brain import (
    InfectedCommonBrain, InfectedSoldierBrain, LabSubjectBrain,
    TankBrain, ToxicBrain, ShooterBrain,
)

# ── Spawn points para oleadas clásicas ───────────────────────────────────────
SPAWN_POINTS = [
    (1000,  800), (2200,  800), (1600, 1400),
    ( 800,  600), (2400, 1200), (1200, 1600),
    (2000,  400), ( 600, 1400), (2600,  600),
    (1600,  200),
]
MIN_SPAWN_SEPARATION     = 150
MIN_SPAWN_DIST_TO_PLAYER = 400

# ── Composición de oleadas clásicas ──────────────────────────────────────────
WAVE_COMPOSITIONS = {
    1:  {"InfectedCommon": 3},
    2:  {"InfectedCommon": 5},
    3:  {"InfectedCommon": 5,  "InfectedSoldier": 1},
    4:  {"InfectedCommon": 6,  "InfectedSoldier": 2},
    5:  {"InfectedCommon": 4,  "InfectedSoldier": 3, "LabSubject": 1},
    6:  {"InfectedCommon": 6,  "InfectedSoldier": 3, "LabSubject": 1},
    7:  {"InfectedCommon": 5,  "InfectedSoldier": 4, "LabSubject": 2},
    8:  {"InfectedCommon": 6,  "InfectedSoldier": 5, "LabSubject": 2},
    9:  {"InfectedCommon": 4,  "InfectedSoldier": 6, "LabSubject": 3},
    10: {"InfectedCommon": 5,  "InfectedSoldier": 6, "LabSubject": 4},
}

# ── Proporciones de enemigos de arena (Nivel 1) ───────────────────────────────
ARENA_MIX = {
    "TankEnemy":    0.08,
    "ToxicEnemy":   0.15,
    "ShooterEnemy": 0.22,
    # el resto: InfectedCommon
}

# ── Brain y clase de cada tipo ────────────────────────────────────────────────
ENEMY_FACTORIES = {
    "InfectedCommon":  (InfectedCommon,  InfectedCommonBrain),
    "InfectedSoldier": (InfectedSoldier, InfectedSoldierBrain),
    "LabSubject":      (LabSubject,      LabSubjectBrain),
    "TankEnemy":       (TankEnemy,       TankBrain),
    "ToxicEnemy":      (ToxicEnemy,      ToxicBrain),
    "ShooterEnemy":    (ShooterEnemy,    ShooterBrain),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def cleanup_dead_enemies(enemy_pool: list):
    """Elimina enemigos muertos in-place. Util para escenas que gestionan su propia lista."""
    enemy_pool[:] = [e for e in enemy_pool if e.is_alive()]


def _stat_scale(wave: int) -> dict:
    scale = 1.0 + (wave - 1) * 0.05
    return {
        "health": scale,
        "damage": scale,
        "speed":  min(1.0 + (wave - 1) * 0.05, 1.5),
    }


def _pick_spawn_point(player, used: list) -> tuple:
    """Elige un punto de SPAWN_POINTS alejado del jugador y de otros spawns recientes."""
    player_pos = pygame.Vector2(player.position)
    candidates = list(SPAWN_POINTS)
    random.shuffle(candidates)

    for pos in candidates:
        v = pygame.Vector2(pos)
        if v.distance_to(player_pos) < MIN_SPAWN_DIST_TO_PLAYER:
            continue
        if not any(v.distance_to(pygame.Vector2(u)) < MIN_SPAWN_SEPARATION for u in used):
            return pos

    # Relajado: solo distancia al jugador
    for pos in candidates:
        if pygame.Vector2(pos).distance_to(player_pos) >= MIN_SPAWN_DIST_TO_PLAYER:
            return pos

    return max(candidates, key=lambda p: pygame.Vector2(p).distance_to(player_pos))


def _pick_arena_point(arena_cx: int, arena_cy: int, arena_half: int,
                      margin: int = 140) -> tuple:
    """Elige un punto en el borde de la arena (spawn de nivel 1)."""
    lo, hi = -arena_half + margin, arena_half - margin
    for _ in range(20):
        edge = random.randint(0, 3)
        if edge == 0:
            ex, ey = arena_cx + random.uniform(lo, hi), arena_cy + lo
        elif edge == 1:
            ex, ey = arena_cx + random.uniform(lo, hi), arena_cy + hi
        elif edge == 2:
            ex, ey = arena_cx + lo, arena_cy + random.uniform(lo, hi)
        else:
            ex, ey = arena_cx + hi, arena_cy + random.uniform(lo, hi)
        dx, dy = ex - arena_cx, ey - arena_cy
        if (dx * dx + dy * dy) >= margin * margin:
            return (ex, ey)
    return (arena_cx + hi, arena_cy)


# ══════════════════════════════════════════════════════════════════════════════
# WaveManager
# ══════════════════════════════════════════════════════════════════════════════

class WaveManager:
    """
    Gestor de oleadas universal.

    Parámetros clave:
      player         — referencia al jugador (para spawn, loot y brains)
      total_waves    — número de oleadas, o None para infinito
      arena_center   — (cx, cy) para modo arena; None usa SPAWN_POINTS clásicos
      arena_half     — radio de la arena (solo si arena_center no es None)
      arena_mix      — True usa proporciones ARENA_MIX; False usa WAVE_COMPOSITIONS
      rest_time      — segundos de descanso entre oleadas
      spawn_duration — segundos que tarda en aparecer la oleada completa
      puddle_list    — lista compartida de charcos (ToxicEnemy)
      start_wave     — primera oleada (para encadenar managers)
      hp_scale_per_wave — factor de HP adicional por oleada (0 = sin escala)
    """

    REST_TIME      = 8.0
    SPAWN_DURATION = 12.0

    def __init__(
        self,
        player,
        total_waves: int | None = 10,
        arena_center: tuple | None = None,
        arena_half: int = 1000,
        arena_mix: bool = False,
        rest_time: float = REST_TIME,
        spawn_duration: float = SPAWN_DURATION,
        puddle_list: list | None = None,
        start_wave: int = 1,
        hp_scale_per_wave: float = 0.0,
    ):
        self.player            = player
        self.total_waves       = total_waves        # None = infinito
        self.arena_center      = arena_center
        self.arena_half        = arena_half
        self.arena_mix         = arena_mix
        self.rest_time         = rest_time
        self.spawn_duration    = spawn_duration
        self.puddle_list       = puddle_list if puddle_list is not None else []
        self.hp_scale_per_wave = hp_scale_per_wave

        self.current_wave  = start_wave - 1
        self.enemies: list = []

        self._state          = "idle"
        self._rest_timer     = 0.0
        self._spawn_queue: list[str] = []
        self._spawn_timer    = 0.0
        self._spawn_interval = 0.0
        self._on_complete    = None

        # Para escenas legacy que usan set_director
        self._director = None

        self._start_next_wave()

    # ── API pública ──────────────────────────────────────────────────────────

    def set_on_complete(self, callback):
        """Callback sin argumentos llamado al terminar todas las oleadas."""
        self._on_complete = callback

    def set_director(self, director):
        """Compatibilidad con game_scene/game.py."""
        self._director = director

    def update(self, delta_time: float):
        # Actualizar brains de todos los enemigos vivos
        for enemy in self.enemies:
            if enemy.is_alive() and enemy.brain is not None:
                enemy.brain.update(delta_time)

        if self._state == "spawning":
            self._tick_spawn(delta_time)
            self._cleanup_dead()

        elif self._state == "fighting":
            self._cleanup_dead()
            if not self.enemies:
                self._on_wave_cleared()

        elif self._state == "resting":
            self._rest_timer -= delta_time
            if self._rest_timer <= 0:
                if self.total_waves is not None and self.current_wave >= self.total_waves:
                    self._finish()
                else:
                    self._start_next_wave()

    def get_hud_info(self) -> dict:
        pending = len(self.enemies) + len(self._spawn_queue)
        return {
            "wave":         self.current_wave,
            "total_waves":  self.total_waves if self.total_waves is not None else "∞",
            "enemies_left": pending,
            "state":        "resting" if self._state == "resting" else "fighting",
            "rest_timer":   max(0.0, self._rest_timer),
        }

    def notify_player_dead(self):
        """Llamar desde la escena cuando el jugador muere."""
        if self._state == "finished":
            return
        self._state = "finished"
        if self._director:
            from scenes.game_over_scene import GameOverScene
            self._director.replace(GameOverScene(stats={
                "score": self.player.score,
                "wave":  self.current_wave,
            }))

    # ── Oleadas ──────────────────────────────────────────────────────────────

    def _start_next_wave(self):
        self.current_wave += 1
        queue = self._build_queue()
        total = len(queue)
        duration = self.spawn_duration + 0.5 * self.current_wave
        self._spawn_queue    = queue
        self._spawn_timer    = 0.0
        self._spawn_interval = duration / total if total > 0 else 0.0
        self._state = "spawning"
        print(f"[WAVE] Oleada {self.current_wave}/{self.total_waves or '∞'} — {total} enemigos")

    def _build_queue(self) -> list[str]:
        """Construye la lista de tipos a spawnear para la oleada actual."""
        if self.arena_mix:
            # Modo arena: proporciones fijas escalando en cantidad
            total = 10 + 3 * self.current_wave
            n_tank    = max(0, int(total * ARENA_MIX["TankEnemy"]))
            n_toxic   = max(0, int(total * ARENA_MIX["ToxicEnemy"]))
            n_shooter = max(0, int(total * ARENA_MIX["ShooterEnemy"]))
            n_common  = total - n_tank - n_toxic - n_shooter
            queue = (["TankEnemy"]    * n_tank  +
                     ["ToxicEnemy"]   * n_toxic +
                     ["ShooterEnemy"] * n_shooter +
                     ["InfectedCommon"] * n_common)
        else:
            # Modo clásico: composición fija por oleada
            composition = WAVE_COMPOSITIONS.get(
                self.current_wave,
                {k: v + (self.current_wave - 10)
                 for k, v in WAVE_COMPOSITIONS[10].items()}
            )
            queue = [kind for kind, n in composition.items() for _ in range(n)]

        random.shuffle(queue)
        return queue

    def _tick_spawn(self, delta_time: float):
        self._spawn_timer += delta_time
        while self._spawn_queue and self._spawn_timer >= self._spawn_interval:
            self._spawn_timer -= self._spawn_interval
            self._spawn_one(self._spawn_queue.pop(0))
        if not self._spawn_queue:
            self._state = "fighting"

    def _spawn_one(self, kind: str):
        EnemyClass, BrainClass = ENEMY_FACTORIES[kind]

        # Posición de spawn
        margin = 200 if kind == "TankEnemy" else 140
        if self.arena_center is not None:
            pos = _pick_arena_point(*self.arena_center, self.arena_half, margin)
        else:
            pos = _pick_spawn_point(self.player, [e.position for e in self.enemies])

        enemy = EnemyClass(position=pos)

        # Escalar stats por oleada
        if self.hp_scale_per_wave > 0.0 and self.current_wave > 1:
            factor = 1.0 + self.hp_scale_per_wave * (self.current_wave - 1)
            enemy.health      = int(enemy.health * factor)
            enemy.base_health = enemy.health
        elif self.arena_center is None:
            # Escala clásica también afecta daño y velocidad
            scale = _stat_scale(self.current_wave)
            enemy.health      = int(enemy.health    * scale["health"])
            enemy.base_health = enemy.health
            enemy.strength    = int(enemy.strength  * scale["damage"])
            enemy.speed       = enemy.speed          * scale["speed"]

        # Loot: enlazar jugador para que die() pueda llamar on_enemy_killed
        enemy._player_ref = self.player

        # Charcos para ToxicEnemy
        if isinstance(enemy, ToxicEnemy) and self.puddle_list is not None:
            enemy.register_puddle_list(self.puddle_list)

        # Brain
        controller  = CharacterController(enemy.speed, enemy)
        enemy.brain = BrainClass(enemy, controller, self.player)

        self.enemies.append(enemy)

    # ── Estado ───────────────────────────────────────────────────────────────

    def _cleanup_dead(self):
        self.enemies[:] = [e for e in self.enemies if e.is_alive()]

    def _on_wave_cleared(self):
        print(f"[WAVE] Oleada {self.current_wave} completada.")
        if self.total_waves is not None and self.current_wave >= self.total_waves:
            self._finish()
        else:
            self._state      = "resting"
            self._rest_timer = self.rest_time

    def _finish(self):
        self._state = "finished"
        if self._on_complete:
            self._on_complete()
        elif self._director:
            from scenes.victory_scene import VictoryScene
            self._director.replace(VictoryScene(stats={
                "score": self.player.score,
                "wave":  self.current_wave,
            }))