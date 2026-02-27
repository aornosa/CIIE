from weapons.melee.melee import Melee

class TacticalKnife(Melee):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/knife/knife.png",
            name="Cuchillo Táctico",
            damage=40,
            reach=60,           # Short reach
            attack_speed=2.0,   # Fast attacks (2 per second)
            reach_radius=30
        )
        self.attack_sound_key = "knife_slash"  # Configure when sound asset is available

class Baton(Melee):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/baton/baton.png",
            name="Porra Antidisturbios",
            damage=45,
            reach=100,          # Longer reach than knife
            attack_speed=1.5,   # Moderate speed (1.5 per second)
            reach_radius=50
        )
        self.attack_sound_key = "baton_hit"  # Configure when sound asset is available