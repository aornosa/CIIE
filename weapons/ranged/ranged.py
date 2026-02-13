import json

import pygame.draw

from core.particles.particle_emitter import ParticleEmitter
from core.particles.particle import Particle
from weapons.weapon_module import Weapon, AMMO_TYPES


class Ranged(Weapon):
    def __init__(self, asset, name, damage, max_range, ammo_type, clip_size, fire_rate, reload_time, lock_time=0):
        super().__init__(asset, name, damage)
        self.max_range = max_range      # Maximum effective range in meters before bullet despawns
        self.ammo_type = ammo_type      # Calliber used (shotgun, high, low, etc.)
        self.clip_size = clip_size      # Number of rounds per clip/magazine
        self.fire_rate = fire_rate      # Time between shots in seconds
        self.reload_time = reload_time  # Time to reload in seconds

        ## Consider adding damage dropoff

        # Lock time used only for delay before a shot after pressing LMB
        self.lock_time = lock_time

        self.current_clip = self.clip_size
        # self.emitter = ParticleEmitter((0,0), self._get_ammo_particle())

    def _get_ammo_particle(self):
        # Return a particle configuration based on ammo type
        ammo_data = json.loads(AMMO_TYPES[self.ammo_type])
        asset = pygame.image.load(ammo_data["asset_particle_path"]).convert_alpha()

        return Particle(asset, lifespan=self.max_range)


    def shoot(self):
        if self.current_clip > 0:
            self.current_clip -= 1
            # Implement shooting logic (raycasting, bullet instantiation, etc.)
        else:
            # play dry fire
            print("Out of ammo! Reload needed.")


    def reload(self):
        # find ammo in inventory and reload, for now just reset clip
        self.current_clip = self.clip_size


    def play_trail_effect(self, screen, start_pos, direction):
        # For testing, draw a simple line representing the bullet trail
        pygame.draw.line(screen, pygame.Color("red"), start_pos, start_pos + direction * self.max_range, 2)