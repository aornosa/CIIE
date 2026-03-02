## Based on Unity's MonoBehaviour adapted to Python for game development.

class MonoliteBehaviour:
    _subclasses = []  # Class variable to track subclasses
    _instances = []  # Global class variable for running instances
    delta_time = 0  # Class variable to hold delta time for all instances
    time_scale = 1.0  # 1.0 = normal, 0.0 = paused

    def __init__(self):
        self._enabled = True  # Whether the behaviour is active

        self._awakened = False  # To track if awake() has been called
        self._started = False  # To track if start() has been called

        MonoliteBehaviour._instances.append(self)  # Add instance to the global list
        print(self.__class__.__name__ + " - subscribed to MonoliteBehaviour")

        self._call_awake()

    def __init_subclass__(cls):
        super().__init_subclass__()
        MonoliteBehaviour._subclasses.append(cls)

    def _call_awake(self):
        if not self._awakened:
            self.awake()
            self._awakened = True


    def awake(self):
        pass

    def start(self):
        pass

    def update(self):
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
    def instantiate_all(cls):
        for sub in cls._subclasses:
            sub()

    @classmethod
    def update_all(cls, dt):
        cls.delta_time = dt * cls.time_scale
        for instance in cls._instances:
            if instance.enabled:
                instance.update()

            if not instance.enabled:
                continue

            if not instance._started:
                instance.start()
                instance._started = True