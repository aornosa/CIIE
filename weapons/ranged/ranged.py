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

                self.emitter.emit()

                forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)

                end = self.parent.position + forward * self.max_range
                start = (self.parent.position + forward * self.muzzle_offset[0]
                         + forward.rotate(90) * self.muzzle_offset[1])

                hit = raycast_segment(start, end, layers=[LAYERS["enemy"], LAYERS["terrain"]])

                if hit and hit[0] is not None:
                    print(f"Hit {hit[0]} at {hit[1]} with t={hit[2]:.2f}")
                    if hasattr(hit[0], "owner") and hit[0].owner:
                        if hasattr(hit[0].owner, "take_damage"):
                            hit[0].owner.take_damage(self.damage)


                self.audio_emitter.audio_clip = SOUNDS["7.62_shoot"]  # Swap to use each their own
                self.audio_emitter.play()
        else:
            # play dry fire
            print("Out of ammo! Reload needed.")


    def reload(self):
        if not self.parent: #or self.current_clip == self.clip_size:
            return
        for item in self.parent.inventory.items:
            if item.ammo and item.ammo.ammo_type == self.ammo_type:
                needed = self.clip_size - self.current_clip
                to_load = min(needed, item.ammo.capacity)
                self.current_clip += to_load
                item.ammo.capacity -= to_load
                if item.ammo.capacity <= 0:
                    self.parent.inventory.remove_item(item)
                print(f"Reloaded [{to_load}] {self.ammo_type} rounds. Current clip: {self.current_clip}")
                break


    def play_trail_effect(self, screen, start_pos, direction):
        # For testing, draw a simple line representing the bullet trail
        pygame.draw.line(screen, pygame.Color("red"), start_pos, start_pos + direction * self.max_range, 2)