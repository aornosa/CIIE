"""
character_scripts/enemy/enemy_brain.py
----------------------------------------
Sistema de IA de enemigos. Todos los tipos persiguen activamente al jugador.

Melee:
  InfectedCommonBrain  — persigue directo sin patrulla
  InfectedSoldierBrain — persigue sin fases de acecho
  LabSubjectBrain      — persigue sin condición de alerta

Arena (Nivel 1):
  TankBrain            — persigue directo, ataca al contacto
  ToxicBrain           — persigue y genera charcos; ataca al contacto
  ShooterBrain         — dispara a distancia, huye si el jugador se acerca
"""

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

    # ── Utilidades compartidas ─────────────────────────────────────────────

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


# ══════════════════════════════════════════════════════════════════════════════
# MELEE — todos persiguen sin fases de espera
# ══════════════════════════════════════════════════════════════════════════════

class InfectedCommonBrain(EnemyBrain):
    """Persigue directamente al jugador en todo momento."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self.follow(delta_time)


class InfectedSoldierBrain(EnemyBrain):
    """Persigue al jugador sin fases de acecho ni patrulla."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self.follow(delta_time)


class LabSubjectBrain(EnemyBrain):
    """Persigue sin condición de alerta — siempre va a por el jugador."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self.follow(delta_time)


# ══════════════════════════════════════════════════════════════════════════════
# ARENA — Nivel 1
# ══════════════════════════════════════════════════════════════════════════════

class TankBrain(EnemyBrain):
    """Persigue directo al jugador y golpea al contacto. Sin patrulla."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self.follow(delta_time)


class ToxicBrain(EnemyBrain):
    """Persigue al jugador generando charcos. Ataca al contacto."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()
        # Genera charcos mientras se mueve
        self.enemy.update(delta_time)
        if dist <= self.enemy.ATTACK_RANGE:
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            self.try_attack(delta_time)
        else:
            self.follow(delta_time)


class ShooterBrain(EnemyBrain):
    """Dispara a distancia. Huye si el jugador se acerca demasiado."""
    def decide_action(self, delta_time):
        self.face_player()
        dist = self.distance_to_player()

        # Actualiza balas en vuelo
        self.enemy.update_bullets(delta_time, self.player)

        if dist < self.enemy.FLEE_RANGE:
            # Huir: moverse en dirección contraria al jugador
            flee_dir = -self.direction_to_player()
            self.controller.speed = self.enemy.speed
            self.controller.move(flee_dir, delta_time)

        elif dist <= self.enemy.ATTACK_RANGE:
            # Posición de disparo: quieto y disparar
            self.controller.move(pygame.Vector2(0, 0), delta_time)
            if self.enemy.can_attack(delta_time):
                self.enemy.shoot(self.player)

        else:
            # Acercarse hasta rango de disparo
            self.follow(delta_time)