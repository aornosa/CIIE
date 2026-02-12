class PoolableObject:
    def __init__(self):
        self._active = False

    def is_active(self):
        return self._active

    def set_active(self, state):
        self._active = state