from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character_scripts.enemy.enemy_base import Enemy
    from character_scripts.player.player import Player


LOOT_TABLES = {
    "InfectedCommon": [
        ("ammo_clip_762",   0.10),   # era 0.20
        ("health_injector", 0.04),   # era 0.05
    ],
    "InfectedSoldier": [
        ("ammo_clip_762",   0.18),   # era 0.30
        ("health_injector", 0.07),   # era 0.10
        ("stim_patch",      0.04),   # era 0.05
    ],
    "LabSubject": [
        ("ammo_clip_762",   0.25),   # era 0.40
        ("health_injector", 0.12),   # era 0.20
        ("adrenaline_shot", 0.08),   # era 0.10
        ("rad_suppressor",  0.06),   # era 0.08
    ],
}

SCORE_REWARDS = {
    "InfectedCommon":  100,
    "InfectedSoldier": 250,
    "LabSubject":      500,
}


def on_enemy_killed(enemy: "Enemy", player: "Player"):
    enemy_type = type(enemy).__name__

    points = SCORE_REWARDS.get(enemy_type, 100)
    player.add_score(points)
    print(f"[LOOT] +{points} puntos ({enemy_type}). Total: {player.score}")

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
            item = ItemInstance(item_def)
            player.inventory.drop_manager.drop_item(item, enemy.position)
            print(f"[LOOT] Soltado al suelo: {item_def.name}")
        except Exception as e:
            print(f"[LOOT] Error al soltar {item_id}: {e}")