from __future__ import annotations
import pygame
from map.interactables.interactable import Interactable
from map.interactables.interaction_manager import InteractionManager


class Door(Interactable):
    _IMAGE_PATH = "assets/interactables/door.png"

    def __init__(self, name: str, position, on_open=None,
                 orientation: str = "horizontal", unlock_condition=None):
        self.position          = pygame.Vector2(position)
        self.is_open           = False
        self._on_open_callback = on_open
        self.orientation       = orientation
        self._image            = None
        # Condición que debe cumplirse para poder abrir la puerta
        self._unlock_condition = unlock_condition
        super().__init__(
            name=name,
            description="",
            interact_text=f"[E] Abrir {name}",
            interact_radius=100,
        )
        InteractionManager().register(self)

    def get_tooltip(self) -> str:
        return "" if self.is_open else self.interact_text

    def is_player_in_range(self, player_position: pygame.Vector2) -> bool:
        return not self.is_open and self.position.distance_to(player_position) <= self.interact_radius

    def interact(self, player):
        if self.is_open:
            return
        if self._unlock_condition and not self._unlock_condition():
            return
        self.is_open = True
        InteractionManager().unregister(self)
        if self._on_open_callback:
            self._on_open_callback()

    def _load_image(self):
        try:
            self._image = pygame.image.load(self._IMAGE_PATH).convert_alpha()
        except Exception:
            # False indica fallo de carga — evita reintentar cada frame
            self._image = False

    def draw(self, screen, camera):
        if self.is_open:
            return
        if self._image is None:
            self._load_image()
        sp = self.position - camera.position
        if self._image:
            img = self._image if self.orientation == "horizontal" else pygame.transform.rotate(self._image, 90)
            screen.blit(img, (sp.x - img.get_width() // 2, sp.y - img.get_height() // 2))
        else:
            if self.orientation == "vertical":
                rect = pygame.Rect(sp.x - 40, sp.y - 70, 80, 140)
            else:
                rect = pygame.Rect(sp.x - 70, sp.y - 40, 140, 80)
            pygame.draw.rect(screen, (80,  50,  20), rect)
            pygame.draw.rect(screen, (150, 100, 50), rect, 3)