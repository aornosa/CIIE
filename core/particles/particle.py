from core.monolite_behaviour import MonoliteBehaviour
from core.pools.poolable_object import PoolableObject


class Particle(PoolableObject):
    def __init__(self, asset, lifespan=10):
        super().__init__()
        self.emitter = None
        self.asset = asset
        self.position = (0, 0)
        self.rotation = 0
        self.scale = 0.2
        self.velocity = (0, 0)
        self.age = lifespan


    def update(self):
        if not self.is_active():
            return
        self.age -= MonoliteBehaviour.delta_time
        if self.age <= 0:
            self.set_active(False)
            self.emitter.kill_particle(self)

        self.position += (MonoliteBehaviour.delta_time * self.velocity[0],
                          MonoliteBehaviour.delta_time * self.velocity[1])
