import pygame
from core.scene import Scene

_TITLE_COLOR   = (220, 50,  50)
_SCORE_COLOR   = (255, 220, 50)
_INFO_COLOR    = (200, 200, 200)
_OPTION_COLOR  = (180, 180, 180)
_SELECT_COLOR  = (255, 220, 50)


class GameOverScene(Scene):
    def __init__(self, score: int, wave_reached: int):
        super().__init__()
        self.score        = score
        self.wave_reached = wave_reached
        self.options      = ["Nueva Partida", "Menú Principal", "Salir"]
        self.selected     = 0

        self._font_title       = pygame.font.SysFont("consolas", 72, bold=True)
        self._font_info        = pygame.font.SysFont("consolas", 36)
        self._font_option      = pygame.font.SysFont("consolas", 30, bold=False)
        self._font_option_bold = pygame.font.SysFont("consolas", 30, bold=True)

        self._alpha = 0

    def handle_events(self, input_handler):
        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select()
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False

        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            self.selected = (self.selected - 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
            self.selected = (self.selected + 1) % len(self.options)

    def update(self, delta_time):
        if self._alpha < 255:
            self._alpha = min(255, self._alpha + int(255 * delta_time * 1.8))

    def render(self, screen):
        W  = screen.get_width()
        H  = screen.get_height()
        cx = W // 2

        screen.fill((15, 5, 5))

        title = self._font_title.render("GAME OVER", True, _TITLE_COLOR)
        screen.blit(title, (cx - title.get_width() // 2, int(H * 0.18)))

        cy = int(H * 0.38)
        wave_surf = self._font_info.render(
            f"Oleada alcanzada: {self.wave_reached}", True, _INFO_COLOR)
        screen.blit(wave_surf, (cx - wave_surf.get_width() // 2, cy))

        cy += 55
        score_surf = self._font_info.render(
            f"Puntuación final: {self.score}", True, _SCORE_COLOR)
        screen.blit(score_surf, (cx - score_surf.get_width() // 2, cy))

        cy += 80
        for i, opt in enumerate(self.options):
            color  = _SELECT_COLOR if i == self.selected else _OPTION_COLOR
            prefix = "> " if i == self.selected else "  "
            font   = self._font_option_bold if i == self.selected else self._font_option
            surf   = font.render(prefix + opt, True, color)
            screen.blit(surf, (cx - surf.get_width() // 2, cy + i * 55))

        if self._alpha < 255:
            fade = pygame.Surface((W, H))
            fade.fill((0, 0, 0))
            fade.set_alpha(255 - self._alpha)
            screen.blit(fade, (0, 0))

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def _select(self):
        option = self.options[self.selected]

        if option == "Nueva Partida":
            from scenes.level1_scene import Level1Scene
            self.director.replace(Level1Scene())

        elif option == "Menú Principal":
            from scenes.main_menu_scene import MainMenuScene
            self.director.replace(MainMenuScene(has_active_game=False))

        elif option == "Salir":
            pygame.event.post(pygame.event.Event(pygame.QUIT))