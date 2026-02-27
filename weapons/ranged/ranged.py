import json

import pygame.draw

from core.audio.sound_cache import SOUNDS
from core.collision.layers import LAYERS
from core.collision.raycast import raycast_segment
from core.monolite_behaviour import MonoliteBehaviour
from core.particles.particle_emitter import ParticleEmitter
from core.particles.particle import Particle
from weapons.weapon_module import Weapon, AMMO_TYPES


class Ranged(Weapon, MonoliteBehaviour):
    def __init__(self, asset, name, damage, max_range, ammo_type, clip_size,
                 fire_rate, reload_time, muzzle_speed=3000, muzzle_offset=(0,0), lock_time=0):
        super().__init__(asset, name, damage)
        MonoliteBehaviour.__init__(self)
        
        self.max_range = max_range      # Maximum effective range in pixels before bullet despawns
        self.ammo_type = ammo_type      # Caliber used (9x19, 7.62, 12gauge, etc.)
        self.clip_size = clip_size      # Number of rounds per clip/magazine
        self.fire_rate = fire_rate      # Time between shots in seconds
        self.reload_time = reload_time  # Time to reload in seconds
        self.muzzle_speed = muzzle_speed  # Initial speed of the bullet in m/s
        self.muzzle_offset = muzzle_offset  # (forward_offset, side_offset)
        self.lock_time = lock_time      # Delay before shot after pressing trigger
        
        self.current_clip = self.clip_size
        self._last_shot_time = 0
        self._is_reloading = False
        self._reload_start_time = 0

        particle_asset = self._load_ammo_particle()
        particle_factory = lambda: Particle(particle_asset)
        self.emitter = ParticleEmitter(particle_factory, speed=muzzle_speed, lifespan=0.5)

    def _load_ammo_particle(self):
        try:
            with open(AMMO_TYPES[self.ammo_type], 'r', encoding="utf-8") as f:
                ammo_data = json.load(f)
            asset = pygame.image.load(ammo_data["asset_particle_path"]).convert_alpha()
            return asset
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load ammo particle for {self.ammo_type}: {e}")
            # Return a fallback simple pixel
            surface = pygame.Surface((2, 2))
            surface.fill((255, 255, 255))
            return surface

    def update(self):
        if self.parent is not None:
            direction = pygame.Vector2(0, -1).rotate(-self.parent.rotation)
            self.emitter.set_position(self.parent.position + (direction * self.muzzle_offset[0] +
                                                              direction.rotate(90) * self.muzzle_offset[1]))
            self.emitter.set_rotation(self.parent.rotation)
        
        # Update reload state
        if self._is_reloading:
            elapsed = (pygame.time.get_ticks() - self._reload_start_time) / 1000.0
            if elapsed >= self.reload_time:
                self._is_reloading = False

    def can_shoot(self) -> bool:
        return (self.current_clip > 0 and 
                not self._is_reloading and
                self._last_shot_time + self.fire_rate * 1000 <= pygame.time.get_ticks())

    def is_reloading(self) -> bool:
        return self._is_reloading

    def shoot(self):
        if not self.parent:
            return False
            
        if self.current_clip <= 0:
            print("Out of ammo! Reload needed.")
            return False
        
        if self._is_reloading:
            print("Still reloading...")
            return False
        
        if not self.can_shoot():
            return False

        self._last_shot_time = pygame.time.get_ticks()
        self.current_clip -= 1

        # Emit particle effect
        self.emitter.emit()

        # Calculate raycast from muzzle
        forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        end = self.parent.position + forward * self.max_range
        start = (self.parent.position + forward * self.muzzle_offset[0]
                 + forward.rotate(90) * self.muzzle_offset[1])

        # Check for hits
        hit = raycast_segment(start, end, layers=[LAYERS["enemy"], LAYERS["terrain"]])

        if hit and hit[0] is not None:
            self._handle_hit(hit[0], hit[1])

        # Play sound
        self._play_shoot_sound()
        
        return True

    def _handle_hit(self, hit_collider, hit_position):
        print(f"Hit {hit_collider} at {hit_position}")
        if hasattr(hit_collider, "owner") and hit_collider.owner:
            if hasattr(hit_collider.owner, "take_damage"):
                hit_collider.owner.take_damage(self.damage)

    def _play_shoot_sound(self):
        if self.audio_emitter:
            try:
                # Try to play ammo-specific sound
                sound_key = f"{self.ammo_type}_shoot"
                self.audio_emitter.audio_clip = SOUNDS[sound_key]
                self.audio_emitter.play()
            except (KeyError, AttributeError):
                # Fallback to generic shoot sound
                try:
                    self.audio_emitter.audio_clip = SOUNDS["generic_shoot"]
                    self.audio_emitter.play()
                except (KeyError, AttributeError):
                    pass

    def reload(self):
        if not self.parent:
            return False
        
        if self.current_clip == self.clip_size:
            print("Magazine already full!")
            return False
        
        if self._is_reloading:
            print("Already reloading...")
            return False

        # Find ammo in inventory
        ammo_found = False
        for item in self.parent.inventory.items:
            if item.ammo and item.ammo.ammo_type == self.ammo_type:
                ammo_found = True
                needed = self.clip_size - self.current_clip
                to_load = min(needed, item.ammo.capacity)
                
                # Start reload
                self._is_reloading = True
                self._reload_start_time = pygame.time.get_ticks()
                
                # Actually load ammo after reload time (could be done on start or end)
                self.current_clip += to_load
                item.ammo.capacity -= to_load
                
                if item.ammo.capacity <= 0:
                    self.parent.inventory.remove_item(item)
                
                print(f"Reloading [{to_load}] {self.ammo_type} rounds. Current clip: {self.current_clip}")
                self._play_reload_sound()
                break
        
        if not ammo_found:
            print(f"No {self.ammo_type} ammo available to reload!")
            return False
        
        return True

    def _play_reload_sound(self):
        if self.audio_emitter:
            try:
                sound_key = f"{self.ammo_type}_reload"
                self.audio_emitter.audio_clip = SOUNDS[sound_key]
                self.audio_emitter.play()
            except (KeyError, AttributeError):
                pass

    def get_ammo_count(self) -> tuple:
        reserve = 0
        if self.parent:
            for item in self.parent.inventory.items:
                if item.ammo and item.ammo.ammo_type == self.ammo_type:
                    reserve += item.ammo.capacity
        return (self.current_clip, reserve)

    def play_trail_effect(self, screen, start_pos, direction):
        pygame.draw.line(screen, pygame.Color("red"), start_pos, start_pos + direction * self.max_range, 2)