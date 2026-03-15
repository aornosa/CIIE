import pygame
from core.scene import Scene
from ui.level_complete_screen import draw_level_complete_screen

class LevelCompleteScene(Scene):
    _FADE_DURATION = 1.2

    def __init__(self, frozen_frame, level_name, stats, next_scene_class=None):
        super().__init__()
        self.frozen_frame     = frozen_frame
        self.level_name       = level_name
        self.stats            = stats
        self.next_scene_class = next_scene_class
        self.options          = ["Continuar", "Menú Principal"]
        self.selected         = 0
        self._fade_timer      = 0.0
        self._ready           = False

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def on_exit(self):
        pygame.mouse.set_visible(False)

    def handle_events(self, input_handler):
        if not self._ready:
            return
        if (input_handler.keys_just_pressed.get(pygame.K_UP) or
                input_handler.keys_just_pressed.get(pygame.K_w)):
            self.selected = (self.selected - 1) % len(self.options)
        if (input_handler.keys_just_pressed.get(pygame.K_DOWN) or
                input_handler.keys_just_pressed.get(pygame.K_s)):
            self.selected = (self.selected + 1) % len(self.options)
        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._confirm()

    def update(self, delta_time):
        if not self._ready:
            self._fade_timer += delta_time
            if self._fade_timer >= self._FADE_DURATION:
                self._fade_timer = self._FADE_DURATION
                self._ready = True

    def render(self, screen):
        alpha = int(255 * (self._fade_timer / self._FADE_DURATION))
        draw_level_complete_screen(
            screen, self.frozen_frame, self.level_name,
            self.stats, self.options, self.selected, alpha,
        )

    def _confirm(self):
        from scenes.main_menu_scene import MainMenuScene
        option = self.options[self.selected]
        if option == "Continuar" and self.next_scene_class is not None:
            self.director.replace(self.next_scene_class())
        else:
            self.director.replace(MainMenuScene())