"""
ShooterEnemy
------------
Enemigo a distancia que ataca con un rayo telegráfico:

Flujo de comportamiento
~~~~~~~~~~~~~~~~~~~~~~~
1. CHASE    — se acerca al jugador mientras esté a más distancia de `attack_range`.
2. AIM      — se detiene, apunta al jugador y muestra la zona rectangular de peligro
               (se ilumina pulsando durante `telegraph_duration` segundos).
3. FIRE     — lanza un raycast. Si el jugador estaba dentro de la zona rectangular
               recibe `fire_damage` puntos de daño.
4. COOLDOWN — espera `fire_cooldown` segundos antes de volver al estado CHASE/AIM.

Todos los parámetros son configurables en el constructor o como constantes de clase.

Zona de peligro
~~~~~~~~~~~~~~~
La zona es un rectángulo orientado desde el origen del enemigo hasta
`attack_range` píxeles en la dirección al jugador, con `zone_width` px de ancho.
Se dibuja desde la escena llamando a `draw_zone(surface, camera)`.
"""
from __future__ import annotations

import math
import pygame

from character_scripts.enemy.enemy_base import Enemy
from core.collision.layers import LAYERS
from core.collision.raycast import raycast_segment


class ShooterEnemy(Enemy):
    # ── Parámetros por defecto ──────────────────────────────────────────────────
    DEFAULT_HEALTH       = 120
    DEFAULT_SPEED        = 90        # px/s cuando se acerca
    DEFAULT_SCALE        = 0.06
    DEFAULT_STRENGTH     = 5

    DEFAULT_ATTACK_RANGE   = 550.0   # px — distancia a la que para y apunta
    DEFAULT_FIRE_DAMAGE    = 30      # HP al impactar
    DEFAULT_TELEGRAPH_DUR  = 1.2     # segundos que muestra la zona antes de disparar
    DEFAULT_FIRE_COOLDOWN  = 2.5     # segundos entre disparos
    DEFAULT_ZONE_WIDTH     = 70      # px de ancho de la zona rectangular

    ASSET_PATH = "assets/enemies/red.png"

    # Colores de la zona telegráfica
    _ZONE_COLOR_DIM    = (255, 80, 30, 50)    # cuando no está a punto de disparar
    _ZONE_COLOR_BRIGHT = (255, 30, 30, 160)   # flash final antes de disparar
    _ZONE_EDGE_COLOR   = (255, 60, 0, 200)

    def __init__(
        self,
        position=(0, 0),
        rotation=0,
        health:         int   = DEFAULT_HEALTH,
        speed:          float = DEFAULT_SPEED,
        scale:          float = DEFAULT_SCALE,
        strength:       int   = DEFAULT_STRENGTH,
        asset:          str   = ASSET_PATH,
        attack_range:   float = DEFAULT_ATTACK_RANGE,
        fire_damage:    int   = DEFAULT_FIRE_DAMAGE,
        telegraph_dur:  float = DEFAULT_TELEGRAPH_DUR,
        fire_cooldown:  float = DEFAULT_FIRE_COOLDOWN,
        zone_width:     float = DEFAULT_ZONE_WIDTH,
    ):
        super().__init__(
            asset    = asset,
            position = position,
            rotation = rotation,
            scale    = scale,
            name     = "Shooter",
            health   = health,
            strength = strength,
            speed    = speed,
        )
        self.attack_range  = attack_range
        self.fire_damage   = fire_damage
        self.telegraph_dur = telegraph_dur
        self.fire_cooldown = fire_cooldown
        self.zone_width    = zone_width

        # ── Estado interno ──────────────────────────────────────────────────────
        # "chase"     → acercándose al jugador
        # "telegraph" → parado, mostrando zona; disparará cuando acabe el timer
        # "cooldown"  → esperando para volver a apuntar
        self._state          = "chase"
        self._state_timer    = 0.0

        # Dirección de ataque fijada al inicio del telegraph (Vector2, normalizado)
        self._aim_direction  = pygame.Vector2(0, -1)
        # Posición de origen del rayo fijada al inicio del telegraph
        self._aim_origin     = pygame.Vector2(position)

        # Indica si hay zona activa para dibujar
        self.zone_active     = False

    # ── API pública — llamar desde la escena cada frame ────────────────────────

    def update(self, delta_time: float, player) -> None:
        """
        Actualiza la IA del ShooterEnemy.
        `player` debe tener `.position` y `.take_damage(amount)`.
        """
        if not self.is_alive():
            self.zone_active = False
            return

        to_player = player.position - self.position
        dist      = to_player.length()

        if self._state == "chase":
            self._update_chase(dist, to_player, player, delta_time)

        elif self._state == "telegraph":
            self._update_telegraph(delta_time, player)

        elif self._state == "cooldown":
            self._state_timer -= delta_time
            self.zone_active = False
            if self._state_timer <= 0:
                self._state = "chase"

    def draw_zone(self, surface: pygame.Surface, camera) -> None:
        """
        Dibuja la zona rectangular de peligro.
        Llama esto desde render() de la escena (antes de dibujar los enemigos).
        """
        if not self.zone_active:
            return

        # Pulso: oscila entre tenue y brillante según el timer
        progress = max(0.0, 1.0 - self._state_timer / self.telegraph_dur)  # 0→1
        # Parpadea rápido en los últimos 0.4 s
        remaining = self._state_timer
        if remaining < 0.4:
            pulse = (math.sin(remaining * math.pi * 14) + 1) / 2
        else:
            pulse = progress

        # Color interpolado
        r = int(255)
        g = int(80 * (1 - pulse))
        b = int(30  * (1 - pulse))
        a = int(50 + 110 * pulse)
        fill_color = (r, g, b, a)

        # Construir los 4 vértices del rectángulo orientado
        forward  = self._aim_direction
        right    = pygame.Vector2(-forward.y, forward.x)  # perpendicular
        half_w   = self.zone_width / 2.0
        length   = self.attack_range

        origin_screen = self._aim_origin - camera.position

        p0 = origin_screen + right * half_w
        p1 = origin_screen - right * half_w
        p2 = origin_screen + forward * length - right * half_w
        p3 = origin_screen + forward * length + right * half_w
        pts = [(int(p.x), int(p.y)) for p in (p0, p1, p2, p3)]

        zone_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(zone_surf, fill_color, pts)
        pygame.draw.polygon(zone_surf, self._ZONE_EDGE_COLOR, pts, 2)
        surface.blit(zone_surf, (0, 0))

    # ── Internos ────────────────────────────────────────────────────────────────

    def _update_chase(self, dist, to_player, player, delta_time):
        """Perseguir al jugador. Cuando está en rango, pasar a telegraph."""
        if dist <= self.attack_range and dist > 0:
            # Fijar datos de ataque
            self._aim_direction = to_player.normalize()
            self._aim_origin    = pygame.Vector2(self.position)
            self._state_timer   = self.telegraph_dur
            self._state         = "telegraph"
            self.zone_active    = True
        # (el movimiento lo gestiona level1_scene como con los demás)

    def _update_telegraph(self, delta_time: float, player):
        """Cuenta regresiva; al llegar a 0 dispara."""
        self._state_timer -= delta_time
        if self._state_timer <= 0:
            self._fire(player)
            self.zone_active  = False
            self._state       = "cooldown"
            self._state_timer = self.fire_cooldown

    def _fire(self, player):
        """
        Lanza el raycast. Si toca al jugador (y no hay terreno antes), daña.
        También comprueba si el jugador está geométricamente dentro de la zona.
        """
        direction  = self._aim_direction
        start      = self._aim_origin
        end        = start + direction * self.attack_range

        # Comprobación geométrica: ¿está el jugador dentro del rectángulo?
        if self._player_in_zone(player.position):
            hit_col, hit_pt, _ = raycast_segment(
                start, end,
                layers=[LAYERS["player"], LAYERS["terrain"]],
            )
            # Si el primer impacto es el jugador (no un muro antes), daña
            if hit_col is not None:
                owner = getattr(hit_col, "owner", None)
                if owner is player or (owner is not None and hasattr(owner, "take_damage")
                                       and owner is not None
                                       and getattr(hit_col, "layer", -1) == LAYERS["player"]):
                    player.take_damage(self.fire_damage)
                elif getattr(hit_col, "layer", -1) == LAYERS["terrain"]:
                    pass  # muro bloquea — no daña

    def _player_in_zone(self, player_pos: pygame.Vector2) -> bool:
        """Comprueba si player_pos está dentro del rectángulo orientado."""
        to_p    = player_pos - self._aim_origin
        forward = self._aim_direction
        right   = pygame.Vector2(-forward.y, forward.x)

        along  = to_p.dot(forward)
        across = to_p.dot(right)

        return 0 <= along <= self.attack_range and abs(across) <= self.zone_width / 2.0

    # Override: en estado "telegraph" el enemigo no se mueve
    @property
    def is_shooting(self) -> bool:
        return self._state == "telegraph"
