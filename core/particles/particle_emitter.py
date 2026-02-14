import pygame

from core.monolite_behaviour import MonoliteBehaviour
from core.pools.object_pool import Pool
from core.virtual_object import VirtualObject


class ParticleEmitter(VirtualObject, MonoliteBehaviour):
    def __init__(self, particle_factory, position = (0, 0), scale=1,  speed=300, lifespan=10):
        VirtualObject.__init__(self, position, 0)
        MonoliteBehaviour.__init__(self)
        self.lifespan = lifespan
        self.speed = speed
        self.scale = scale

        self.surface = None
        self.camera = None

        self.active_particles = []
        self.particle_pool = Pool(particle_factory, starting_size=100)


    def emit(self):
        particle = self.particle_pool.acquire()

        particle.emitter = self # Backreference so the particle can call back to the emitter when it dies
        particle.position = pygame.Vector2(self.position)
        particle.age = self.lifespan # change to use max_range/speed

        forward = pygame.math.Vector2(0, -1).rotate(-self.rotation)
        particle.velocity = forward * self.speed
        particle.rotation = self.rotation + 90
        self.active_particles.append(particle)

    def kill_particle(self, particle):
        if particle in self.active_particles:
            self.active_particles.remove(particle)
            self.particle_pool.release(particle)

    def update(self):
        for particle in self.active_particles:
            particle.update()
            self._draw_particle(particle)

    def _draw_particle(self, particle):
        if self.surface is None or self.camera is None:
            return
        if particle.is_active():
            scaled_asset = pygame.transform.scale(particle.asset, (int(particle.asset.get_width() * particle.scale),
                                                                int(particle.asset.get_height() * particle.scale)))
            rotated_asset = pygame.transform.rotate(scaled_asset, particle.rotation)
            center_screen = particle.position - self.camera.position
            rect = rotated_asset.get_rect(center=(int(center_screen.x), int(center_screen.y)))
            self.surface.blit(rotated_asset, rect.topleft)

