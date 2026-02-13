import pygame
from settings import *


class Object:
    def __init__(self, asset, position=(0, 0), rotation=0, scale=1):
        self.asset = pygame.image.load(asset).convert_alpha()
        self.position = pygame.Vector2(position)

        self.rotation = rotation
        self.scale = scale

        # Cached transformed surfaces
        self._scaled_asset = None
        self._scaled_scale = None

        self._render_asset = None  # final (scaled + rotated) surface
        self._render_rotation = None
        self._render_scale = None

        # Initial build
        self._rebuild_cache(force=True)

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = pygame.Vector2(position)

    def get_rotation(self):
        return self.rotation

    def set_rotation(self, rotation):
        self.rotation = rotation

    def get_scale(self):
        return self.scale

    def set_scale(self, scale):
        self.scale = scale

    def _get_scaled_asset(self):
        # Pre-scale once per scale change
        if self._scaled_asset is None or self._scaled_scale != self.scale:
            if self.scale == 1:
                self._scaled_asset = self.asset
            else:
                w, h = self.asset.get_size()
                sw = max(1, int(w * self.scale))
                sh = max(1, int(h * self.scale))
                self._scaled_asset = pygame.transform.scale(self.asset, (sw, sh))
            self._scaled_scale = self.scale
        return self._scaled_asset

    def _rebuild_cache(self, force=False):
        if not force and self._render_rotation == self.rotation and self._render_scale == self.scale:
            return

        base = self._get_scaled_asset()

        # Skip rotation entirely if not needed
        if self.rotation % 360 == 0:
            self._render_asset = base
        else:
            self._render_asset = pygame.transform.rotate(base, self.rotation)

        self._render_rotation = self.rotation
        self._render_scale = self.scale

    def draw(self, surface, camera):
        self._rebuild_cache()

        screen_pos = self.position - camera.position
        rect = self._render_asset.get_rect(center=screen_pos)
        surface.blit(self._render_asset, rect)