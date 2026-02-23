import pygame

from core.audio.audio_emitter import AudioEmitter
from core.audio.audio_mixer_category import SoundCategory
from settings import MAX_AUDIO_CHANNELS
from audio_clip import AudioClip

class AudioManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        pygame.mixer.set_num_channels(MAX_AUDIO_CHANNELS)

        self.listener = None
        self.master_volume = 1.0
        self.mixer_volumes = {
            SoundCategory.MUSIC: 1.0,
            SoundCategory.SFX: 1.0,
        }
        self.active_channels = {}

    def set_listener(self, listener):
        self.listener = listener

    def set_master_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, volume))

    def set_mixer_volume(self, category, volume):
        if category in self.mixer_volumes:
            self.mixer_volumes[category] = max(0.0, min(1.0, volume))


    def play_sound(self, audio_clip: AudioClip, emitter: AudioEmitter):
        if self.listener is None:
            return

        volume = self.master_volume * self.mixer_volumes.get(audio_clip.category, 1.0)

