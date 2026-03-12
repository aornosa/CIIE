"""
MusicManager
------------
Gestiona la música de fondo del juego.
"""
from __future__ import annotations

import os
import random
import pygame

_MUSIC_DIRS = {
    "fight": "assets/music/fight_music",
    "idle":  "assets/music/idle_music",
    "menu":  "assets/music/menu_music",
}

_FADE_MS        = 800
_MUSIC_ENDEVENT = pygame.USEREVENT + 10


class MusicManager:
    _instance: "MusicManager | None" = None

    @classmethod
    def instance(cls) -> "MusicManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._tracks: dict[str, list[str]] = {}
        for cat, folder in _MUSIC_DIRS.items():
            self._tracks[cat] = self._scan(folder)

        self._current_category: str | None = None
        self._playlist: list[str] = []

        # ── Comprobar mixer de forma segura ──────────────────────────────────
        try:
            self._mixer_ok = pygame.mixer.get_init() is not None
        except pygame.error:
            self._mixer_ok = False

        if self._mixer_ok:
            try:
                pygame.mixer.music.set_endevent(_MUSIC_ENDEVENT)
            except pygame.error:
                self._mixer_ok = False

    # ── API pública ────────────────────────────────────────────────────────────

    def set_category(self, category: str):
        """Cambia a la categoría indicada. No hace nada si ya está activa."""
        if not self._mixer_ok:
            return
        if category == self._current_category:
            return
        if category not in self._tracks or not self._tracks[category]:
            return
        self._current_category = category
        self._playlist = []
        try:
            self._play_next(fade_out=pygame.mixer.music.get_busy())
        except pygame.error:
            self._mixer_ok = False

    def handle_event(self, event: pygame.event.Event):
        if not self._mixer_ok:
            return
        if event.type == _MUSIC_ENDEVENT:
            self._play_next(fade_out=False)

    def stop(self, fade_ms: int = _FADE_MS):
        self._current_category = None
        if self._mixer_ok:
            try:
                pygame.mixer.music.fadeout(fade_ms)
            except pygame.error:
                pass

    # ── Lógica interna ─────────────────────────────────────────────────────────

    def _play_next(self, fade_out: bool = False):
        if not self._mixer_ok or self._current_category is None:
            return

        if not self._playlist:
            tracks = list(self._tracks[self._current_category])
            random.shuffle(tracks)
            self._playlist = tracks

        if not self._playlist:
            return

        path = self._playlist.pop(0)
        try:
            if fade_out:
                pygame.mixer.music.fadeout(_FADE_MS)
            pygame.mixer.music.load(path)
            self._apply_volume()
            pygame.mixer.music.play(0, fade_ms=_FADE_MS if fade_out else 0)
        except pygame.error as e:
            print(f"[MusicManager] No se pudo reproducir '{path}': {e}")

    def _apply_volume(self):
        try:
            from core.audio.audio_manager import AudioManager
            from core.audio.audio_mixer_category import SoundCategory
            am = AudioManager.instance()
            vol = am.master_volume * am.mixer_volumes.get(SoundCategory.MUSIC, 1.0)
            pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))
        except Exception:
            try:
                pygame.mixer.music.set_volume(1.0)
            except pygame.error:
                pass

    @staticmethod
    def _scan(folder: str) -> list[str]:
        if not os.path.isdir(folder):
            return []
        exts = {".mp3", ".ogg", ".wav"}
        return [
            os.path.join(folder, f)
            for f in sorted(os.listdir(folder))
            if os.path.splitext(f)[1].lower() in exts
        ]