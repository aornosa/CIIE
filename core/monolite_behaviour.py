## Based on Unity's MonoBehaviour adapted to Python for game development.

class MonoliteBehaviour:
    _instances = []  # Global class variable for running instances

    def __init__(self):
        self.enabled = True  # Whether the behaviour is active

        MonoliteBehaviour._instances.append(self)  # Add instance to the global list

    def update(self, delta_time):
        pass

    def destroy(self):
        if self in MonoliteBehaviour._instances:
            MonoliteBehaviour._instances.remove(self)  # Remove instance from the global list

    @classmethod
    def update_all(cls, delta_time):
        for instance in cls._instances:
            if instance.enabled:
                instance.update(delta_time)