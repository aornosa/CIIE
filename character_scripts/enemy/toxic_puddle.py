"""
ToxicPuddle
-----------
Charco tóxico que deja el ToxicEnemy en el suelo.
- Se dibuja como un círculo verde semitransparente.
- Daña al jugador cada `damage_interval` segundos mientras esté encima.
- Desaparece tras `lifetime` segundos.

Todos los parámetros son configurables al crearlo.
"""
from __future__ import annotations
import pygame


class ToxicPuddle:
    # ── Parámetros por defecto ──────────────────────────────────────────────────
    DEFAULT_RADIUS          = 30     # px
    DEFAULT_DAMAGE          = 5      # HP por tick
    DEFAULT_DAMAGE_INTERVAL = 0.75  # segundos entre ticks de daño
    DEFAULT_LIFETIME        = 12.0   # segundos hasta que desaparece

    # Colores
    _COLOR_BASE    = (30, 180, 30, 80)    # verde semitransparente (fondo)
    _COLOR_RING    = (60, 220, 60, 160)   # borde
    _COLOR_BUBBLE  = (80, 255, 80, 120)   # pequeñas "burbujas" decorativas

    def __init__(
        self,
        position: tuple[float, float],
        radius:          int   = DEFAULT_RADIUS,
        damage:          int   = DEFAULT_DAMAGE,
        damage_interval: float = DEFAULT_DAMAGE_INTERVAL,
        lifetime:        float = DEFAULT_LIFETIME,
    ):
        self.position         = pygame.Vector2(position)
        self.radius           = radius
        self.damage           = damage
        self.damage_interval  = damage_interval
        self.lifetime         = lifetime

        self._age             = 0.0   # segundos de vida transcurridos
        self._damage_timer    = 0.0   # acumulador hacia el próximo tick de daño
        self._player_inside   = False  # ¿estaba el jugador dentro el frame anterior?

        # Superficie precalculada para el charco (SRCALPHA)
        diam = radius * 2 + 4
        self._surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
        self._bake_surface()

    def _bake_surface(self):
        """Dibuja el charco una sola vez en la superficie interna."""
        cx = cy = self.radius + 2
        # Fondo
        pygame.draw.circle(self._surf, self._COLOR_BASE, (cx, cy), self.radius)
        # Anillo exterior
        pygame.draw.circle(self._surf, self._COLOR_RING, (cx, cy), self.radius, 3)
        # Burbujas decorativas
        import math
        for i in range(4):
            angle = i * (math.pi / 2)
            bx = int(cx + self.radius * 0.5 * math.cos(angle))
            by = int(cy + self.radius * 0.5 * math.sin(angle))
            pygame.draw.circle(self._surf, self._COLOR_BUBBLE, (bx, by), max(2, self.radius // 7))

    # ── API pública ─────────────────────────────────────────────────────────────

    @property
    def is_alive(self) -> bool:
        return self._age < self.lifetime

    def update(self, delta_time: float, player) -> None:
        """
        Llama esto cada frame.
        `player` debe tener `.position` y `.take_damage(amount)`.
        """
        self._age          += delta_time
        self._damage_timer += delta_time

        dist = (player.position - self.position).length()
        currently_inside = dist <= self.radius

        # Daño instantáneo al entrar por primera vez
        if currently_inside and not self._player_inside:
            player.take_damage(self.damage)
            self._damage_timer = 0.0  # resetear tick para no doblar daño

        # Daño periódico mientras permanece dentro
        elif currently_inside and self._damage_timer >= self.damage_interval:
            self._damage_timer -= self.damage_interval
            player.take_damage(self.damage)

        self._player_inside = currently_inside

    def draw(self, surface: pygame.Surface, camera) -> None:
        """Dibuja el charco en el screen."""
        if not self.is_alive:
            return

        screen_pos = self.position - camera.position
        rect = self._surf.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))

        # Atenuar según vida restante (fade-out en los últimos 2 s)
        fade_start = max(0.0, self.lifetime - 2.0)
        if self._age >= fade_start and self.lifetime > fade_start:
            alpha = int(255 * (1.0 - (self._age - fade_start) / (self.lifetime - fade_start)))
            tmp = self._surf.copy()
            tmp.set_alpha(alpha)
            surface.blit(tmp, rect)
        else:
            surface.blit(self._surf, rect)

    # ── Interno ─────────────────────────────────────────────────────────────────

    def _try_damage(self, player) -> None:
        """Inflige daño si el jugador está dentro del radio."""
        dist = (player.position - self.position).length()
        if dist <= self.radius:
            player.take_damage(self.damage)
