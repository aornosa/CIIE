from __future__ import annotations
import pygame
from map.interactables.interactable import Interactable
from map.interactables.interaction_manager import InteractionManager

class Door(Interactable):
    def __init__(self, name: str, position, cost: int, on_open=None, orientation: str = "horizontal"):
        self.position          = pygame.Vector2(position)
        self.cost              = cost
        self.is_open           = False
        self._on_open_callback = on_open
        self.orientation       = orientation
        super().__init__(
            name=name,
            description=f"Cuesta {cost} puntos abrir esta puerta.",
            interact_text=f"[E] Abrir {name} ({cost} pts)",
            interact_radius=100,
        )
        InteractionManager().register(self)

    def get_tooltip(self) -> str:
        return "" if self.is_open else self.interact_text

    def is_player_in_range(self, player_position: pygame.Vector2) -> bool:
        return not self.is_open and self.position.distance_to(player_position) <= self.interact_radius

    def interact(self, player):
        if self.is_open or player.score < self.cost:
            return
        player.score -= self.cost
        self.is_open  = True
        InteractionManager().unregister(self)
        if self._on_open_callback:
            self._on_open_callback()

    def draw(self, screen, camera):
        if self.is_open:
            return
        sp = self.position - camera.position
        # Geometría según orientación: vertical más alta, horizontal más ancha
        if self.orientation == "vertical":
            rect = pygame.Rect(sp.x - 40, sp.y - 70, 80, 140)
        else:
            rect = pygame.Rect(sp.x - 70, sp.y - 40, 140, 80)
        pygame.draw.rect(screen, (80,  50,  20), rect)
        pygame.draw.rect(screen, (150, 100, 50), rect, 3)
        label = pygame.font.SysFont("consolas", 16).render(f"{self.cost}pts", True, (255, 220, 50))
        screen.blit(label, (sp.x - label.get_width() // 2, sp.y - 60))