import random
import pygame
from character_scripts.character_controller import CharacterController
from character_scripts.enemy.enemy_base import Enemy
from character_scripts.player.player import Player


class EnemyBrain:
    def __init__(self, enemy: Enemy, controller: CharacterController, player: Player):
        self.enemy = enemy
        self.player = player
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
        if delta.length() > 0:
            return delta.normalize()
        return pygame.Vector2(0, 0)

    def follow(self, delta_time):
        self.controller.speed = self.enemy.speed
        self.controller.move(self.direction_to_player(), delta_time)

    def face_player(self):
        direction = self.direction_to_player()
        if direction.length() > 0:
            self.enemy.rotation = direction.angle_to(pygame.Vector2(0, -1))

    def try_attack(self, delta_time):
        if not self.enemy.is_alive():
            return
        if self.distance_to_player() <= self.enemy.ATTACK_RANGE:
            if self.enemy.can_attack(delta_time):
                self.player.take_damage(self.enemy.strength)

    # --- Patrulla genérica reutilizable ---
    def _init_patrol(self, radius=150):
        self._patrol_origin = pygame.Vector2(self.enemy.position)
        self._patrol_target = self._new_patrol_target(radius)
        self._patrol_radius = radius
        self._patrol_wait   = 0.0  # segundos esperando en el target

    def _new_patrol_target(self, radius=None):
        r = radius or getattr(self, "_patrol_radius", 150)
        angle = random.uniform(0, 360)
        offset = pygame.Vector2(r, 0).rotate(angle)
        return self._patrol_origin + offset

    def _patrol(self, delta_time, speed_factor=0.4):
        # Espera breve al llegar al destino antes de elegir otro
        if self._patrol_wait > 0:
            self._patrol_wait -= delta_time
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            return

        dist_to_target = self.enemy.position.distance_to(self._patrol_target)
        if dist_to_target < 24:
            self._patrol_target = self._new_patrol_target()
            self._patrol_wait   = random.uniform(0.5, 1.5)
            return

        direction = self._patrol_target - self.enemy.position
        if direction.length() > 0:
            direction = direction.normalize()

        # Orientar al enemigo hacia donde va
        self.enemy.rotation = direction.angle_to(pygame.Vector2(0, -1))

        self.controller.speed = self.enemy.speed * speed_factor
        self.controller.move(direction, delta_time)


class InfectedCommonBrain(EnemyBrain):
    def __init__(self, enemy, controller, player):
        super().__init__(enemy, controller, player)
        self._init_patrol(radius=180)

    def decide_action(self, delta_time):
        dist = self.distance_to_player()
        self.face_player()

        if dist <= self.enemy.DETECTION_RANGE:
            if dist <= self.enemy.ATTACK_RANGE:
                self.controller.move(pygame.Vector2(0, 0), delta_time)
                self.try_attack(delta_time)
            else:
                self.follow(delta_time)
        else:
            self._patrol(delta_time, speed_factor=0.35)


class InfectedSoldierBrain(EnemyBrain):
    CHASE_RANGE = 180

    def __init__(self, enemy, controller, player):
        super().__init__(enemy, controller, player)
        self._stalk_speed = max(30, enemy.speed * 0.5)
        self._chase_speed = enemy.speed
        self._init_patrol(radius=250)

    def decide_action(self, delta_time):
        dist = self.distance_to_player()
        self.face_player()

        if dist > self.enemy.DETECTION_RANGE:
            self._patrol(delta_time, speed_factor=0.4)
            return

        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        elif dist <= self.CHASE_RANGE:
            self.controller.speed = self._chase_speed
            self.controller.move(self.direction_to_player(), delta_time)
        else:
            self.controller.speed = self._stalk_speed
            self.controller.move(self.direction_to_player(), delta_time)


class LabSubjectBrain(EnemyBrain):
    PATROL_RADIUS = 120

    def __init__(self, enemy, controller, player):
        super().__init__(enemy, controller, player)
        self._init_patrol(radius=self.PATROL_RADIUS)
        self._alerted = False

    def decide_action(self, delta_time):
        dist = self.distance_to_player()
        self.face_player()

        if dist <= self.enemy.DETECTION_RANGE:
            self._alerted = True

        if self._alerted:
            if dist <= self.enemy.ATTACK_RANGE:
                self.controller.move(pygame.Vector2(0, 0), delta_time)
                self.try_attack(delta_time)
            else:
                self.follow(delta_time)
        else:
            self._patrol(delta_time, speed_factor=0.45)