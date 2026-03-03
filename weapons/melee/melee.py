import pygame
import math

from weapons.weapon_module import Weapon
from core.monolite_behaviour import MonoliteBehaviour
from core.collision.layers import LAYERS
from core.collision.raycast import raycast_segment
from core.audio.sound_cache import SOUNDS
from core.particles.particle_emitter import ParticleEmitter
from core.particles.particle import Particle

# Number of rays distributed across the attack cone
CONE_RAY_COUNT = 7


class Melee(Weapon, MonoliteBehaviour):
    def __init__(self, asset, name, damage, reach, attack_speed=1.0, reach_radius=40):
        super().__init__(asset, name, damage)
        MonoliteBehaviour.__init__(self)

        self.reach = reach                  # Maximum reach in pixels
        self.attack_speed = attack_speed    # Attacks per second
        self.attack_cooldown = 1.0 / attack_speed
        self.reach_radius = reach_radius    # Kept for API compatibility

        # Cone half-angle in degrees — derived from reach_radius and reach via
        # a simple arc approximation so narrower weapons feel tight and wide
        # ones feel broad.  Clamped to [15, 60] degrees.
        self.cone_half_angle = max(15.0, min(60.0, math.degrees(math.atan2(reach_radius, reach))))

        self._last_attack_time = 0
        self._is_attacking = False
        self._attack_duration = 0.3
        self._attack_start_time = 0

        self._hit_targets = set()

        self.particle_color = (255, 150, 50)

        impact_particle_asset = self._create_impact_particle()
        particle_factory = lambda: Particle(impact_particle_asset)
        self.impact_emitter = ParticleEmitter(particle_factory, speed=300, lifespan=0.6)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_impact_particle(self):
        surface = pygame.Surface((12, 12))
        surface.fill(self.particle_color)
        lighter_color = tuple(min(255, c + 100) for c in self.particle_color)
        pygame.draw.rect(surface, lighter_color, (0, 0, 12, 12), 1)
        return surface

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self):
        if self.parent is None:
            return

        self.impact_emitter.set_position(self.parent.position)

        if self._is_attacking:
            elapsed = pygame.time.get_ticks() - self._attack_start_time
            if elapsed > self._attack_duration * 1000:
                self._is_attacking = False
                self._hit_targets.clear()

    def can_attack(self) -> bool:
        current_time = pygame.time.get_ticks()
        return current_time - self._last_attack_time >= self.attack_cooldown * 1000

    def attack(self):
        if self.parent is None or not self.can_attack():
            return False

        self._last_attack_time = pygame.time.get_ticks()
        self._is_attacking = True
        self._attack_start_time = self._last_attack_time
        self._hit_targets.clear()

        forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        # Start the rays slightly in front of the character to avoid
        # self-collision with the player's own collider.
        ray_origin = self.parent.position + forward * 20

        self._check_cone_hits_raycast(ray_origin, forward)
        self._play_attack_sound()
        return True

    # ------------------------------------------------------------------
    # Raycast-based hurtbox  (replaces the old manual cone loop)
    # ------------------------------------------------------------------

    def _check_cone_hits_raycast(self, origin: pygame.Vector2, forward: pygame.Vector2):
        """
        Fire CONE_RAY_COUNT rays spread evenly across the attack cone.
        Each ray uses the same raycast_segment pipeline as Ranged weapons,
        filtering on LAYERS["enemy"] so terrain blocks the swing.
        """
        for i in range(CONE_RAY_COUNT):
            # Distribute rays symmetrically: -half_angle … 0 … +half_angle
            if CONE_RAY_COUNT == 1:
                t = 0.0
            else:
                t = i / (CONE_RAY_COUNT - 1)          # [0, 1]

            angle = (t * 2 - 1) * self.cone_half_angle  # [-half, +half] degrees
            ray_dir = forward.rotate(angle)
            ray_end = origin + ray_dir * self.reach

            hit_collider, hit_point, _ = raycast_segment(
                origin, ray_end,
                layers=[LAYERS["enemy"]],
                ignore=None,
            )

            if hit_collider is None:
                continue

            owner = getattr(hit_collider, "owner", None)
            if owner is None or owner in self._hit_targets:
                continue

            self._hit_targets.add(owner)
            self._apply_damage(owner, hit_point or ray_end)

    # ------------------------------------------------------------------

    def _apply_damage(self, target, hit_position: pygame.Vector2 = None):
        if hasattr(target, "take_damage"):
            target.take_damage(self.damage)

        pos = hit_position if hit_position is not None else (
            target.position if hasattr(target, "position") else self.parent.position
        )
        self.impact_emitter.set_position(pos)
        for _ in range(5):
            self.impact_emitter.emit()

    def _play_attack_sound(self):
        if self.audio_emitter and hasattr(self, "attack_sound_key"):
            try:
                self.audio_emitter.audio_clip = SOUNDS[self.attack_sound_key]
                self.audio_emitter.play()
            except (KeyError, AttributeError):
                pass

    def get_attack_progress(self) -> float:
        if not self._is_attacking:
            return 0.0
        elapsed = pygame.time.get_ticks() - self._attack_start_time
        return min(1.0, elapsed / (self._attack_duration * 1000))

    # ------------------------------------------------------------------
    # Visual cone  — uses SRCALPHA surface for proper transparency
    # ------------------------------------------------------------------

    def draw_attack_cone(self, screen, camera):
        """
        Draw the attack cone as a smooth arc with alpha fade.

        The cone consists of:
          • A filled polygon (arc segments + origin) fading as the attack ends.
          • Two edge lines showing the exact raycast boundaries.
          • Thin inner rays at each raycast angle for readability.
        """
        if self.parent is None or not self._is_attacking:
            return

        progress = self.get_attack_progress()          # 0 → 1 over attack duration
        # Fade out in the second half of the swing
        alpha = int(180 * max(0.0, 1.0 - progress * 1.5))
        if alpha <= 0:
            return

        base_color = self.particle_color
        forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        origin_screen = self.parent.position + forward * 20 - camera.position

        # ---- Build arc polygon points ----
        ARC_STEPS = 16
        arc_points_screen = []
        for i in range(ARC_STEPS + 1):
            t = i / ARC_STEPS
            angle = (t * 2 - 1) * self.cone_half_angle
            ray_dir = forward.rotate(angle)
            world_pt = self.parent.position + forward * 20 + ray_dir * self.reach
            arc_points_screen.append(world_pt - camera.position)

        # Full polygon: origin → arc → back to origin
        poly_points = [(int(origin_screen.x), int(origin_screen.y))]
        poly_points += [(int(p.x), int(p.y)) for p in arc_points_screen]

        # ---- Draw onto a temporary surface with alpha ----
        surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        fill_color  = (*base_color, alpha // 2)        # translucent fill
        edge_color  = (*base_color, alpha)             # solid edges
        ray_color   = (*base_color, alpha // 3)        # subtle inner rays

        # Filled arc
        if len(poly_points) >= 3:
            pygame.draw.polygon(surf, fill_color, poly_points)

        # Outer edge arc
        arc_screen_ints = [(int(p.x), int(p.y)) for p in arc_points_screen]
        if len(arc_screen_ints) >= 2:
            pygame.draw.lines(surf, edge_color, False, arc_screen_ints, 2)

        # Left / right boundary lines
        ox, oy = int(origin_screen.x), int(origin_screen.y)
        pygame.draw.line(surf, edge_color, (ox, oy), arc_screen_ints[0],  2)
        pygame.draw.line(surf, edge_color, (ox, oy), arc_screen_ints[-1], 2)

        # Individual ray lines (one per raycast)
        for i in range(CONE_RAY_COUNT):
            if CONE_RAY_COUNT == 1:
                t = 0.0
            else:
                t = i / (CONE_RAY_COUNT - 1)
            angle = (t * 2 - 1) * self.cone_half_angle
            ray_dir = forward.rotate(angle)
            ray_end_world = self.parent.position + forward * 20 + ray_dir * self.reach
            ray_end_screen = ray_end_world - camera.position
            pygame.draw.line(surf, ray_color,
                             (ox, oy),
                             (int(ray_end_screen.x), int(ray_end_screen.y)), 1)

        screen.blit(surf, (0, 0))