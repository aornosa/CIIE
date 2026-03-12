"""
scenes/victory_scene.py
------------------------
Pantalla de victoria. Igual que GameOverScene pero en verde dorado.
"""
import pygame
from core.scene import Scene

_BG_COLOR    = (5, 15, 5)
_TITLE_COLOR = (255, 220, 50)
_STAT_COLOR  = (200, 200, 200)
_OPT_COLOR   = (180, 180, 180)
_SEL_COLOR   = (255, 220, 50)

_STAT_LABELS = {
    "kills": "Bajas",
    "coins": "Monedas",
    "score": "Puntuación",
    "wave":  "Oleada alcanzada",
}


class VictoryScene(Scene):
    """
    Parámetros
    ----------
    stats : dict
        Cualquier combinación de: kills, coins, score, wave.
    """

    def __init__(self, stats: dict | None = None):
        super().__init__()
        self.stats    = stats or {}
        self.options  = ["Nueva Partida", "Menú Principal", "Salir"]
        self.selected = 0
        self._alpha   = 0

        self._font_title = None
        self._font_stat  = None
        self._font_opt   = None
        self._font_opt_b = None

    def _ensure_fonts(self):
        if self._font_title is None:
            self._font_title = pygame.font.SysFont("consolas", 72, bold=True)
            self._font_stat  = pygame.font.SysFont("consolas", 34)
            self._font_opt   = pygame.font.SysFont("consolas", 30)
            self._font_opt_b = pygame.font.SysFont("consolas", 30, bold=True)

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False

        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            self.selected = (self.selected - 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
            self.selected = (self.selected + 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select()

    def update(self, delta_time):
        if self._alpha < 255:
            self._alpha = min(255, self._alpha + int(255 * delta_time * 1.8))

    def render(self, screen):
        self._ensure_fonts()
        W, H = screen.get_width(), screen.get_height()
        cx   = W // 2
        screen.fill(_BG_COLOR)

        title = self._font_title.render("¡VICTORIA!", True, _TITLE_COLOR)
        screen.blit(title, (cx - title.get_width() // 2, int(H * 0.18)))

        cy = int(H * 0.38)
        for key in ("wave", "score", "kills", "coins"):
            if key not in self.stats:
                continue
            line = self._font_stat.render(
                f"{_STAT_LABELS[key]}:  {self.stats[key]}", True, _STAT_COLOR)
            screen.blit(line, (cx - line.get_width() // 2, cy))
            cy += 52

        cy += 28
        for i, opt in enumerate(self.options):
            color  = _SEL_COLOR if i == self.selected else _OPT_COLOR
            prefix = "> " if i == self.selected else "  "
            font   = self._font_opt_b if i == self.selected else self._font_opt
            surf   = font.render(prefix + opt, True, color)
            screen.blit(surf, (cx - surf.get_width() // 2, cy + i * 52))

        if self._alpha < 255:
            fade = pygame.Surface((W, H))
            fade.fill((0, 0, 0))
            fade.set_alpha(255 - self._alpha)
            screen.blit(fade, (0, 0))

    def _select(self):
        opt = self.options[self.selected]
        if opt == "Nueva Partida":
            from scenes.level1_scene import Level1Scene
            self.director.replace(Level1Scene())
        elif opt == "Menú Principal":
            from scenes.main_menu_scene import MainMenuScene
            self.director.replace(MainMenuScene(has_active_game=False))
        elif opt == "Salir":
            pygame.event.post(pygame.event.Event(pygame.QUIT))