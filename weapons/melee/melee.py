import pygame
import math

from weapons.weapon_module import Weapon
from core.monolite_behaviour import MonoliteBehaviour
from core.collision.raycast import raycast_segment
from core.collision.layers import LAYERS
from core.audio.sound_cache import SOUNDS
from core.particles.particle_emitter import ParticleEmitter
from core.particles.particle import Particle


class Melee(Weapon, MonoliteBehaviour):
    def __init__(self, asset, name, damage, reach, attack_speed=1.0, reach_radius=40):
        super().__init__(asset, name, damage)
        MonoliteBehaviour.__init__(self)
        
        self.reach = reach                  # Maximum reach in pixels
        self.attack_speed = attack_speed    # Attacks per second
        self.attack_cooldown = 1.0 / attack_speed  # Time between attacks in seconds
        self.reach_radius = reach_radius    # Radius for arc-based attacks
        
        self._last_attack_time = 0
        self._is_attacking = False
        self._attack_duration = 0.3  # Duration of attack animation in seconds
        self._attack_start_time = 0
        
        self._hit_targets = set()
        
        # Impact particle system for melee hits
        impact_particle_asset = self._create_impact_particle()
        particle_factory = lambda: Particle(impact_particle_asset)
        self.impact_emitter = ParticleEmitter(particle_factory, speed=200, lifespan=0.3)

    def _create_impact_particle(self):
        """Create a simple placeholder particle for melee impacts."""
        surface = pygame.Surface((4, 4))
        surface.fill((200, 100, 50))  # Orange-brown for impact
        return surface

    def update(self):
        """Update attack state based on elapsed time."""
        if self.parent is None:
            return
        
        # Update impact emitter position
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
        if self.parent is None:
            return False
            
        if not self.can_attack():
            return False

        self._last_attack_time = pygame.time.get_ticks()
        self._is_attacking = True
        self._attack_start_time = self._last_attack_time
        self._hit_targets.clear()

        # Get direction from parent rotation
        forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        
        # Attack position ahead of parent
        attack_start = self.parent.position + forward * 20
        attack_end = attack_start + forward * self.reach
        
        # Perform raycast for primary hit
        hit = raycast_segment(attack_start, attack_end, layers=[LAYERS["enemy"], LAYERS["terrain"]])
        
        if hit and hit[0] is not None:
            target = hit[0]
            if target not in self._hit_targets:
                self._hit_targets.add(target)
                self._apply_damage(target)
                print(f"Melee hit {target} with {self.damage} damage")

        # Check for nearby targets in arc (within reach_radius)
        self._check_arc_hits(attack_start, forward)
        
        # Play attack sound
        self._play_attack_sound()
        
        return True

    def _check_arc_hits(self, attack_center: pygame.Vector2, forward: pygame.Vector2):
        from core.collision.collision_manager import CollisionManager
        
        # Create a small circle around attack point to catch nearby enemies
        # This is a simplified approach - could be expanded to proper arc detection
        nearby_distance = self.reach_radius
        
        # Get all colliders in range
        for collider in CollisionManager.active_colliders:
            if collider.layer not in [LAYERS["enemy"]]:
                continue
                
            if collider.owner in self._hit_targets:
                continue
                
            dist = attack_center.distance_to(collider.position)
            if dist < nearby_distance:
                self._hit_targets.add(collider.owner)
                self._apply_damage(collider.owner)
                print(f"Melee arc hit {collider.owner} with {self.damage} damage")

    def _apply_damage(self, target):
        """Apply damage to target and emit impact particles."""
        if hasattr(target, "take_damage"):
            target.take_damage(self.damage)
        
        # Emit impact particles at target position
        if hasattr(target, "position"):
            self.impact_emitter.set_position(target.position)
            self.impact_emitter.emit()

    def _play_attack_sound(self):
        if self.audio_emitter and hasattr(self, 'attack_sound_key'):
            try:
                self.audio_emitter.audio_clip = SOUNDS[self.attack_sound_key]
                self.audio_emitter.play()
            except (KeyError, AttributeError):
                pass  # Sound not configured or doesn't exist

    def get_attack_progress(self) -> float:
        if not self._is_attacking:
            return 0.0
        
        elapsed = pygame.time.get_ticks() - self._attack_start_time
        progress = min(1.0, elapsed / (self._attack_duration * 1000))
        return progress