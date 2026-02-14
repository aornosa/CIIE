import pygame.mixer_music


class AudioClip:
    def __init__(self, source_path: str, priority=0):
        self.source = pygame.mixer.Sound(source_path)
        self.priority = priority