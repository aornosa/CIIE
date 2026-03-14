import pygame
import math
from weapons.weapon_module import Weapon
from core.monolite_behaviour import MonoliteBehaviour
from core.collision.layers import LAYERS
from core.collision.raycast import raycast_segment
from core.audio.sound_cache import SOUNDS
from core.particles.particle_emitter import ParticleEmitter
from core.particles.particle import Particle

CONE_RAY_COUNT = 7


def _ray_angles(half_angle: float) -> list[float]:
    """Devuelve los ángulos de los rayos del cono, de -half_angle a +half_angle."""
    if CONE_RAY_COUNT == 1:
        return [0.0]
    return [(i / (CONE_RAY_COUNT - 1) * 2 - 1) * half_angle for i in range(CONE_RAY_COUNT)]


class Melee(Weapon, MonoliteBehaviour):
    def __init__(self, asset, name, damage, reach, attack_speed=1.0, reach_radius=40):
        super().__init__(asset, name, damage)
        MonoliteBehaviour.__init__(self)

        self.reach           = reach
        self.attack_speed    = attack_speed
        self.attack_cooldown = 1.0 / attack_speed
        self.reach_radius    = reach_radius

        self.cone_half_angle = max(15.0, min(60.0, math.degrees(math.atan2(reach_radius, reach))))

        self._last_attack_time  = 0
        self._is_attacking      = False
        self._attack_duration   = 0.3
        self._attack_start_time = 0
        self._hit_targets       = set()

        self.particle_color = (255, 150, 50)
        impact_asset        = self._create_impact_particle()
        self.impact_emitter = ParticleEmitter(lambda: Particle(impact_asset), speed=300, lifespan=0.6)

    def _create_impact_particle(self):
        surface = pygame.Surface((12, 12))
        surface.fill(self.particle_color)
        lighter = tuple(min(255, c + 100) for c in self.particle_color)
        pygame.draw.rect(surface, lighter, (0, 0, 12, 12), 1)
        return surface

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
        return pygame.time.get_ticks() - self._last_attack_time >= self.attack_cooldown * 1000

    def attack(self):
        if self.parent is None or not self.can_attack():
            return False

        self._last_attack_time  = pygame.time.get_ticks()
        self._is_attacking      = True
        self._attack_start_time = self._last_attack_time
        self._hit_targets.clear()

        forward    = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        ray_origin = self.parent.position + forward * 20
        self._check_cone_hits_raycast(ray_origin, forward)
        self._play_attack_sound()
        return True

    def _check_cone_hits_raycast(self, origin: pygame.Vector2, forward: pygame.Vector2):
        for angle in _ray_angles(self.cone_half_angle):
            ray_end = origin + forward.rotate(angle) * self.reach
            hit_collider, hit_point, _ = raycast_segment(
                origin, ray_end, layers=[LAYERS["enemy"]])
            if hit_collider is None:
                continue
            owner = getattr(hit_collider, "owner", None)
            if owner is None or owner in self._hit_targets:
                continue
            self._hit_targets.add(owner)
            self._apply_damage(owner, hit_point or ray_end)

    def _apply_damage(self, target, hit_position: pygame.Vector2 = None):
        if hasattr(target, "take_damage"):
            target.take_damage(self.damage)
        pos = hit_position or (
            target.position if hasattr(target, "position") else self.parent.position)
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

    def draw_attack_cone(self, screen, camera):
        if self.parent is None or not self._is_attacking:
            return

        progress = self.get_attack_progress()
        alpha    = int(180 * max(0.0, 1.0 - progress * 1.5))
        if alpha <= 0:
            return

        forward       = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        muzzle_world  = self.parent.position + forward * 20
        origin_screen = muzzle_world - camera.position

        # Construye los puntos del arco en coordenadas de pantalla
        arc_screen = [
            (muzzle_world + forward.rotate((i / 16 * 2 - 1) * self.cone_half_angle) * self.reach) - camera.position
            for i in range(17)
        ]
        arc_ints = [(int(p.x), int(p.y)) for p in arc_screen]
        ox, oy   = int(origin_screen.x), int(origin_screen.y)
        poly     = [(ox, oy)] + arc_ints

        base         = self.particle_color
        fill_color   = (*base, alpha // 2)
        edge_color   = (*base, alpha)
        ray_color    = (*base, alpha // 3)

        surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        if len(poly) >= 3:
            pygame.draw.polygon(surf, fill_color, poly)
        if len(arc_ints) >= 2:
            pygame.draw.lines(surf, edge_color, False, arc_ints, 2)
        pygame.draw.line(surf, edge_color, (ox, oy), arc_ints[0],  2)
        pygame.draw.line(surf, edge_color, (ox, oy), arc_ints[-1], 2)

        for angle in _ray_angles(self.cone_half_angle):
            end = (muzzle_world + forward.rotate(angle) * self.reach) - camera.position
            pygame.draw.line(surf, ray_color, (ox, oy), (int(end.x), int(end.y)), 1)

        screen.blit(surf, (0, 0))