from core.object_pool import Pool


class ParticleEmitter:
    def __init__(self, particle):
        self.particle_pool = Pool(particle, starting_size=100)


    def emit(self):
        pass
