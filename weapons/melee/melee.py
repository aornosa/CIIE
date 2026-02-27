import pygame
import math

from weapons.weapon_module import Weapon
from core.monolite_behaviour import MonoliteBehaviour
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
        
        # Color para partículas (puede ser overrideada por subclases)
        self.particle_color = (255, 150, 50)  # Orange by default
        
        # Impact particle system for melee hits
        impact_particle_asset = self._create_impact_particle()
        particle_factory = lambda: Particle(impact_particle_asset)
        self.impact_emitter = ParticleEmitter(particle_factory, speed=300, lifespan=0.6)

    def _create_impact_particle(self):
        """Create a simple placeholder particle for melee impacts."""
        surface = pygame.Surface((12, 12))
        surface.fill(self.particle_color)  # Use weapon-specific color
        # Add a border to make it more visible
        lighter_color = tuple(min(255, c + 100) for c in self.particle_color)
        pygame.draw.rect(surface, lighter_color, (0, 0, 12, 12), 1)
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

        # Get direction from parent rotation (where mouse is pointing)
        forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        
        # Attack position ahead of parent
        attack_start = self.parent.position + forward * 20
        
        # Check for targets in cone (45 degrees)
        self._check_cone_hits(attack_start, forward)
        
        # Play attack sound
        self._play_attack_sound()
        
        return True
    
    def _check_cone_hits(self, attack_start: pygame.Vector2, forward: pygame.Vector2):
        """Check for targets within a 45-degree cone in front of the attack."""
        from core.collision.collision_manager import CollisionManager
        import math
        
        cone_angle = 45  # 45 degrees total (22.5 on each side)
        half_angle = cone_angle / 2
        
        # Get all dynamic colliders in range (enemies are dynamic)
        for collider in CollisionManager.dynamic_colliders:
            if collider.layer not in [LAYERS["enemy"]]:
                continue
                
            if collider.owner in self._hit_targets:
                continue
            
            # Get position from collider's owner or rect center
            if hasattr(collider.owner, "position"):
                target_pos = pygame.Vector2(collider.owner.position)
            else:
                target_pos = pygame.Vector2(collider.rect.center)
            
            # Vector from attack start to target
            to_target = target_pos - attack_start
            
            # Check if target is within reach
            if to_target.length() > self.reach:
                continue
            
            # Check if target is within cone angle
            to_target_normalized = to_target.normalize()
            dot_product = forward.dot(to_target_normalized)
            
            # Calculate angle between forward and target direction
            angle_rad = math.acos(max(-1, min(1, dot_product)))  # Clamp to [-1, 1] for floating point errors
            angle_deg = math.degrees(angle_rad)
            
            if angle_deg <= half_angle:
                self._hit_targets.add(collider.owner)
                self._apply_damage(collider.owner)
                print(f"Melee cone hit {collider.owner} with {self.damage} damage at angle {angle_deg:.1f}°")

    def _apply_damage(self, target):
        """Apply damage to target and emit impact particles."""
        if hasattr(target, "take_damage"):
            target.take_damage(self.damage)
        
        # Emit impact particles at target position
        if hasattr(target, "position"):
            self.impact_emitter.set_position(target.position)
            # Emit multiple particles for more visible effect
            for _ in range(5):
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
    
    def draw_attack_cone(self, screen, camera):
        """Draw the attack cone as a semi-transparent visual effect."""
        if self.parent is None or not self._is_attacking:
            return
        # Get direction from parent rotation
        forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        # Attack position ahead of parent
        attack_start = self.parent.position + forward * 20
        # Convert to screen coordinates
        screen_pos = attack_start - camera.position
        # Cone parameters
        cone_angle = 45  # degrees total
        half_angle = cone_angle / 2
        # Calculate the two edges of the cone
        left_angle = -self.parent.rotation - half_angle
        right_angle = -self.parent.rotation + half_angle
        left_dir = pygame.math.Vector2(0, -1).rotate(left_angle)
        right_dir = pygame.math.Vector2(0, -1).rotate(right_angle)
        # Cone endpoints in world space
        left_end = attack_start + left_dir * self.reach
        right_end = attack_start + right_dir * self.reach
        # Convert all points to screen space
        left_screen = left_end - camera.position
        right_screen = right_end - camera.position
        # Draw filled cone (triangle) directly on screen
        points = [
            (int(screen_pos.x), int(screen_pos.y)),
            (int(left_screen.x), int(left_screen.y)),
            (int(right_screen.x), int(right_screen.y))
        ]
        # Draw semi-transparent cone based on weapon color
        if hasattr(self, 'particle_color'):
            color = (*self.particle_color, 80)  # Add alpha for transparency
        else:
            color = (255, 150, 50, 80)  # Default orange
        pygame.draw.polygon(screen, color, points)
        # Draw outline with bright color for visibility
        outline_color = (*self.particle_color, 255) if hasattr(self, 'particle_color') else (255, 150, 50, 255)
        pygame.draw.line(screen, outline_color, points[0], points[1], 3)
        pygame.draw.line(screen, outline_color, points[0], points[2], 3)
        pygame.draw.line(screen, outline_color, points[1], points[2], 3)