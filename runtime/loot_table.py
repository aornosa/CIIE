"""
runtime/loot_table.py
-----------------------
Tablas de loot y puntuación para todos los tipos de enemigo.
on_enemy_killed() es llamado automáticamente desde enemy_base.Enemy.die()
cuando enemy._player_ref está asignado (lo hace WaveManager al spawnear).
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character_scripts.enemy.enemy_base import Enemy
    from character_scripts.player.player import Player


# ── Loot (item_id, probabilidad de drop) ─────────────────────────────────────
LOOT_TABLES = {
    # Oleadas clásicas
    "InfectedCommon": [
        ("ammo_clip_762",   0.10),
        ("health_injector", 0.04),
    ],
    "InfectedSoldier": [
        ("ammo_clip_762",   0.18),
        ("health_injector", 0.07),
        ("stim_patch",      0.04),
    ],
    "LabSubject": [
        ("ammo_clip_762",   0.25),
        ("health_injector", 0.12),
        ("adrenaline_shot", 0.08),
        ("rad_suppressor",  0.06),
    ],

    # Arena — Nivel 1
    "TankEnemy": [
        ("health_injector", 0.20),
        ("ammo_clip_762",   0.15),
        ("stim_patch",      0.08),
    ],
    "ToxicEnemy": [
        ("ammo_clip_762",   0.12),
        ("rad_suppressor",  0.10),
        ("health_injector", 0.05),
    ],
    "ShooterEnemy": [
        ("ammo_clip_762",   0.20),
        ("health_injector", 0.06),
        ("stim_patch",      0.05),
    ],
}

# ── Puntuación por muerte ─────────────────────────────────────────────────────
SCORE_REWARDS = {
    "InfectedCommon":  100,
    "InfectedSoldier": 250,
    "LabSubject":      500,
    "TankEnemy":       350,
    "ToxicEnemy":      200,
    "ShooterEnemy":    220,
}


def on_enemy_killed(enemy: "Enemy", player: "Player"):
    """
    Llamado desde Enemy.die() cuando _player_ref está asignado.
    Otorga puntos y lanza la tirada de loot.
    """
    enemy_type = type(enemy).__name__

    points = SCORE_REWARDS.get(enemy_type, 100)
    player.add_score(points)
    print(f"[LOOT] +{points} pts ({enemy_type}). Total: {player.score}")

    _try_drop(LOOT_TABLES.get(enemy_type, []), enemy, player)


def _try_drop(table: list, enemy: "Enemy", player: "Player"):
    from item.item_loader import ItemRegistry
    from item.item_instance import ItemInstance

    for item_id, chance in table:
        if random.random() > chance:
            continue
        try:
            item = ItemInstance(ItemRegistry.get(item_id))
            player.inventory.drop_manager.drop_item(item, enemy.position)
            print(f"[LOOT] Drop al suelo: {item_id}")
        except Exception as e:
            print(f"[LOOT] Error al soltar {item_id}: {e}")