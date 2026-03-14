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
                 fire_rate, reload_time, muzzle_speed=3000, muzzle_offset=(0, 0), lock_time=0):
        super().__init__(asset, name, damage)
        MonoliteBehaviour.__init__(self)

        self.max_range     = max_range
        self.ammo_type     = ammo_type
        self.reload_time   = reload_time
        self.muzzle_speed  = muzzle_speed
        self.muzzle_offset = muzzle_offset
        self.lock_time     = lock_time

        # Stats base — las propiedades suman los upgrades del jugador encima
        self._base_damage    = damage
        self._base_clip_size = clip_size
        self._base_fire_rate = fire_rate
        self._base_reload_time = reload_time

        self.current_clip       = clip_size
        self._last_shot_time    = 0
        self._is_reloading      = False
        self._reload_start_time = 0

        particle_asset   = self._load_ammo_particle()
        particle_factory = lambda: Particle(particle_asset)
        self.emitter     = ParticleEmitter(particle_factory, speed=muzzle_speed, lifespan=0.5)

    def _upgrades(self):
        # Devuelve los upgrades del jugador o ceros si no hay parent
        if self.parent and hasattr(self.parent, "weapon_upgrades"):
            return self.parent.weapon_upgrades
        return {"ranged_damage": 0, "ranged_clip": 0, "ranged_fire_rate": 0.0, "ranged_reload_time": 0.0}

    @property
    def damage(self):
        return self._base_damage + self._upgrades().get("ranged_damage", 0)

    @damage.setter
    def damage(self, value):
        self._base_damage = value

    @property
    def clip_size(self):
        return self._base_clip_size + self._upgrades().get("ranged_clip", 0)

    @clip_size.setter
    def clip_size(self, value):
        self._base_clip_size = value

    @property
    def fire_rate(self):
        return max(0.05, self._base_fire_rate + self._upgrades().get("ranged_fire_rate", 0.0))

    @fire_rate.setter
    def fire_rate(self, value):
        self._base_fire_rate = value

    @property
    def reload_time(self):
        return max(0.3, self._base_reload_time + self._upgrades().get("ranged_reload_time", 0.0))

    @reload_time.setter
    def reload_time(self, value):
        self._base_reload_time = value

    def _load_ammo_particle(self):
        try:
            with open(AMMO_TYPES[self.ammo_type], 'r', encoding="utf-8") as f:
                ammo_data = json.load(f)
            return pygame.image.load(ammo_data["asset_particle_path"]).convert_alpha()
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            surface.fill((255, 230, 80, 220))
            return surface

    def update(self):
        if self.parent is not None:
            direction = pygame.Vector2(0, -1).rotate(-self.parent.rotation)
            self.emitter.set_position(
                self.parent.position
                + direction * self.muzzle_offset[0]
                + direction.rotate(90) * self.muzzle_offset[1]
            )
            self.emitter.set_rotation(self.parent.rotation)

        if self._is_reloading:
            elapsed = (pygame.time.get_ticks() - self._reload_start_time) / 1000.0
            if elapsed >= self.reload_time:
                self._finish_reload()

    def _finish_reload(self):
        self._is_reloading = False
        self.current_clip  = self.clip_size

    def cancel_reload(self):
        self._is_reloading = False

    def on_unequipped(self):
        self.cancel_reload()
        super().on_unequipped()

    def can_shoot(self) -> bool:
        return (
            self.current_clip > 0
            and not self._is_reloading
            and self._last_shot_time + self.fire_rate * 1000 <= pygame.time.get_ticks()
        )

    def is_reloading(self) -> bool:
        return self._is_reloading

    def shoot(self) -> bool:
        if not self.parent or not self.can_shoot():
            return False

        self._last_shot_time = pygame.time.get_ticks()
        self.current_clip -= 1

        forward = pygame.math.Vector2(0, -1).rotate(-self.parent.rotation)
        start   = (self.parent.position
                   + forward * self.muzzle_offset[0]
                   + forward.rotate(90) * self.muzzle_offset[1])
        end     = self.parent.position + forward * self.max_range

        hit = raycast_segment(start, end, layers=[LAYERS["enemy"], LAYERS["terrain"]])
        if hit and hit[0] is not None:
            dist = pygame.Vector2(start).distance_to(pygame.Vector2(hit[1]))
            self._handle_hit(hit[0], hit[1])
        else:
            dist = self.max_range

        original_lifespan     = self.emitter.lifespan
        self.emitter.lifespan = dist / self.muzzle_speed if self.muzzle_speed > 0 else 0.5
        self.emitter.emit()
        self.emitter.lifespan = original_lifespan

        self._play_shoot_sound()
        return True

    def _handle_hit(self, hit_collider, hit_position):
        owner = getattr(hit_collider, "owner", None)
        if owner and hasattr(owner, "take_damage"):
            owner.take_damage(self.damage)

    def _play_shoot_sound(self):
        if self.audio_emitter:
            try:
                self.audio_emitter.audio_clip = SOUNDS[f"{self.ammo_type}_shoot"]
                self.audio_emitter.play()
            except (KeyError, AttributeError):
                pass

    def reload(self) -> bool:
        if not self.parent:
            return False
        if self.current_clip == self.clip_size or self._is_reloading:
            return False
        self._start_reload()
        return True

    def _start_reload(self):
        self._is_reloading      = True
        self._reload_start_time = pygame.time.get_ticks()
        self._play_reload_sound()

    def _play_reload_sound(self):
        if self.audio_emitter:
            try:
                self.audio_emitter.audio_clip = SOUNDS[f"{self.ammo_type}_reload"]
                self.audio_emitter.play()
            except (KeyError, AttributeError):
                pass

    def get_ammo_count(self) -> tuple[int, int]:
        return self.current_clip, self.clip_size

    def play_trail_effect(self, screen, start_pos, direction):
        pass