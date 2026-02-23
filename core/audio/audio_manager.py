import pygame

from core.audio.audio_emitter import AudioEmitter
from core.audio.audio_mixer_category import SoundCategory
from core.monolite_behaviour import MonoliteBehaviour
from settings import MAX_AUDIO_CHANNELS
from audio_clip import AudioClip

class AudioManager(MonoliteBehaviour):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        MonoliteBehaviour.__init__(self)
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

        distance = self.listener.get_position().distance_to(emitter.get_position())

        if distance > emitter.max_distance:
            return

        volume = 1 - (distance/emitter.max_distance) # Linear distance falloff

        volume *= (audio_clip.base_volume * self.master_volume *
                   self.mixer_volumes.get(audio_clip.category, 1.0))

        if volume <= 0:
            return

        # Stereo panning
        delta_x = self.listener.get_position().x - emitter.get_position().x
        pan = max(-1, min(1, delta_x / emitter.max_distance))

        left = volume * (1 - pan) / 2 if pan < 0 else volume / 2
        right = volume * (1 + pan) / 2 if pan > 0 else volume / 2

        channel = self.get_available_channel(audio_clip.priority)

        effective_prio = audio_clip.priority - distance * 0.01

        if channel is None:
            return

        channel.set_volume(left, right)
        channel.play(audio_clip.source)

        self.active_channels[channel] = {
            "emitter": emitter,
            "clip": audio_clip,
            "priority": effective_prio,
        }




    def get_available_channel(self, new_clip_priority):
        channel = pygame.mixer.find_channel()

        if channel:
            return channel # Free available

        # If no free channels, steal from lower prio
        lowest_prio = float('inf')
        lowest_channel = None

        for ch, data in self.active_channels.items():
            if data["priority"] < lowest_prio:
                lowest_prio = data["priority"]
                lowest_channel = ch

        if lowest_channel and lowest_prio < new_clip_priority:
            lowest_channel.stop()
            del self.active_channels[lowest_channel]
            return lowest_channel

        return None # Current sound is lowest prio


    def update(self):
        # Cleanup
        dead_channels = [
            ch for ch, data in self.active_channels.items()
            if not ch.get_busy()
        ]
        for ch in dead_channels:
            del self.active_channels[ch]
