import pygame
from core.monolite_behaviour import MonoliteBehaviour
import time

class FPS_Counter(MonoliteBehaviour):
    def __init__(self, font_size=24, color=(255, 255, 255)):
        super().__init__()
        self.font = pygame.font.SysFont("Arial", font_size)
        self.color = color
        self.fps = 0
        self.last_update = 0
        self.update_interval = 0.5


    def update(self):       
        now = time.time()
        if now - self.last_update >= self.update_interval:
            self.fps = int(1 / MonoliteBehaviour.delta_time) if MonoliteBehaviour.delta_time > 0 else 0
            self.last_update = now
        self.draw()

    def draw(self, surface=None):
        if surface is None:
            surface = pygame.display.get_surface()
        if surface is None:
            return
        fps_text = self.font.render(f"FPS: {self.fps}", True, self.color)
        surface.blit(fps_text, (10, 10))