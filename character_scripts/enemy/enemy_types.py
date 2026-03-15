import math
import pygame
from character_scripts.enemy.enemy_base import Enemy

class InfectedCommon(Enemy):
    ATTACK_RANGE    = 32
    DETECTION_RANGE = 500
    ATTACK_COOLDOWN = 1.2

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/infected_common/infected_common.png",
            position=position, scale=0.07,
            name="Infectado", health=120, strength=12, speed=150,
        )

class InfectedSoldier(Enemy):
    ATTACK_RANGE    = 38
    DETECTION_RANGE = 600
    ATTACK_COOLDOWN = 1.8

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/infected_soldier/infected_soldier.png",
            position=position, scale=0.09,
            name="Soldado Infectado", health=260, strength=28, speed=165,
        )

class LabSubject(Enemy):
    ATTACK_RANGE    = 42
    DETECTION_RANGE = 400
    ATTACK_COOLDOWN = 2.5
    CHARGE_RANGE    = 400

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/lab_subject/lab_subject.png",
            position=position, scale=0.12,
            name="Sujeto de Laboratorio", health=500, strength=70, speed=70,
        )

class TankEnemy(Enemy):
    ATTACK_RANGE    = 40
    DETECTION_RANGE = 800
    ATTACK_COOLDOWN = 2.0
    CHARGE_RANGE    = 500

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/red.png",
            position=position, scale=0.2,
            name="Tanque", health=800, strength=35, speed=80,
        )

class ToxicPuddle:
    DAMAGE_INTERVAL = 0.75
    LIFETIME        = 12.0
    RADIUS          = 30
    DAMAGE          = 5

    _COLOR_BASE   = (30,  180, 30,  80)
    _COLOR_RING   = (60,  220, 60, 160)
    _COLOR_BUBBLE = (80,  255, 80, 120)

    def __init__(self, position):
        self.position       = pygame.Vector2(position)
        self._lifetime      = self.LIFETIME
        self._age           = 0.0
        # Empieza en DAMAGE_INTERVAL para evitar daño inmediato al spawnear
        self._dmg_timer     = self.DAMAGE_INTERVAL
        self._player_inside = False
        self.is_alive       = True

        diam       = self.RADIUS * 2 + 4
        self._surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
        self._bake_surface()

    def _bake_surface(self):
        cx = cy = self.RADIUS + 2
        pygame.draw.circle(self._surf, self._COLOR_BASE, (cx, cy), self.RADIUS)
        pygame.draw.circle(self._surf, self._COLOR_RING, (cx, cy), self.RADIUS, 3)
        # Cuatro burbujas decorativas en cruz
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
            # Daño instantáneo al entrar al charco
            player.take_damage(self.DAMAGE)
            self._dmg_timer = 0.0
        elif currently_inside:
            self._dmg_timer += delta_time
            if self._dmg_timer >= self.DAMAGE_INTERVAL:
                self._dmg_timer -= self.DAMAGE_INTERVAL
                player.take_damage(self.DAMAGE)
        else:
            self._dmg_timer = self.DAMAGE_INTERVAL

        self._player_inside = currently_inside

    def draw(self, screen, camera):
        if not self.is_alive:
            return
        screen_pos = self.position - camera.position
        rect       = self._surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))

        # Fade-out en los últimos 2 segundos de vida
        fade_start = max(0.0, self.LIFETIME - 2.0)
        if self._age >= fade_start:
            alpha = int(255 * (1.0 - (self._age - fade_start) / 2.0))
            tmp   = self._surf.copy()
            tmp.set_alpha(max(0, alpha))
            screen.blit(tmp, rect)
        else:
            screen.blit(self._surf, rect)

class ToxicEnemy(Enemy):
    ATTACK_RANGE    = 35
    DETECTION_RANGE = 600
    ATTACK_COOLDOWN = 1.5
    PUDDLE_INTERVAL = 0.6
    FLEE_RANGE      = 150

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/green.png",
            position=position, scale=0.08,
            name="Tóxico", health=170, strength=15, speed=140,
        )
        self._puddle_timer = 0.0
        self._puddle_list  = None

    def register_puddle_list(self, puddle_list: list):
        self._puddle_list = puddle_list

    def update(self, delta_time):
        if self._puddle_list is None:
            return
        self._puddle_timer += delta_time
        if self._puddle_timer >= self.PUDDLE_INTERVAL:
            self._puddle_timer -= self.PUDDLE_INTERVAL
            self._puddle_list.append(ToxicPuddle(self.position))

class ShooterEnemy(Enemy):
    ATTACK_RANGE    = 350
    FLEE_RANGE      = 220
    DETECTION_RANGE = 700
    ATTACK_COOLDOWN = 1.5
    BULLET_SPEED    = 420
    BULLET_DAMAGE   = 18

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/yellow.png",
            position=position, scale=0.06,
            name="Tirador", health=140, strength=self.BULLET_DAMAGE, speed=155,
        )
        self._attack_timer   = self.ATTACK_COOLDOWN * 0.5
        self._bullets: list  = []

    def shoot(self, player):
        direction = player.position - self.position
        if direction.length() == 0:
            return
        self._bullets.append({
            "pos":    pygame.Vector2(self.position),
            "dir":    direction.normalize(),
            "damage": self.BULLET_DAMAGE,
        })

    def update_bullets(self, delta_time, player):
        alive = []
        for b in self._bullets:
            b["pos"]      += b["dir"] * self.BULLET_SPEED * delta_time
            b["traveled"]  = b.get("traveled", 0) + self.BULLET_SPEED * delta_time
            # Ignora colisión en las primeras unidades para no dañar al spawnear
            if b["traveled"] > 40 and b["pos"].distance_to(player.position) < 24:
                player.take_damage(b["damage"])
            elif b["pos"].distance_to(self.position) < 1200:
                alive.append(b)
        self._bullets = alive

    def draw_zone(self, screen, camera):
        pos  = self.position - camera.position
        r    = self.ATTACK_RANGE
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (220, 80, 0, 35), (r, r), r)
        screen.blit(surf, (int(pos.x) - r, int(pos.y) - r))

    def draw_bullets(self, screen, camera):
        for b in self._bullets:
            pos = b["pos"] - camera.position
            pygame.draw.circle(screen, (255, 200, 0), (int(pos.x), int(pos.y)), 10)