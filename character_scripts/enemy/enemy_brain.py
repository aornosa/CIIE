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

class InfectedCommonBrain(EnemyBrain):
    def decide_action(self, delta_time):
        dist = self.distance_to_player()
        self.face_player()

        if dist <= self.enemy.DETECTION_RANGE:
            if dist <= self.enemy.ATTACK_RANGE:
                # En rango de ataque: parar y golpear
                self.controller.move(pygame.Vector2(0, 0), delta_time)
                self.try_attack(delta_time)
            else:
                # Detectado: perseguir
                self.follow(delta_time)
        # Si está fuera de rango: no hace nada (idle)

class InfectedSoldierBrain(EnemyBrain):
    CHASE_RANGE = 180   

    def __init__(self, enemy, controller, player):
        super().__init__(enemy, controller, player)
        self._stalk_speed = max(30, enemy.speed * 0.5)
        self._chase_speed = enemy.speed

    def decide_action(self, delta_time):
        dist = self.distance_to_player()
        self.face_player()

        if dist > self.enemy.DETECTION_RANGE:
            return  # Idle

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
        self._origin = pygame.Vector2(enemy.position)
        self._patrol_target = self._new_patrol_target()
        self._alerted = False   

    def _new_patrol_target(self):
        import random
        angle = random.uniform(0, 360)
        offset = pygame.Vector2(self.PATROL_RADIUS, 0).rotate(angle)
        return self._origin + offset

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
            self._patrol(delta_time)

    def _patrol(self, delta_time):
        dist_to_target = self.enemy.position.distance_to(self._patrol_target)
        if dist_to_target < 20:
            self._patrol_target = self._new_patrol_target()

        direction = self._patrol_target - self.enemy.position
        if direction.length() > 0:
            direction = direction.normalize()
        self.controller.speed = self.enemy.speed
        self.controller.move(direction, delta_time)