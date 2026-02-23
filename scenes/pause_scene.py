import pygame
from core.scene import Scene
from ui.pause_menu import draw_pause_menu


class PauseScene(Scene):
    """Pause menu – stacked on top of GameScene."""

    def __init__(self, game_scene):
        super().__init__()
        self.game_scene = game_scene  # Keep reference to render frozen game beneath
        self.options = ["Reanudar", "Opciones", "Salir al Menu"]
        self.selected = 0

    def handle_events(self, input_handler):
        # ESC to resume
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
        pass  # Game is frozen – nothing updates

    def render(self, screen):
        # Draw the frozen game underneath
        self.game_scene.render(screen)
        # Draw pause menu overlay on top
        draw_pause_menu(screen, self.options, self.selected)

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def on_exit(self):
        pygame.mouse.set_visible(False)

    # -- Option handlers --------------------------------------------------

    def _select_option(self):
        option = self.options[self.selected]

        if option == "Reanudar":
            self.director.pop()

        elif option == "Opciones":
            from scenes.settings_scene import SettingsScene
            self.director.push(SettingsScene())

        elif option == "Salir al Menu":
            from scenes.main_menu_scene import MainMenuScene
            # Save reference before pop clears self.director
            director = self.director
            director.pop()
            director.replace(MainMenuScene())
