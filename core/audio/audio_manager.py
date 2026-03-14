from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
import pygame.mixer_music
if TYPE_CHECKING:
    from core.audio.audio_emitter import AudioEmitter
from core.audio.audio_mixer_category import SoundCategory
from core.monolite_behaviour import MonoliteBehaviour
from settings import MAX_AUDIO_CHANNELS
from core.audio.audio_clip import AudioClip

class AudioManager(MonoliteBehaviour):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self): AudioManager.instance()

    def __init__(self):
        MonoliteBehaviour.__init__(self)
        try:
            pygame.mixer.set_num_channels(MAX_AUDIO_CHANNELS)
            self.mixer_available = True
        except pygame.error:
            self.mixer_available = False

        self.listener = None
        self.master_volume = 1.0
        self.mixer_volumes = {
            SoundCategory.MUSIC: 1.0,
            SoundCategory.SFX: 1.0,
        }
        self.active_channels = {}
        self._current_music_path = None

    def set_listener(self, listener): self.listener = listener

    def set_master_volume(self, volume):
        self.master_volume = max(0.0, min(1.0, volume))
        self._apply_music_volume()

    def set_mixer_volume(self, category, volume):
        if category in self.mixer_volumes:
            self.mixer_volumes[category] = max(0.0, min(1.0, volume))
            if category == SoundCategory.MUSIC:
                self._apply_music_volume()

    def play_music(self, path: str, loops: int = -1, fade_ms: int = 0):
        if not self.mixer_available:
            return
        try:
            if self._current_music_path != path:
                pygame.mixer.music.load(path)
                self._current_music_path = path
            self._apply_music_volume()
            if fade_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"[AudioManager] No se pudo reproducir música '{path}': {e}")

    def stop_music(self, fade_ms: int = 0):
        if not self.mixer_available:
            return
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

    def pause_music(self):
        if self.mixer_available:
            pygame.mixer.music.pause()

    def resume_music(self):
        if self.mixer_available:
            pygame.mixer.music.unpause()

    def is_music_playing(self) -> bool:
        return self.mixer_available and pygame.mixer.music.get_busy()

    def _apply_music_volume(self):
        if not self.mixer_available:
            return
        vol = self.master_volume * self.mixer_volumes.get(SoundCategory.MUSIC, 1.0)
        pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))

    def play_sound(self, audio_clip: AudioClip, emitter: AudioEmitter):
        if not self.mixer_available or audio_clip.source is None:
            return
        if self.listener is None:
            return

        distance = self.listener.get_position().distance_to(emitter.get_position())
        if distance > emitter.max_distance:
            return

        # Atenuación lineal por distancia, escalada por volúmenes de categoría y master
        volume = 1 - (distance / emitter.max_distance)
        volume *= (audio_clip.base_volume * self.master_volume *
                   self.mixer_volumes.get(audio_clip.category, 1.0))
        if volume <= 0:
            return

        # Panning estéreo: desplazamiento en X normalizado al rango [-1, 1]
        delta_x = self.listener.get_position().x - emitter.get_position().x
        pan = max(-1, min(1, delta_x / emitter.max_distance))
        left  = volume * (1 - pan) / 2 if pan < 0 else volume / 2
        right = volume * (1 + pan) / 2 if pan > 0 else volume / 2

        channel = self.get_available_channel(audio_clip.priority)
        # Penaliza la prioridad efectiva según distancia para el robo de canal
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
        if not self.mixer_available:
            return None

        channel = pygame.mixer.find_channel()
        if channel:
            return channel

        # Sin canales libres: busca el canal activo de menor prioridad
        lowest_prio    = float('inf')
        lowest_channel = None
        for ch, data in self.active_channels.items():
            if data["priority"] < lowest_prio:
                lowest_prio    = data["priority"]
                lowest_channel = ch

        # Roba el canal solo si el sonido nuevo tiene mayor prioridad
        if lowest_channel and lowest_prio < new_clip_priority:
            lowest_channel.stop()
            del self.active_channels[lowest_channel]
            return lowest_channel

        return None

    def update(self):
        # Libera entradas de canales que ya terminaron de reproducirse
        dead_channels = [ch for ch, data in self.active_channels.items()
                         if not ch.get_busy()]
        for ch in dead_channels:
            del self.active_channels[ch]