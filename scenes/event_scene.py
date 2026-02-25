import pygame
from core.scene import Scene
from dialogs.dialog_manager import DialogManager
from ui.dialog import draw_dialog_ui


class EventScene(Scene):
    """Generic stacked scene for scripted events with dialog.

    The game scene passed as 'game_scene' is rendered frozen underneath.
    An independent DialogManager drives the dialog. When the dialog ends the
    scene pops itself and returns control to the game.
    """

    def __init__(self, game_scene, dialog_tree):
        super().__init__()
        self.game_scene = game_scene

        # Each EventScene owns its own DialogManager instance — no shared state
        self.dialog_manager = DialogManager()
        self.dialog_manager.start_dialog(dialog_tree)

    # ------------------------------------------------------------------

    def handle_events(self, input_handler):
        self.dialog_manager.input_handler = input_handler
        self.dialog_manager.handle_input(
            input_handler.get_keys_pressed(),
            input_handler.get_keys_just_pressed(),
        )

    def update(self, delta_time):
        # Pop back to the game as soon as the dialog finishes
        if not self.dialog_manager.is_dialog_active:
            self.director.pop()

    def render(self, screen):
        # Draw the frozen game world underneath
        self.game_scene.render(screen)

        # Dim overlay so the dialog box stands out
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Dialog UI on top
        draw_dialog_ui(screen, self.dialog_manager)

    def on_enter(self):
        pygame.mouse.set_visible(False)

    def on_exit(self):
        pygame.mouse.set_visible(False)
