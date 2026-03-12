import pygame
from core.scene import Scene
from ui.main_menu import draw_main_menu


class MainMenuScene(Scene):
    """Main menu – first scene the player sees."""

    def __init__(self, has_active_game: bool = False):
        super().__init__()
        if has_active_game:
            self.options = ["Continuar", "Nueva Partida", "Opciones", "Salir"]
        else:
            self.options = ["Jugar", "Opciones", "Salir"]
        self.selected = 0
        self._has_active_game = has_active_game

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            # Si hay partida activa debajo en el stack, ESC funciona como Continuar
            if self._has_active_game:
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
        draw_main_menu(screen, self.options, self.selected)

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def _select_option(self):
        option = self.options[self.selected]

        if option == "Jugar" or option == "Nueva Partida":
            from scenes.level1_scene import Level1Scene
            director = self.director
            if self._has_active_game:
                director.pop()
                director.replace(Level1Scene())
            else:
                director.replace(Level1Scene())

        elif option == "Continuar":
            # Level1Scene sigue vivo en el stack — solo hacemos pop de este menú
            director = self.director
            director.pop()

        elif option == "Opciones":
            from scenes.settings_scene import SettingsScene
            self.director.push(SettingsScene())

        elif option == "Salir":
            pygame.event.post(pygame.event.Event(pygame.QUIT))