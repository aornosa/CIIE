import pygame.mixer_music

from core.audio.audio_mixer_category import SoundCategory


class AudioClip:
    def __init__(self, source_path, base_volume=1.0, priority=0, category=SoundCategory.SFX):
        try:
            self.source = pygame.mixer.Sound(source_path)
        except pygame.error:
            # If mixer is not available or file not found, create a dummy sound
            self.source = None
        
        self.priority = priority
        self.base_volume = max(0.0, min(1.0, base_volume))
        self.category = category