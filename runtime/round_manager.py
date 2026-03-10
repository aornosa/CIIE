from __future__ import annotations
import random
import pygame
from character_scripts.enemy.enemy_types import InfectedCommon, InfectedSoldier, LabSubject
from character_scripts.enemy.enemy_brain import InfectedCommonBrain, InfectedSoldierBrain, LabSubjectBrain
from character_scripts.character_controller import CharacterController

SPAWN_POINTS = [
    (1000, 800),
    (2200, 800),
    (1600, 1400),
    (800,  600),
    (2400, 1200),
    (1200, 1600),
    (2000, 400),
]

WAVE_COMPOSITIONS = {
    1:  {"InfectedCommon": 3},
    2:  {"InfectedCommon": 5},
    3:  {"InfectedCommon": 5, "InfectedSoldier": 1},
    4:  {"InfectedCommon": 6, "InfectedSoldier": 2},
    5:  {"InfectedCommon": 4, "InfectedSoldier": 3, "LabSubject": 1},
    6:  {"InfectedCommon": 6, "InfectedSoldier": 3, "LabSubject": 1},
    7:  {"InfectedCommon": 5, "InfectedSoldier": 4, "LabSubject": 2},
    8:  {"InfectedCommon": 6, "InfectedSoldier": 5, "LabSubject": 2},
    9:  {"InfectedCommon": 4, "InfectedSoldier": 6, "LabSubject": 3},
    10: {"InfectedCommon": 5, "InfectedSoldier": 6, "LabSubject": 4},
}

def _stat_scale(wave: int) -> dict:
    scale = 1.0 + (wave - 1) * 0.05
    return {
        "health": scale,
        "damage": scale,
        "speed":  min(1.0 + (wave - 1) * 0.05, 1.5),
    }

ENEMY_FACTORIES = {
    "InfectedCommon":  (InfectedCommon,  InfectedCommonBrain),
    "InfectedSoldier": (InfectedSoldier, InfectedSoldierBrain),
    "LabSubject":      (LabSubject,      LabSubjectBrain),
}


def _spawn_wave(wave_number: int, player) -> list:
    composition = WAVE_COMPOSITIONS.get(
        wave_number,
        {k: v + (wave_number - 10) for k, v in WAVE_COMPOSITIONS[10].items()}
    )
    scale = _stat_scale(wave_number)
    spawn_positions = SPAWN_POINTS.copy()
    random.shuffle(spawn_positions)

    pool = []
    pos_index = 0
    for enemy_type, count in composition.items():
        EnemyClass, BrainClass = ENEMY_FACTORIES[enemy_type]
        for _ in range(count):
            pos = spawn_positions[pos_index % len(spawn_positions)]
            pos_index += 1

            enemy = EnemyClass(position=pos)
            enemy.health      = int(enemy.health   * scale["health"])
            enemy.base_health = enemy.health
            enemy.strength    = int(enemy.strength * scale["damage"])
            enemy.speed       = enemy.speed        * scale["speed"]
            enemy._player_ref = player  # necesario para loot al morir

            controller = CharacterController(enemy.speed, enemy)
            enemy.brain = BrainClass(enemy, controller, player)
            pool.append(enemy)

    return pool


def cleanup_dead_enemies(enemy_pool: list):
    enemy_pool[:] = [e for e in enemy_pool if e.is_alive()]


class WaveManager:
    REST_TIME = 5.0

    def __init__(self, player, total_waves: int = 10):
        self.player = player
        self.total_waves = total_waves
        self.current_wave = 0
        self.enemies: list = []
        self._state = "spawning"
        self._rest_timer = 0.0
        self._director = None

        self._start_next_wave()

    def set_director(self, director):
        self._director = director

    def update(self, delta_time: float, screen=None):
        # Actualizar brains de todos los enemigos vivos
        for enemy in self.enemies:
            if enemy.is_alive() and enemy.brain is not None:
                enemy.brain.update(delta_time)

        if self._state == "fighting":
            cleanup_dead_enemies(self.enemies)
            if len(self.enemies) == 0:
                self._on_wave_cleared()

        elif self._state == "resting":
            self._rest_timer -= delta_time
            if self._rest_timer <= 0:
                if self.current_wave >= self.total_waves:
                    self._on_victory()
                else:
                    self._start_next_wave()

    def _start_next_wave(self):
        self.current_wave += 1
        self.enemies = _spawn_wave(self.current_wave, self.player)
        self._state = "fighting"
        print(f"[WAVE] Oleada {self.current_wave}/{self.total_waves} — {len(self.enemies)} enemigos")

    def _on_wave_cleared(self):
        print(f"[WAVE] Oleada {self.current_wave} completada.")
        if self.current_wave >= self.total_waves:
            self._on_victory()
        else:
            self._state = "resting"
            self._rest_timer = self.REST_TIME

    def _on_victory(self):
        self._state = "finished"
        if self._director:
            from scenes.victory_scene import VictoryScene
            self._director.replace(VictoryScene(self.player.score))

    def notify_player_dead(self):
        if self._state == "finished":
            return
        self._state = "finished"
        if self._director:
            from scenes.game_over_scene import GameOverScene
            self._director.replace(GameOverScene(self.player.score, self.current_wave))

    def get_hud_info(self) -> dict:
        return {
            "wave":         self.current_wave,
            "total_waves":  self.total_waves,
            "enemies_left": len(self.enemies),
            "state":        self._state,
            "rest_timer":   max(0.0, self._rest_timer),
        }