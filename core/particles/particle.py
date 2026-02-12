from core.monolite_behaviour import MonoliteBehaviour
from core.poolable_object import PoolableObject


class Particle(PoolableObject, MonoliteBehaviour):
    def __init__(self, asset, position, velocity, lifespan):
        super().__init__()
        self.asset = asset
        self.position = position
        self.velocity = velocity
        self.age = lifespan

    def update(self, delta_time):
        if not self.is_active():
            return
        self.age -= delta_time
        if self.age <= 0:
            self.set_active(False)

        self.position += self.velocity * delta_time
