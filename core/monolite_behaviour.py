## Based on Unity's MonoBehaviour adapted to Python for game development.

class MonoliteBehaviour:
    _instances = []  # Global class variable for running instances

    def __init__(self):
        self._enabled = True  # Whether the behaviour is active

        self._awakened = False  # To track if awake() has been called
        self._started = False  # To track if start() has been called

        MonoliteBehaviour._instances.append(self)  # Add instance to the global list

        self._call_awake()

    def _call_awake(self):
        if not self._awakened:
            self.awake()
            self._awakened = True


    def awake(self):
        pass

    def start(self):
        pass

    def update(self, delta_time):
        pass

    def on_enable(self):
        pass

    def on_disable(self):
        pass

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled == value:
            return
        self._enabled = value
        if self._enabled:
            self.on_enable()
        else:
            self.on_disable()


    def destroy(self):
        self.on_destroy()
        if self in MonoliteBehaviour._instances:
            MonoliteBehaviour._instances.remove(self)  # Remove instance from the global list

    def on_destroy(self):
        pass

    @classmethod
    def update_all(cls, delta_time):
        for instance in cls._instances:
            if instance.enabled:
                instance.update(delta_time)

            if not instance.enabled:
                continue

            if not instance._started:
                instance.start()
                instance._started = True