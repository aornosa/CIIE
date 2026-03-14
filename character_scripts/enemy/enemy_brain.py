import random
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

    def decide_action(self, delta_time):
        pass

    def distance_to_player(self):
        return self.enemy.position.distance_to(self.player.position)

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

class InfectedCommonBrain(MeleeBrain): pass

class InfectedSoldierBrain(EnemyBrain):
    """Corre en zigzag hacia el jugador"""
    _ZIG_INTERVAL = 0.6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._zig_timer = 0.0
        self._zig_angle = 0.0

    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self._zig_timer -= delta_time
            if self._zig_timer <= 0:
                self._zig_timer = self._ZIG_INTERVAL
                self._zig_angle = random.uniform(-35, 35)
            direction = self.direction_to_player().rotate(self._zig_angle)
            self.controller.speed = self.enemy.speed
            self.controller.move(direction, delta_time)

class LabSubjectBrain(EnemyBrain):
    """Lento a distancia, carga a máxima velocidad cuando está cerca."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        elif dist <= self.enemy.CHARGE_RANGE:
            # Carga rápida en línea recta al estar cerca
            self.controller.speed = self.enemy.speed * 2.5
            self.controller.move(self.direction_to_player(), delta_time)
        else:
            self.follow(delta_time)

class TankBrain(EnemyBrain):
    """Carga en línea recta cuando el jugador está lejos, lento al acercarse."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        elif dist >= self.enemy.CHARGE_RANGE:
            # Carga a alta velocidad desde lejos
            self.controller.speed = self.enemy.speed * 2.0
            self.controller.move(self.direction_to_player(), delta_time)
        else:
            self.follow(delta_time)

class ToxicBrain(EnemyBrain):
    """Huye si el jugador se acerca demasiado, genera charcos al moverse."""
    def decide_action(self, delta_time):
        # update() del ToxicEnemy gestiona la generación de charcos
        self.enemy.update(delta_time)
        self.face_player()
        dist = self.distance_to_player()
        if dist < self.enemy.FLEE_RANGE:
            # Huye en dirección contraria
            flee_dir = -self.direction_to_player()
            self.controller.speed = self.enemy.speed
            self.controller.move(flee_dir, delta_time)
        elif dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self.follow(delta_time)

class ShooterBrain(EnemyBrain):
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()

        # Actualizar proyectiles en vuelo
        self.enemy.update_bullets(delta_time, self.player)

        if dist < self.enemy.FLEE_RANGE:
            flee_dir = -self.direction_to_player()
            self.controller.speed = self.enemy.speed
            self.controller.move(flee_dir, delta_time)
        elif dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            if self.enemy.can_attack(delta_time):
                self.enemy.shoot(self.player)
        else:
            self.follow(delta_time)