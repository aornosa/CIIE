from weapons.weapon_module import Weapon

class Ranged(Weapon):
    def __init__(self, asset, name, damage, max_range, ammo_type, clip_size, fire_rate, reload_time, lock_time=0):
        super().__init__(asset, name, damage)
        self.max_range = max_range      # Maximum effective range in meters before bullet despawns
        self.ammo_type = ammo_type      # Calliber used (shotgun, high, low, etc.)
        self.clip_size = clip_size      # Number of rounds per clip/magazine
        self.fire_rate = fire_rate      # Time between shots in seconds
        self.reload_time = reload_time  # Time to reload in seconds

        ## Consider adding damage dropoff

        # Lock time used only for delay before a shot after pressing LMB
        self.lock_time = lock_time

        self.current_clip = self.clip_size

    def shoot(self):
        pass