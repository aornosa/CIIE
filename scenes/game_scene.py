import pygame
from core.scene import Scene
from core.monolite_behaviour import MonoliteBehaviour
from game import game_loop


class GameScene(Scene):
    """Wraps the existing game_loop as a Scene so it integrates with SceneDirector."""

    def __init__(self):
        super().__init__()
        self._last_frame = None

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

    def update(self, delta_time):
        pass  # game_loop handles its own update

    def render(self, screen):
        game_loop(screen, self.director.clock, self.director._input_handler)
        self._last_frame = screen.copy()

    def get_last_frame(self):
        """Return the last rendered frame (used by PauseScene to show frozen game)."""
        return self._last_frame

    def on_enter(self):
        MonoliteBehaviour.time_scale = 1.0
        pygame.mouse.set_visible(False)

    def on_exit(self):
        MonoliteBehaviour.time_scale = 0.0
