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
        # Color is set to default orange in Melee.__init__

class Baton(Melee):
    def __init__(self):
        # First set the color before calling super().__init__
        # We need to do this in a way that doesn't break the MRO
        # Actually, we can't set it before super().__init__() because we need Melee to be initialized
        # So we'll override after super().__init__() and recreate the emitter
        super().__init__(
            asset="assets/weapons/baton/baton.png",
            name="Porra Antidisturbios",
            damage=45,
            reach=100,          # Longer reach than knife
            attack_speed=1.5,   # Moderate speed (1.5 per second)
            reach_radius=50
        )
        self.attack_sound_key = "baton_hit"  # Configure when sound asset is available
        
        # Override particle color and recreate the emitter with new color
        self.particle_color = (100, 200, 255)  # Light blue for baton impact
        from core.particles.particle_emitter import ParticleEmitter
        from core.particles.particle import Particle
        import pygame
        
        # Recreate impact emitter with new color
        impact_particle_asset = self._create_impact_particle()
        particle_factory = lambda: Particle(impact_particle_asset)
        self.impact_emitter = ParticleEmitter(particle_factory, speed=300, lifespan=0.6)