from character_scripts.enemy.enemy_base import Enemy

def spawn_enemies(count):
    enemies = []
    for i in range(count):
        enemy = Enemy("assets/icon.png", (i * 100, 100), 0, 0.05)
        enemies.append(enemy)
    return enemies