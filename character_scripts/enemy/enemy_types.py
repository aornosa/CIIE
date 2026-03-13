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
  ShooterEnemy    — dispara proyectiles reales, huye si el jugador se acerca
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
    """Tanque: muy resistente, lento, golpea fuerte al contacto."""
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
        # Collider explícito: el asset es 1024x1024 pero el sprite se ve ~30px
        self.collider.rect.w = 25
        self.collider.rect.h = 25

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False


# ── ToxicPuddle ───────────────────────────────────────────────────────────────
# Versión completa con fade-out, burbujas decorativas y reset de timer al salir

class ToxicPuddle:
    """Charco tóxico dejado por ToxicEnemy."""
    DAMAGE_INTERVAL = 0.75
    LIFETIME        = 12.0
    RADIUS          = 30
    DAMAGE          = 5

    _COLOR_BASE   = (30,  180, 30,  80)
    _COLOR_RING   = (60,  220, 60, 160)
    _COLOR_BUBBLE = (80,  255, 80, 120)

    def __init__(self, position):
        self.position      = pygame.Vector2(position)
        self._lifetime     = self.LIFETIME
        self._age          = 0.0
        # FIX: arranca en DAMAGE_INTERVAL para no hacer daño instantáneo al spawnear
        self._dmg_timer    = self.DAMAGE_INTERVAL
        self._player_inside = False
        self.is_alive      = True

        # Superficie precalculada
        diam = self.RADIUS * 2 + 4
        self._surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
        self._bake_surface()

    def _bake_surface(self):
        import math
        cx = cy = self.RADIUS + 2
        pygame.draw.circle(self._surf, self._COLOR_BASE,   (cx, cy), self.RADIUS)
        pygame.draw.circle(self._surf, self._COLOR_RING,   (cx, cy), self.RADIUS, 3)
        for i in range(4):
            angle = i * (math.pi / 2)
            bx = int(cx + self.RADIUS * 0.5 * math.cos(angle))
            by = int(cy + self.RADIUS * 0.5 * math.sin(angle))
            pygame.draw.circle(self._surf, self._COLOR_BUBBLE,
                               (bx, by), max(2, self.RADIUS // 7))

    def update(self, delta_time, player):
        self._age      += delta_time
        self._lifetime -= delta_time
        if self._lifetime <= 0:
            self.is_alive = False
            return

        dist             = (player.position - self.position).length()
        currently_inside = dist <= self.RADIUS

        if currently_inside and not self._player_inside:
            # Daño instantáneo al entrar
            player.take_damage(self.DAMAGE)
            self._dmg_timer = 0.0
        elif currently_inside:
            self._dmg_timer += delta_time
            if self._dmg_timer >= self.DAMAGE_INTERVAL:
                self._dmg_timer -= self.DAMAGE_INTERVAL
                player.take_damage(self.DAMAGE)
        else:
            # Resetear timer al salir para evitar daño inmediato al volver a entrar
            self._dmg_timer = self.DAMAGE_INTERVAL

        self._player_inside = currently_inside

    def draw(self, screen, camera):
        if not self.is_alive:
            return
        screen_pos = self.position - camera.position
        rect = self._surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))

        # Fade-out en los últimos 2 segundos
        fade_start = max(0.0, self.LIFETIME - 2.0)
        if self._age >= fade_start:
            alpha = int(255 * (1.0 - (self._age - fade_start) / 2.0))
            tmp = self._surf.copy()
            tmp.set_alpha(max(0, alpha))
            screen.blit(tmp, rect)
        else:
            screen.blit(self._surf, rect)


class ToxicEnemy(Enemy):
    """Tóxico: deja charcos periódicamente al moverse. Ataca al contacto."""
    DEFAULT_SPEED   = 110
    ATTACK_RANGE    = 35
    DETECTION_RANGE = 600
    ATTACK_COOLDOWN = 1.5
    PUDDLE_INTERVAL = 0.6   # igual que rama compañero

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
        self._puddle_list  = None
        # Collider explícito: el asset es 1024x1024 pero el sprite se ve ~25px
        self.collider.rect.w = 20
        self.collider.rect.h = 20

    def register_puddle_list(self, puddle_list: list):
        """La escena/WaveManager debe llamar esto para conectar la lista compartida."""
        self._puddle_list = puddle_list

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False

    def update(self, delta_time):
        """Genera charcos periódicamente. Llamar desde ToxicBrain cada frame."""
        if self._puddle_list is None:
            return
        self._puddle_timer += delta_time
        if self._puddle_timer >= self.PUDDLE_INTERVAL:
            self._puddle_timer -= self.PUDDLE_INTERVAL
            self._puddle_list.append(ToxicPuddle(self.position))


class ShooterEnemy(Enemy):
    """
    Tirador a distancia con proyectiles físicos reales.
    Huye si el jugador se acerca demasiado (FLEE_RANGE).
    Gestiona sus propias balas internamente.
    """
    DEFAULT_SPEED   = 130
    ATTACK_RANGE    = 350
    FLEE_RANGE      = 180
    DETECTION_RANGE = 700
    ATTACK_COOLDOWN = 1.8
    BULLET_SPEED    = 420
    BULLET_DAMAGE   = 18

    # Compatibilidad con draw_zone de level1_scene (no dibuja zona telegráfica)
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
        self._attack_timer = ShooterEnemy.ATTACK_COOLDOWN * 0.5
        self._bullets: list = []
        # Collider explícito: el asset es 1024x1024 pero el sprite se ve ~20px
        self.collider.rect.w = 20
        self.collider.rect.h = 20

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False

    def shoot(self, player):
        """Dispara un proyectil hacia el jugador. Llamado desde ShooterBrain."""
        direction = player.position - self.position
        if direction.length() == 0:
            return
        self._bullets.append({
            "pos":    pygame.Vector2(self.position),
            "dir":    direction.normalize(),
            "damage": self.BULLET_DAMAGE,
        })

    def update_bullets(self, delta_time, player):
        """Mueve proyectiles y comprueba impacto. Llamado desde ShooterBrain."""
        alive = []
        for b in self._bullets:
            b["pos"] += b["dir"] * self.BULLET_SPEED * delta_time
            b["traveled"] = b.get("traveled", 0) + self.BULLET_SPEED * delta_time
            # Solo puede impactar si recorrió al menos 40 px (evita daño al spawnear)
            if b["traveled"] > 40 and b["pos"].distance_to(player.position) < 24:
                player.take_damage(b["damage"])
            elif b["pos"].distance_to(self.position) < 1200:
                alive.append(b)
        self._bullets = alive

    def draw_zone(self, screen, camera):
        """Dibuja un aura circular tenue alrededor del tirador (rango de disparo)."""
        pos  = self.position - camera.position
        r    = self.ATTACK_RANGE
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (220, 80, 0, 35), (r, r), r)
        screen.blit(surf, (int(pos.x) - r, int(pos.y) - r))

    def draw_bullets(self, screen, camera):
        """Dibuja los proyectiles en vuelo."""
        for b in self._bullets:
            pos = b["pos"] - camera.position
            pygame.draw.circle(screen, (255, 200, 0), (int(pos.x), int(pos.y)), 5)