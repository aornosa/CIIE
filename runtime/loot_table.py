from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character_scripts.enemy.enemy_base import Enemy
    from character_scripts.player.player import Player


LOOT_TABLES = {
    "InfectedCommon": [
        ("ammo_clip_762",   0.35),
        ("health_injector", 0.10),
    ],
    "InfectedSoldier": [
        ("ammo_clip_762",   0.50),
        ("health_injector", 0.20),
        ("stim_patch",      0.10),
    ],
    "LabSubject": [
        ("ammo_clip_762",   0.60),
        ("health_injector", 0.40),
        ("adrenaline_shot", 0.20),
        ("rad_suppressor",  0.15),
    ],
}

SCORE_REWARDS = {
    "InfectedCommon":  100,
    "InfectedSoldier": 250,
    "LabSubject":      500,
}


def on_enemy_killed(enemy: "Enemy", player: "Player"):
    enemy_type = type(enemy).__name__

    # Puntos
    points = SCORE_REWARDS.get(enemy_type, 100)
    player.add_score(points)
    print(f"[LOOT] +{points} puntos ({enemy_type}). Total: {player.score}")

    # Loot drop
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

            if not player.inventory.check_full():
                # Inventario con espacio — pickup directo
                player.inventory.add_item(item)
                print(f"[LOOT] Recogido: {item_def.name}")
            else:
                # Inventario lleno — soltar al suelo usando el drop_manager del jugador
                player.inventory.drop_manager.drop_item(item, enemy.position)
                print(f"[LOOT] Soltado al suelo: {item_def.name}")
        except Exception as e:
            print(f"[LOOT] Error al soltar {item_id}: {e}")