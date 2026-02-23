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
        # Check for pause (ESC)
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

        # All other input is handled inside game_update via the input_handler

    def update(self, delta_time):
        game.game_update(delta_time, self._get_input_handler())
        MonoliteBehaviour.update_all(delta_time)

        # Check if a trigger zone fired this frame
        if game.red_zone.pending:
            game.red_zone.consume()
            from scenes.red_zone_event_scene import RedZoneEventScene
            self.director.push(RedZoneEventScene(self))

        elif game.blue_zone.pending:
            game.blue_zone.consume()
            from scenes.blue_zone_event_scene import BlueZoneEventScene
            self.director.push(BlueZoneEventScene(self))

    def render(self, screen):
        game.game_render(screen)

    def on_enter(self):
        pygame.mouse.set_visible(False)

    # -- Helpers -----------------------------------------------------------

    def _get_input_handler(self):
        """Retrieve the shared InputHandler stored on the director."""
        return self.director._input_handler
