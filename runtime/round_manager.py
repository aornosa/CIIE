from __future__ import annotations
import random
import pygame

from character_scripts.enemy.enemy_types import (
    InfectedCommon, InfectedSoldier, LabSubject,
    TankEnemy, ToxicEnemy, ShooterEnemy,
)
from character_scripts.enemy.enemy_brain import (
    InfectedCommonBrain, InfectedSoldierBrain, LabSubjectBrain,
    TankBrain, ToxicBrain, ShooterBrain,
)
from character_scripts.character_controller import CharacterController

_SPAWN_OFFSETS = [
    (-800, -600), ( 800, -600), (   0, -900),
    (-900,    0), ( 900,    0),
    (-800,  600), ( 800,  600), (   0,  900),
    (-600, -800), ( 600, -800), (-600,  800), ( 600,  800),
    (-700, -400), ( 700, -400), (-700,  400), ( 700,  400),
]

MIN_SPAWN_DIST_TO_PLAYER = 350
MIN_SPAWN_SEPARATION     = 120
HP_SCALE_PER_WAVE        = 0.08
MAX_ENEMIES_ON_SCREEN    = 35

_ENEMY_FACTORIES = {
    "InfectedCommon":  (InfectedCommon,  InfectedCommonBrain),
    "InfectedSoldier": (InfectedSoldier, InfectedSoldierBrain),
    "LabSubject":      (LabSubject,      LabSubjectBrain),
    "TankEnemy":       (TankEnemy,       TankBrain),
    "ToxicEnemy":      (ToxicEnemy,      ToxicBrain),
    "ShooterEnemy":    (ShooterEnemy,    ShooterBrain),
}


def _composition(wave: int) -> dict:
    """
    Composición temática por rangos de oleada.
    Cada rango tiene una identidad distinta; más allá de la 25 escala sin techo.
    """
    def rvar(n: int, spread: int = 2) -> int:
        return max(0, round(n * 1.5) + random.randint(-1, spread))

    if wave <= 3:
        return {
            "InfectedCommon":  rvar(6),
            "InfectedSoldier": rvar(1),
            "LabSubject":      0,
            "ToxicEnemy":      0,
            "ShooterEnemy":    0,
            "TankEnemy":       0,
        }
    elif wave <= 6:
        return {
            "InfectedCommon":  rvar(4),
            "InfectedSoldier": rvar(3),
            "LabSubject":      0,
            "ToxicEnemy":      rvar(2),
            "ShooterEnemy":    rvar(1),
            "TankEnemy":       0,
        }
    elif wave <= 9:
        return {
            "InfectedCommon":  rvar(2),
            "InfectedSoldier": rvar(3),
            "LabSubject":      rvar(1),
            "ToxicEnemy":      rvar(2),
            "ShooterEnemy":    rvar(3),
            "TankEnemy":       rvar(2),
        }
    elif wave == 10:
        return {
            "InfectedCommon":  rvar(8),
            "InfectedSoldier": rvar(5),
            "LabSubject":      rvar(2),
            "ToxicEnemy":      rvar(4),
            "ShooterEnemy":    rvar(4),
            "TankEnemy":       rvar(3),
        }
    elif wave <= 13:
        return {
            "InfectedCommon":  rvar(2),
            "InfectedSoldier": rvar(5),
            "LabSubject":      rvar(3),
            "ToxicEnemy":      rvar(2),
            "ShooterEnemy":    rvar(2),
            "TankEnemy":       rvar(2),
        }
    elif wave <= 18:
        return {
            "InfectedCommon":  rvar(1),
            "InfectedSoldier": rvar(3),
            "LabSubject":      rvar(4),
            "ToxicEnemy":      rvar(3),
            "ShooterEnemy":    rvar(4),
            "TankEnemy":       rvar(4),
        }
    elif wave <= 24:
        return {
            "InfectedCommon":  rvar(1),
            "InfectedSoldier": rvar(4),
            "LabSubject":      rvar(5),
            "ToxicEnemy":      rvar(3),
            "ShooterEnemy":    rvar(5),
            "TankEnemy":       rvar(5),
        }
    elif wave == 25:
        return {
            "InfectedCommon":  rvar(6),
            "InfectedSoldier": rvar(6),
            "LabSubject":      rvar(5),
            "ToxicEnemy":      rvar(5),
            "ShooterEnemy":    rvar(6),
            "TankEnemy":       rvar(5),
        }
    else:
        extra = wave - 25
        return {
            "InfectedCommon":  rvar(2 + extra // 5),
            "InfectedSoldier": rvar(5 + extra // 3),
            "LabSubject":      rvar(4 + extra // 3),
            "ToxicEnemy":      rvar(3 + extra // 4),
            "ShooterEnemy":    rvar(5 + extra // 3),
            "TankEnemy":       rvar(4 + extra // 3),
        }


def _pick_spawn(player, arena_center, arena_half, used: list) -> pygame.Vector2:
    player_pos = pygame.Vector2(player.position)
    cx, cy     = arena_center
    margin     = 120
    candidates = [
        pygame.Vector2(cx + ox, cy + oy)
        for ox, oy in _SPAWN_OFFSETS
        if abs(ox) < arena_half - margin and abs(oy) < arena_half - margin
    ]
    random.shuffle(candidates)
    for pos in candidates:
        if pos.distance_to(player_pos) < MIN_SPAWN_DIST_TO_PLAYER:
            continue
        if any(pos.distance_to(u) < MIN_SPAWN_SEPARATION for u in used):
            continue
        return pos
    # Sin candidato válido: usa el punto más lejano al jugador
    return max(candidates, key=lambda p: p.distance_to(player_pos))


def cleanup_dead_enemies(pool: list):
    pool[:] = [e for e in pool if e.is_alive()]


class WaveManager:
    def __init__(
        self,
        player,
        total_waves=None,
        arena_center=(960, 540),
        arena_half=1000,
        arena_mix=False,
        puddle_list=None,
        start_wave=1,
        hp_scale_per_wave=None,
    ):
        self.player       = player
        self.total_waves  = total_waves
        self.arena_center = arena_center
        self.arena_half   = arena_half
        self.arena_mix    = arena_mix
        self.puddle_list  = puddle_list if puddle_list is not None else []
        self.hp_scale     = hp_scale_per_wave if hp_scale_per_wave is not None else HP_SCALE_PER_WAVE

        self.current_wave  = start_wave - 1
        self.enemies: list = []
        self._state        = "resting"
        self._rest_timer   = 0.5
        self._on_complete  = None

        self._spawn_queue    = []
        self._spawn_interval = 0.5
        self._spawn_timer    = 0.0

    def set_on_complete(self, callback):
        self._on_complete = callback

    def update(self, delta_time: float):
        for e in self.enemies:
            if not e.is_alive():
                continue
            if e.brain is not None:
                e.brain.update(delta_time)
            if getattr(e, "_hit_flash_timer", 0) > 0:
                e._hit_flash_timer = max(0.0, e._hit_flash_timer - delta_time)

        for tp in list(self.puddle_list):
            tp.update(delta_time, self.player)
            if not tp.is_alive:
                self.puddle_list.remove(tp)

        cleanup_dead_enemies(self.enemies)

        if self._state == "fighting":
            if self._spawn_queue:
                self._spawn_timer -= delta_time
                if self._spawn_timer <= 0:
                    self._spawn_timer = self._spawn_interval
                    self._do_spawn_one(self._spawn_queue.pop(0))
            if not self.enemies and not self._spawn_queue:
                self._on_wave_cleared()

        elif self._state == "resting":
            self._rest_timer -= delta_time
            if self._rest_timer <= 0:
                self._start_next_wave()

    def _start_next_wave(self):
        self.current_wave += 1

        if self.total_waves is not None and self.current_wave > self.total_waves:
            self._state = "finished"
            if self._on_complete:
                self._on_complete()
            return

        comp  = _composition(self.current_wave) if self.arena_mix else \
                {"InfectedCommon": max(5, self.current_wave + 4)}
        scale    = 1.0 + (self.current_wave - 1) * self.hp_scale
        # Cap crece con la oleada a partir de la 25 para mantener el desafío
        cap      = MAX_ENEMIES_ON_SCREEN + max(0, (self.current_wave - 25) * 2)
        to_spawn = min(sum(comp.values()), cap - len(self.enemies))

        self._spawn_queue = self._build_spawn_list(comp, scale, to_spawn)
        self._spawn_timer = 0.0
        self._state       = "fighting"

    def _build_spawn_list(self, comp, scale, limit):
        entries = []
        for enemy_type, count in comp.items():
            if enemy_type not in _ENEMY_FACTORIES:
                continue
            EClass, BClass = _ENEMY_FACTORIES[enemy_type]
            for _ in range(count):
                entries.append((EClass, BClass, scale))
        random.shuffle(entries)
        return entries[:limit]

    def _do_spawn_one(self, entry):
        EClass, BClass, scale = entry
        used = [pygame.Vector2(e.position) for e in self.enemies]
        pos  = _pick_spawn(self.player, self.arena_center, self.arena_half, used)

        enemy             = EClass(position=(pos.x, pos.y))
        enemy.health      = int(enemy.health   * scale)
        enemy.base_health = enemy.health
        enemy.strength    = int(enemy.strength * scale)
        enemy._player_ref = self.player

        if hasattr(enemy, "register_puddle_list"):
            enemy.register_puddle_list(self.puddle_list)

        ctrl        = CharacterController(enemy.speed, enemy)
        enemy.brain = BClass(enemy, ctrl, self.player)

        # Adelanta medio cooldown para que no ataque nada más spawnear
        if hasattr(enemy, "_attack_timer"):
            enemy._attack_timer = getattr(enemy, "ATTACK_COOLDOWN", 0) * 0.5
        enemy._contact_cd = 1.0

        self.enemies.append(enemy)

    def _on_wave_cleared(self):
        if self.total_waves is not None and self.current_wave >= self.total_waves:
            self._state = "finished"
            if self._on_complete:
                self._on_complete()
        else:
            self._state      = "resting"
            self._rest_timer = 0.0

    def notify_player_dead(self):
        self._state = "finished"

    def get_hud_info(self) -> dict:
        return {
            "wave":         self.current_wave,
            "total_waves":  self.total_waves or "∞",
            "enemies_left": len(self.enemies) + len(self._spawn_queue),
            "state":        self._state,
            "rest_timer":   0.0,
        }