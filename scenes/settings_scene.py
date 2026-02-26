import pygame
from core.scene import Scene
from ui.settings_menu import draw_settings_menu


class SettingsScene(Scene):
    """Settings / options menu – can be reached from MainMenu or PauseMenu."""

    def __init__(self):
        super().__init__()
        self.options = ["Audio (placeholder)", "Video (placeholder)", "Volver"]
        self.selected = 0

    def handle_events(self, input_handler):
        # ESC to go back
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            self.director.pop()
            return

        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            self.selected = (self.selected - 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
            self.selected = (self.selected + 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select_option()

    def update(self, delta_time):
        pass

    def render(self, screen):
        draw_settings_menu(screen, self.options, self.selected)

    def on_enter(self):
        pygame.mouse.set_visible(True)

    # -- Option handlers --------------------------------------------------

    def _select_option(self):
        option = self.options[self.selected]

        if option == "Volver":
            self.director.pop()
