"""
runtime/loot_table.py
----------------------
Tablas de loot y recompensas de puntuación por tipo de enemigo.

IDs válidos (item_data.json):
  ammo_clip_762 (cap 60), ammo_clip_12gauge (cap 16), ammo_clip_9mm (cap 30)
  health_injector, stim_patch, adrenaline_shot, rad_suppressor
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character_scripts.enemy.enemy_base import Enemy
    from character_scripts.player.player import Player


LOOT_TABLES = {
    "InfectedCommon": [
        ("ammo_clip_762", 0.20),
        ("stim_patch",    0.08),
    ],
    "InfectedSoldier": [
        ("ammo_clip_762",   0.25),
        ("stim_patch",      0.12),
        ("health_injector", 0.05),
    ],
    "LabSubject": [
        ("ammo_clip_762",   0.30),
        ("health_injector", 0.15),
        ("adrenaline_shot", 0.10),
        ("rad_suppressor",  0.07),
    ],
    "TankEnemy": [
        ("ammo_clip_762",    0.20),
        ("ammo_clip_12gauge",0.15),
        ("health_injector",  0.10),
        ("stim_patch",       0.08),
    ],
    "ToxicEnemy": [
        ("ammo_clip_762",  0.20),
        ("stim_patch",     0.10),
        ("rad_suppressor", 0.06),
    ],
    "ShooterEnemy": [
        ("ammo_clip_762",   0.25),
        ("ammo_clip_9mm",   0.15),
        ("stim_patch",      0.08),
        ("adrenaline_shot", 0.06),
    ],
}

SCORE_REWARDS = {
    "InfectedCommon":  500,
    "InfectedSoldier": 1250,
    "LabSubject":      2500,
    "TankEnemy":       1750,
    "ToxicEnemy":      1000,
    "ShooterEnemy":    1100,
}


def on_enemy_killed(enemy: "Enemy", player: "Player"):
    enemy_type = type(enemy).__name__

    points = SCORE_REWARDS.get(enemy_type, 500)
    player.add_score(points)
    print(f"[LOOT] +{points} pts ({enemy_type}). Total: {player.score}")

    table = LOOT_TABLES.get(enemy_type, [])
    _try_drop(table, enemy, player)


def _try_drop(table: list, enemy: "Enemy", player: "Player"):
    from item.item_loader import ItemRegistry
    from item.item_instance import ItemInstance

    for item_id, chance in table:
        if random.random() > chance:
            continue
        try:
            item_def = ItemRegistry.get(item_id)
            item     = ItemInstance(item_def)
            player.inventory.drop_manager.drop_item(item, enemy.position)
            print(f"[LOOT] Drop: {item_def.name}")
            return   # máximo 1 item por enemigo
        except Exception as e:
            print(f"[LOOT] Error al soltar {item_id}: {e}")