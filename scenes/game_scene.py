import pygame
from core.scene import Scene
from core.monolite_behaviour import MonoliteBehaviour
from game import game_loop, set_director


class GameScene(Scene):
    """Wraps the existing game_loop as a Scene so it integrates with SceneDirector."""

    def __init__(self):
        super().__init__()
        self._last_frame = None
        self._director_ref = None  

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

        if input_handler.actions.get("shop"):
            input_handler.actions["shop"] = False
            from scenes.shop_scene import ShopScene
            from game import player
            self.director.push(ShopScene(self, player))
            return

    def update(self, delta_time):
        # ── Música ────────────────────────────────────────────
        from core.audio.music_manager import MusicManager
        MusicManager.instance().set_category("idle")
        pass

    def render(self, screen):
        game_loop(screen, self._director_ref.clock, self._director_ref._input_handler)
        if self._director_ref.get_current() is not self and self._last_frame is not None:
            screen.blit(self._last_frame, (0, 0))
        else:
            self._last_frame = screen.copy()

    def get_last_frame(self):
        return self._last_frame

    def on_enter(self):
        MonoliteBehaviour.time_scale = 1.0
        pygame.mouse.set_visible(False)
        self._director_ref = self.director
        set_director(self.director)

    def on_exit(self):
        MonoliteBehaviour.time_scale = 0.0