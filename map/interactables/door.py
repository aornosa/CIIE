from __future__ import annotations
import pygame
from map.interactables.interactable import Interactable
from map.interactables.interaction_manager import InteractionManager


class Door(Interactable):

    def __init__(self, name: str, position, cost: int, on_open=None, orientation: str = "horizontal"):
        self.position = pygame.Vector2(position)
        self.cost = cost
        self.is_open = False
        self._on_open_callback = on_open
        self.orientation = orientation

        interact_text = f"[E] Abrir {name} ({cost} pts)"
        super().__init__(
            name=name,
            description=f"Cuesta {cost} puntos abrir esta puerta.",
            interact_text=interact_text,
            interact_radius=100,
        )

        InteractionManager().register(self)

    def get_tooltip(self) -> str:
        if self.is_open:
            return ""   
        return self.interact_text

    def is_player_in_range(self, player_position: pygame.Vector2) -> bool:
        if self.is_open:
            return False   
        return self.position.distance_to(player_position) <= self.interact_radius

    def interact(self, player):
        if self.is_open:
            return

        if player.score < self.cost:
            print(f"[DOOR] Puntos insuficientes: {player.score}/{self.cost}")
            return

        player.score -= self.cost
        self.is_open = True
        InteractionManager().unregister(self)
        print(f"[DOOR] '{self.name}' abierta. Puntos restantes: {player.score}")

        if self._on_open_callback:
            self._on_open_callback()

    def draw(self, screen, camera):
        if self.is_open:
            return
        screen_pos = self.position - camera.position
        if self.orientation == "vertical":
            rect = pygame.Rect(screen_pos.x - 40, screen_pos.y - 70, 80, 140)
        else:
            rect = pygame.Rect(screen_pos.x - 70, screen_pos.y - 40, 140, 80)
        pygame.draw.rect(screen, (80, 50, 20), rect)
        pygame.draw.rect(screen, (150, 100, 50), rect, 3)

        font = pygame.font.SysFont("consolas", 16)
        label = font.render(f"{self.cost}pts", True, (255, 220, 50))
        screen.blit(label, (screen_pos.x - label.get_width() // 2, screen_pos.y - 60))