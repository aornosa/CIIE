from weapons.melee.melee import Melee

class TacticalKnife(Melee):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/knife/knife.png",
            name="Cuchillo Táctico",
            damage=90,           # era 40
            reach=240,
            attack_speed=2.5,    # era 2.0
            reach_radius=160,
        )
        self.attack_sound_key = "knife_slash"


class Baton(Melee):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/baton/baton.png",
            name="Porra Antidisturbios",
            damage=110,          # era 45
            reach=280,
            attack_speed=1.8,    # era 1.5
            reach_radius=220,
        )
        self.attack_sound_key = "baton_hit"
        self.particle_color = (100, 200, 255)
        from core.particles.particle_emitter import ParticleEmitter
        from core.particles.particle import Particle
        impact_particle_asset = self._create_impact_particle()
        particle_factory = lambda: Particle(impact_particle_asset)
        self.impact_emitter = ParticleEmitter(particle_factory, speed=300, lifespan=0.6)