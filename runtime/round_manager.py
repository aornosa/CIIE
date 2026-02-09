from character_scripts.enemy.enemy_base import Enemy
from character_scripts.enemy.enemy_brain import EnemyBrain

def spawn_enemies(count):
    enemy_pool = []
    for i in range(count):
        enemy = Enemy("assets/icon.png", (i * 100, 100), 0, 0.05)
        enemy_pool.append(enemy)
    return enemy_pool