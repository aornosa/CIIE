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
        if not self.is_toggle:
            self.remaining -= delta_time

    # Compatibilidad con código que espera una API estilo update().
    def update(self, delta_time):
        self.tick(delta_time)

    def is_expired(self) -> bool:
        return (not self.is_toggle) and self.remaining <= 0