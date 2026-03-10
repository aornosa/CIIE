import pygame
from core.scene import Scene
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

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
        self.options      = ["Volver al Menú"]
        self.selected     = 0

        self._font_title  = pygame.font.SysFont("consolas", 72, bold=True)
        self._font_info   = pygame.font.SysFont("consolas", 36)
        self._font_option = pygame.font.SysFont("consolas", 30)

    def handle_events(self, input_handler):
        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select()
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False

    def update(self, delta_time):
        pass

    def render(self, screen):
        screen.fill((15, 5, 5))

        cy = 180
        title = self._font_title.render("GAME OVER", True, _TITLE_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, cy))

        cy += 120
        wave_surf = self._font_info.render(
            f"Oleada alcanzada: {self.wave_reached}", True, _INFO_COLOR)
        screen.blit(wave_surf, (SCREEN_WIDTH // 2 - wave_surf.get_width() // 2, cy))

        cy += 55
        score_surf = self._font_info.render(
            f"Puntuación final: {self.score}", True, _SCORE_COLOR)
        screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, cy))

        cy += 100
        for i, opt in enumerate(self.options):
            color = _SELECT_COLOR if i == self.selected else _OPTION_COLOR
            prefix = "> " if i == self.selected else "  "
            surf = self._font_option.render(prefix + opt, True, color)
            screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, cy + i * 55))

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def _select(self):
        from scenes.main_menu_scene import MainMenuScene
        self.director.replace(MainMenuScene())