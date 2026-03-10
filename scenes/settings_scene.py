import pygame
from core.scene import Scene
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

_TITLE_FONT  = None
_OPTION_FONT = None


def _get_fonts():
    global _TITLE_FONT, _OPTION_FONT
    if _TITLE_FONT is None:
        _TITLE_FONT  = pygame.font.SysFont("consolas", 48, bold=True)
        _OPTION_FONT = pygame.font.SysFont("consolas", 30)
    return _TITLE_FONT, _OPTION_FONT


def draw_settings_menu(screen, options, selected_index):
    title_font, option_font = _get_fonts()

    screen.fill((20, 20, 30))

    cx = SCREEN_WIDTH // 2

    title_surface = title_font.render("Opciones", True, (255, 255, 255))
    screen.blit(title_surface, (cx - title_surface.get_width() // 2, 200))

    start_y = 340
    for i, option in enumerate(options):
        if i == selected_index:
            color = (255, 220, 50)
            option_font.bold = True
            prefix = "> "
        else:
            color = (200, 200, 200)
            option_font.bold = False
            prefix = "  "

        text_surface = option_font.render(prefix + option, True, color)
        screen.blit(text_surface, (cx - text_surface.get_width() // 2, start_y + i * 50))


class SettingsScene(Scene):
    """Settings / options menu – can be reached from MainMenu or PauseMenu."""

    def __init__(self):
        super().__init__()
        self.options = ["Controles", "Audio (placeholder)", "Video (placeholder)", "Volver"]
        self.selected = 0

    def handle_events(self, input_handler):
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

    def _select_option(self):
        option = self.options[self.selected]

        if option == "Controles":
            from scenes.keybindings_scene import KeybindingsScene
            self.director.push(KeybindingsScene())

        elif option == "Volver":
            self.director.pop()