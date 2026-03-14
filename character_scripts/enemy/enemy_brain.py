import pygame
from character_scripts.character_controller import CharacterController
from character_scripts.enemy.enemy_base import Enemy
from character_scripts.player.player import Player

class EnemyBrain:
    def __init__(self, enemy: Enemy, controller: CharacterController, player: Player):
        self.enemy      = enemy
        self.player     = player
        self.controller = controller

    def update(self, delta_time):
        if not self.enemy.is_alive():
            return
        self.decide_action(delta_time)

    def decide_action(self, delta_time): pass

    def distance_to_player(self): return self.enemy.position.distance_to(self.player.position)

    def direction_to_player(self):
        delta = self.player.position - self.enemy.position
        return delta.normalize() if delta.length() > 0 else pygame.Vector2(0, 0)

    def follow(self, delta_time):
        self.controller.speed = self.enemy.speed
        self.controller.move(self.direction_to_player(), delta_time)

    def face_player(self):
        d = self.direction_to_player()
        if d.length() > 0:
            self.enemy.rotation = d.angle_to(pygame.Vector2(0, -1))

    def try_attack(self, delta_time):
        if not self.enemy.is_alive():
            return
        if (self.distance_to_player() <= self.enemy.ATTACK_RANGE
                and self.enemy.can_attack(delta_time)):
            self.player.take_damage(self.enemy.strength)

class MeleeBrain(EnemyBrain):
    """Comportamiento base para enemigos cuerpo a cuerpo: seguir y atacar al llegar al rango."""
    def decide_action(self, delta_time):
        self.face_player()
        if self.distance_to_player() <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self.follow(delta_time)

class InfectedCommonBrain(MeleeBrain):  pass
class InfectedSoldierBrain(MeleeBrain): pass
class LabSubjectBrain(MeleeBrain):      pass
class TankBrain(MeleeBrain):            pass

class ToxicBrain(MeleeBrain):
    def decide_action(self, delta_time):
        # update() del ToxicEnemy gestiona la generación de charcos
        self.enemy.update(delta_time)
        super().decide_action(delta_time)

class ShooterBrain(EnemyBrain):
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()

        # Actualizar proyectiles en vuelo
        self.enemy.update_bullets(delta_time, self.player)

        if dist < self.enemy.FLEE_RANGE:
            # Huir en dirección contraria al jugador
            flee_dir = -self.direction_to_player()
            self.controller.speed = self.enemy.speed
            self.controller.move(flee_dir, delta_time)
        elif dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            if self.enemy.can_attack(delta_time):
                self.enemy.shoot(self.player)
        else:
            self.follow(delta_time)