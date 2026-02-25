import pygame.mixer_music

from core.audio.audio_mixer_category import SoundCategory


class AudioClip:
    def __init__(self, source_path, base_volume=1.0, priority=0, category=SoundCategory.SFX):
        self.source = pygame.mixer.Sound(source_path)
        self.priority = priority

        self.base_volume = max(0.0, min(1.0, base_volume))
        self.category = category