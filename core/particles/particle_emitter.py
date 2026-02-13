from core.object_pool import Pool
from core.virtual_object import VirtualObject


class ParticleEmitter(VirtualObject):
    def __init__(self, position, particle):
        super().__init__(position, 0)

        self.particle_pool = Pool(particle, starting_size=100)


    def emit(self):
        pass
