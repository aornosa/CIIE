from __future__ import annotations
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from character_scripts.enemy.enemy_base import Enemy
    from character_scripts.player.player import Player

LOOT_TABLES: dict[str, list[tuple[str, float]]] = {
    "InfectedCommon": [
        ("stim_patch", 0.03),
    ],
    "InfectedSoldier": [
        ("stim_patch",      0.05),
        ("health_injector", 0.02),
    ],
    "LabSubject": [
        ("health_injector", 0.07),
        ("adrenaline_shot", 0.04),
        ("rad_suppressor",  0.03),
    ],
    "TankEnemy": [
        ("health_injector", 0.05),
        ("stim_patch",      0.04),
    ],
    "ToxicEnemy": [
        ("stim_patch",     0.04),
        ("rad_suppressor", 0.03),
    ],
    "ShooterEnemy": [
        ("stim_patch",      0.04),
        ("adrenaline_shot", 0.03),
    ],
}

SCORE_REWARDS: dict[str, int] = {
    "InfectedCommon":  1000,
    "InfectedSoldier": 3000,
    "LabSubject":      8000,
    "TankEnemy":       5000,
    "ToxicEnemy":      2500,
    "ShooterEnemy":    2500,
}


def on_enemy_killed(enemy: "Enemy", player: "Player"):
    enemy_type = type(enemy).__name__
    player.add_score(SCORE_REWARDS.get(enemy_type, 1000))
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
        except Exception:
            pass