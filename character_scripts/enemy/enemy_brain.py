from character_scripts.character_controller import CharacterController
from character_scripts.enemy.enemy_base import Enemy
from character_scripts.player.player import Player


class EnemyBrain:
    def __init__(self, enemy: Enemy, controller: CharacterController, player: Player, delta_time):
        self.enemy = enemy
        self.player = player
        self.controller = controller
        self.delta_time = delta_time
        self.is_alive = True

    def update(self, delta_time):
        pass

    def decide_action(self):
        pass

    def follow(self):
        pass

    def stalk(self):
        pass

    def flee(self):
        pass
