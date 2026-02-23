from core.monolite_behaviour import MonoliteBehaviour


class AudioListener(MonoliteBehaviour):
    def __init__(self, owner):
        MonoliteBehaviour.__init__(self)
        self.owner = owner
        self.position = (0, 0)

    def set_position(self, position):
        self.set_position(position)

    def get_position(self):
        return self.position

    def sync_with_owner(self):
        if self.owner is not None:
            self.position = self.owner.get_position()

    def update(self):
        self.sync_with_owner()