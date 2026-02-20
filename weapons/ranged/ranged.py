import json

import pygame.draw

from core.monolite_behaviour import MonoliteBehaviour
from core.particles.particle_emitter import ParticleEmitter
from core.particles.particle import Particle
from weapons.weapon_module import Weapon, AMMO_TYPES


class Ranged(Weapon, MonoliteBehaviour):
    def __init__(self, asset, name, damage, max_range, ammo_type, clip_size,
                 fire_rate, reload_time, muzzle_speed=3000, muzzle_offset=(0,0), lock_time=0):
        super().__init__(asset, name, damage)
        MonoliteBehaviour.__init__(self)
        self.max_range = max_range      # Maximum effective range in meters before bullet despawns
        self.ammo_type = ammo_type      # Calliber used (shotgun, high, low, etc.)
        self.clip_size = clip_size      # Number of rounds per clip/magazine
        self.fire_rate = fire_rate      # Time between shots in seconds
        self.reload_time = reload_time  # Time to reload in seconds

        self.muzzle_speed = muzzle_speed  # Initial speed of the bullet in m/s
        self.muzzle_offset = muzzle_offset

        ## Consider adding damage dropoff

        # Lock time used only for delay before a shot after pressing LMB
        self.lock_time = lock_time

        self.current_clip = self.clip_size

        self.parent = None  # Will be set when equipped by a character

        self._last_shot_time = 0

        particle_asset = self._load_ammo_particle()
        particle_factory = lambda: Particle(particle_asset)
        self.emitter = ParticleEmitter(particle_factory, speed=muzzle_speed, lifespan=0.5)

    def _load_ammo_particle(self):
        # Return a particle configuration based on ammo type
        with open(AMMO_TYPES[self.ammo_type], 'r', encoding="utf-8") as f:
            ammo_data = json.load(f)

        asset = pygame.image.load(ammo_data["asset_particle_path"]).convert_alpha()
        return asset

    def update(self):
        if self.parent is not None:
            direction = pygame.Vector2(0, -1).rotate(-self.parent.rotation)
            self.emitter.set_position(self.parent.position + (direction * self.muzzle_offset[0] +
                                                              direction.rotate(90) * self.muzzle_offset[1]))
            self.emitter.set_rotation(self.parent.rotation)


    def shoot(self):
        if self.current_clip > 0:
            if self._last_shot_time + self.fire_rate * 1000 <= pygame.time.get_ticks():
                self._last_shot_time = pygame.time.get_ticks()
                self.current_clip -= 1

                # Implement shooting logic (raycasting, bullet instantiation, etc.)

                self.emitter.emit()
        else:
            # play dry fire
            print("Out of ammo! Reload needed.")


    def reload(self):
        if not self.parent: #or self.current_clip == self.clip_size:
            return
        print(self.parent.inventory.items)
        for item in self.parent.inventory.items:
            print(item)
        self.current_clip = self.clip_size


    def play_trail_effect(self, screen, start_pos, direction):
        # For testing, draw a simple line representing the bullet trail
        pygame.draw.line(screen, pygame.Color("red"), start_pos, start_pos + direction * self.max_range, 2)