import pygame

from core.monolite_behaviour import MonoliteBehaviour
from core.object_pool import Pool
from core.virtual_object import VirtualObject


class ParticleEmitter(VirtualObject, MonoliteBehaviour):
    def __init__(self, particle_factory, position = (0, 0), lifespan=10):
        VirtualObject.__init__(self, position, 0)
        MonoliteBehaviour.__init__(self)
        self.lifespan = lifespan

        self.surface = None
        self.camera = None

        self.active_particles = []
        self.particle_pool = Pool(particle_factory, starting_size=100)


    def emit(self):
        particle = self.particle_pool.acquire()

        particle.emitter = self # Backreference so the particle can call back to the emitter when it dies
        particle.position = pygame.Vector2(self.position)
        particle.age = self.lifespan

        forward = pygame.math.Vector2(0, -1).rotate(-self.rotation)
        particle.velocity = forward * 100
        self.active_particles.append(particle)

    def kill_particle(self, particle):
        if particle in self.active_particles:
            self.active_particles.remove(particle)
            self.particle_pool.release(particle)

    def update(self):
        print("Updating Particle Emitter with", len(self.active_particles), "active particles")
        for particle in self.active_particles:
            print(particle, particle.age, particle.is_active())
            particle.update()
            self._draw_particle(particle)

    def _draw_particle(self, particle):
        if self.surface is None or self.camera is None:
            return
        if particle.is_active():
            self.surface.blit(particle.asset, particle.position - self.camera.position)
            print("drawing particle at", particle.position- self.camera.position)