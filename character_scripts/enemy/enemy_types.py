"""
character_scripts/enemy/enemy_types.py
---------------------------------------
Todos los tipos de enemigo del juego en un único módulo.

Melee (brain gestionado por WaveManager):
  InfectedCommon  — civil infectado, rápido y débil
  InfectedSoldier — soldado infectado, más duro y dañino
  LabSubject      — sujeto de laboratorio, lentísimo pero muy resistente

Arena / Nivel 1 (brain gestionado por WaveManager):
  TankEnemy       — tanque lento y muy resistente
  ToxicEnemy      — deja charcos de ácido al moverse
  ShooterEnemy    — dispara a distancia, huye si el jugador se acerca
  ToxicPuddle     — auxiliar de ToxicEnemy (no es Enemy)
"""

import pygame
from character_scripts.enemy.enemy_base import Enemy


# ══════════════════════════════════════════════════════════════════════════════
# MELEE — oleadas clásicas
# ══════════════════════════════════════════════════════════════════════════════

class InfectedCommon(Enemy):
    """Civil infectado. Bajo HP, bajo daño, velocidad media."""
    ATTACK_RANGE    = 32
    DETECTION_RANGE = 500
    ATTACK_COOLDOWN = 1.2

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/infected_common/infected_common.png",
            position=position,
            scale=0.20,
            name="Infectado",
            health=160,
            strength=12,
            speed=120,
        )
        self._attack_timer = 0.0

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False


class InfectedSoldier(Enemy):
    """Exsoldado infectado. HP medio-alto, daño alto, velocidad media-baja."""
    ATTACK_RANGE    = 38
    DETECTION_RANGE = 600
    ATTACK_COOLDOWN = 1.8

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/infected_soldier/infected_soldier.png",
            position=position,
            scale=0.22,
            name="Soldado Infectado",
            health=420,
            strength=28,
            speed=95,
        )
        self._attack_timer = 0.0

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False


class LabSubject(Enemy):
    """Sujeto de laboratorio. Muy alto HP, daño devastador, muy lento."""
    ATTACK_RANGE    = 42
    DETECTION_RANGE = 400
    ATTACK_COOLDOWN = 2.5

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/lab_subject/lab_subject.png",
            position=position,
            scale=0.28,
            name="Sujeto de Laboratorio",
            health=800,
            strength=55,
            speed=60,
        )
        self._attack_timer = 0.0

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# ARENA — Nivel 1
# ══════════════════════════════════════════════════════════════════════════════

class TankEnemy(Enemy):
    """Tanque: muy resistente, lento, empuja al contacto."""
    DEFAULT_SPEED   = 85
    ATTACK_RANGE    = 40
    DETECTION_RANGE = 800
    ATTACK_COOLDOWN = 2.0

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/red.png",
            position=position,
            scale=0.15,
            name="Tanque",
            health=600,
            strength=35,
            speed=TankEnemy.DEFAULT_SPEED,
        )
        self._attack_timer = 0.0

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False


class ToxicPuddle:
    """Charco ácido dejado por ToxicEnemy. No es un Enemy."""
    DAMAGE_INTERVAL = 0.5
    LIFETIME        = 8.0
    RADIUS          = 40
    DAMAGE          = 8

    def __init__(self, position):
        self.position   = pygame.Vector2(position)
        self._lifetime  = self.LIFETIME
        # FIX: start timer at full interval so the puddle doesn't deal
        # instant damage the very first frame it is created.
        self._dmg_timer = self.DAMAGE_INTERVAL
        self.is_alive   = True

    def update(self, delta_time, player):
        self._lifetime -= delta_time
        if self._lifetime <= 0:
            self.is_alive = False
            return
        if self.position.distance_to(player.position) <= self.RADIUS:
            self._dmg_timer -= delta_time
            if self._dmg_timer <= 0:
                self._dmg_timer = self.DAMAGE_INTERVAL
                player.take_damage(self.DAMAGE)
        else:
            # Reset timer when player steps out so there's no instant
            # damage the moment they walk back in.
            self._dmg_timer = self.DAMAGE_INTERVAL

    def draw(self, screen, camera):
        pos   = self.position - camera.position
        alpha = int(180 * (self._lifetime / self.LIFETIME))
        r     = self.RADIUS
        surf  = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (80, 200, 50, alpha), (r, r), r)
        screen.blit(surf, (pos.x - r, pos.y - r))


class ToxicEnemy(Enemy):
    """Tóxico: deja charcos de ácido periódicamente al moverse."""
    DEFAULT_SPEED   = 110
    ATTACK_RANGE    = 35
    DETECTION_RANGE = 600
    ATTACK_COOLDOWN = 1.5
    PUDDLE_INTERVAL = 2.5

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/green.png",
            position=position,
            scale=0.12,
            name="Tóxico",
            health=220,
            strength=15,
            speed=ToxicEnemy.DEFAULT_SPEED,
        )
        self._attack_timer = 0.0
        self._puddle_timer = 0.0
        self._puddle_list: list = []

    def register_puddle_list(self, puddle_list: list):
        """Recibe la lista compartida de charcos de la escena."""
        self._puddle_list = puddle_list

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False

    def update(self, delta_time):
        """Genera charcos periódicamente. Llamar desde el brain en cada frame."""
        if not self._puddle_list:
            return
        self._puddle_timer += delta_time
        if self._puddle_timer >= self.PUDDLE_INTERVAL:
            self._puddle_timer = 0.0
            self._puddle_list.append(ToxicPuddle(self.position))


class ShooterEnemy(Enemy):
    """Tirador a distancia. Huye si el jugador se acerca. Gestiona sus propias balas."""
    DEFAULT_SPEED   = 130
    ATTACK_RANGE    = 350
    FLEE_RANGE      = 180
    DETECTION_RANGE = 700
    ATTACK_COOLDOWN = 1.8
    BULLET_SPEED    = 420
    BULLET_DAMAGE   = 18

    zone_active = False
    is_shooting = False

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/yellow.png",
            position=position,
            scale=0.10,
            name="Tirador",
            health=180,
            strength=ShooterEnemy.BULLET_DAMAGE,
            speed=ShooterEnemy.DEFAULT_SPEED,
        )
        self._attack_timer = 0.0
        self._bullets: list = []

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False

    def shoot(self, player):
        """Dispara un proyectil hacia el jugador. Llamar desde ShooterBrain."""
        direction = player.position - self.position
        if direction.length() == 0:
            return
        self._bullets.append({
            "pos":    pygame.Vector2(self.position),
            "dir":    direction.normalize(),
            "damage": self.BULLET_DAMAGE,
        })
        self.is_shooting = True
        self.zone_active = True

    def update_bullets(self, delta_time, player):
        """Mueve proyectiles y comprueba impacto. Llamar desde ShooterBrain."""
        alive = []
        for b in self._bullets:
            b["pos"] += b["dir"] * self.BULLET_SPEED * delta_time
            dist_player = b["pos"].distance_to(player.position)
            dist_origin = b["pos"].distance_to(self.position)
            if dist_player < 24:
                player.take_damage(b["damage"])
            elif dist_origin < 1200:
                alive.append(b)
        self._bullets = alive
        self.is_shooting = False
        self.zone_active = False

    def draw_zone(self, screen, camera):
        pos  = self.position - camera.position
        r    = self.ATTACK_RANGE
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (220, 80, 0, 35), (r, r), r)
        screen.blit(surf, (pos.x - r, pos.y - r))

    def draw_bullets(self, screen, camera):
        for b in self._bullets:
            pos = b["pos"] - camera.position
            pygame.draw.circle(screen, (255, 200, 0), (int(pos.x), int(pos.y)), 5)