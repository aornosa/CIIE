import pygame
from core.scene import Scene
from core.monolite_behaviour import MonoliteBehaviour

# game.py holds all the game state and logic – we just delegate to it
import game


class GameScene(Scene):
    """Main gameplay scene – wraps the existing game.py logic."""

    def __init__(self):
        super().__init__()

    def handle_events(self, input_handler):
        # Check for pause (ESC) – flag is reset automatically each frame by reset_frame()
        if input_handler.actions.get("pause"):
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

        # DEBUG: Temporary development shortcut to open BlueZoneEventScene with F12.
        # Remove this binding or guard it behind a debug flag before production release.
        if input_handler.keys_just_pressed.get(pygame.K_F12):
            from scenes.blue_zone_event_scene import BlueZoneEventScene
            self.director.push(BlueZoneEventScene(self))

    def update(self, delta_time):
        game.game_update(delta_time, self._get_input_handler())
        MonoliteBehaviour.update_all(delta_time)

    def render(self, screen):
        game.game_render(screen)

    def on_enter(self):
        pygame.mouse.set_visible(False)

    # -- Helpers -----------------------------------------------------------

    def _get_input_handler(self):
        """Retrieve the shared InputHandler stored on the director."""
        return self.director._input_handler
