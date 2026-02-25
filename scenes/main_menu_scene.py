import pygame
from core.scene import Scene
from ui.main_menu import draw_main_menu


class MainMenuScene(Scene):
    """Main menu – first scene the player sees."""

    def __init__(self):
        super().__init__()
        self.options = ["Jugar", "Opciones", "Salir"]
        self.selected = 0

    def handle_events(self, input_handler):
        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            self.selected = (self.selected - 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
            self.selected = (self.selected + 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select_option()

    def update(self, delta_time):
        pass  # Menu has no dynamic logic

    def render(self, screen):
        draw_main_menu(screen, self.options, self.selected)

    def on_enter(self):
        pygame.mouse.set_visible(True)

    # -- Option handlers --------------------------------------------------

    def _select_option(self):
        option = self.options[self.selected]

        if option == "Jugar":
            from scenes.game_scene import GameScene
            self.director.replace(GameScene())

        elif option == "Opciones":
            from scenes.settings_scene import SettingsScene
            self.director.push(SettingsScene())

        elif option == "Salir":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
