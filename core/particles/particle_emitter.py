import pygame

from core.monolite_behaviour import MonoliteBehaviour
from core.object_pool import Pool
from core.virtual_object import VirtualObject


class ParticleEmitter(VirtualObject, MonoliteBehaviour):
    def __init__(self, particle_factory, position = (0, 0)):
        super().__init__(position, 0)

        self.active_particles = []
        self.particle_pool = Pool(particle_factory, starting_size=100)


    def emit(self):
        particle = self.particle_pool.acquire()
        particle.emitter = self # Backreference so the particle can call back to the emitter when it dies
        particle.position = self.position
        forward = pygame.math.Vector2(0, -1).rotate(self.rotation)
        particle.velocity = forward * 100
        self.active_particles.append(particle)

    def kill_particle(self, particle):
        if particle in self.active_particles:
            self.active_particles.remove(particle)
            self.particle_pool.release(particle)

    def update(self):
        for particle in self.active_particles:
            particle.update()