import pygame

from settings import MAX_AUDIO_CHANNELS
from audio_clip import AudioClip

class AudioManager:
    def __init__(self):
        self.mixer = pygame.mixer
        self.mixer.init()
        self.mixer.set_num_channels(MAX_AUDIO_CHANNELS)

        self.channels = {}


    def play_audio_clip(self, clip):
        channel = self._get_channel()
        if channel:
            channel.play(clip)

    def _get_channel(self):
        for channel in self.channels:
            pass
        return self.mixer.Channel(0)