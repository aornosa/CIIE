from weapons.melee.melee import Melee

class TacticalKnife(Melee):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/knife/knife.png",
            name="Cuchillo Táctico",
            damage=70,
            reach=180,
            fire_rate=0.29,
            reach_radius=120,
        )
        self.attack_sound_key = "knife_slash"

class Baton(Melee):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/baton/baton.png",
            name="Porra Antidisturbios",
            damage=130,
            reach=340,
            fire_rate=0.71,
            reach_radius=260,
        )
        self.attack_sound_key = "baton_hit"
        self.particle_color   = (100, 200, 255)

        from core.particles.particle_emitter import ParticleEmitter
        from core.particles.particle import Particle
        particle_factory    = lambda: Particle(self._create_impact_particle())
        self.impact_emitter = ParticleEmitter(particle_factory, speed=300, lifespan=0.6)