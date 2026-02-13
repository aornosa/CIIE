class StatusEffect:
    def __init__(self, icon, name, modifiers, duration, is_buff=True):
        self.icon = icon
        self.name = name
        self.modifiers = modifiers
        self.duration = duration
        self.remaining = duration
        self.is_buff = is_buff
        self.is_toggle = duration == -1
        self.is_stackable = False

    def tick(self, delta_time):
        if not self.is_buff:
            self.remaining -= delta_time