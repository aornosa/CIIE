from character_scripts.enemy.enemy_types import InfectedCommon, InfectedSoldier, LabSubject
from character_scripts.enemy.enemy_brain import InfectedCommonBrain, InfectedSoldierBrain, LabSubjectBrain
from character_scripts.character_controller import CharacterController


def spawn_enemies(player):
    definitions = [
        (InfectedCommon,  InfectedCommonBrain,  (1000, 800)),
        (InfectedSoldier, InfectedSoldierBrain, (2200, 800)),
        (LabSubject,      LabSubjectBrain,      (1600, 1400)),
    ]

    enemy_pool = []
    for EnemyClass, BrainClass, position in definitions:
        enemy = EnemyClass(position=position)
        controller = CharacterController(enemy.speed, enemy)
        enemy.brain = BrainClass(enemy, controller, player)
        enemy_pool.append(enemy)
    return enemy_pool

def cleanup_dead_enemies(enemy_pool):
    enemy_pool[:] = [e for e in enemy_pool if e.is_alive()]