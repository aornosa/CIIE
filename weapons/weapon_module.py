import pygame

from core.audio.audio_emitter import AudioEmitter
from core.object import Object

AMMO_TYPES = {
    "9x19": "assets/ammo/9x19/data.json",
    "7.62": "assets/ammo/7.62/data.json",
    "12gauge": "assets/ammo/12Gauge/data.json",
}


class Weapon:
    """Base class for all weapons in the game."""
    
    def __init__(self, asset, name, damage, pullout_time=0):
        """
        Initialize a weapon.
        
        Args:
            asset: Path to weapon sprite
            name: Display name of weapon
            damage: Base damage value
            pullout_time: Time in seconds to equip the weapon
        """
        self.asset = pygame.image.load(asset)
        self.name = name
        self.damage = damage
        self.object = Object(asset, (0, 0), 0, 1)
        self.pullout_time = pullout_time
        
        # Set by character when equipped
        self.parent = None
        self.audio_emitter = None
    
    def update(self):
        """Called each frame. Override in subclasses."""
        pass
    
    def get_name(self) -> str:
        """Get weapon display name."""
        return self.name
    
    def get_damage(self) -> int:
        """Get base damage value."""
        return self.damage
    
    def get_asset(self):
        """Get weapon sprite."""
        return self.asset
    
    def on_equipped(self, parent):
        """Called when weapon is equipped by a character."""
        self.parent = parent
        if parent and hasattr(parent, 'audio_emitter'):
            self.audio_emitter = parent.audio_emitter
    
    def on_unequipped(self):
        """Called when weapon is unequipped."""
        self.parent = None
        self.audio_emitter = None