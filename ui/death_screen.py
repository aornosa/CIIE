import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

_TITLE_FONT   = None
_STAT_FONT    = None
_OPTION_FONT  = None
_HINT_FONT    = None

_RED_DARK   = (120,  10,  10)
_RED_MID    = (200,  30,  30)
_RED_BRIGHT = (255,  60,  60)
_WHITE      = (255, 255, 255)
_GREY       = (160, 160, 160)
_YELLOW     = (255, 215,   0)


def _fonts():
    global _TITLE_FONT, _STAT_FONT, _OPTION_FONT, _HINT_FONT
    if _TITLE_FONT is None:
        _TITLE_FONT  = pygame.font.SysFont("consolas", 80, bold=True)
        _STAT_FONT   = pygame.font.SysFont("consolas", 30)
        _OPTION_FONT = pygame.font.SysFont("consolas", 34)
        _HINT_FONT   = pygame.font.SysFont("consolas", 22)


def draw_death_screen(screen, frozen_frame, stats, options, selected_index, alpha):
    """
    frozen_frame  – pygame.Surface of the last game frame (may be None)
    stats         – dict with keys: score, coins, kills
    options       – list of option strings
    selected_index – currently highlighted option
    alpha         – 0-255 fade-in progress
    """
    _fonts()

    # ── Frozen game frame darkened beneath ──────────────────
    if frozen_frame:
        darkened = frozen_frame.copy()
        veil = pygame.Surface(darkened.get_size())
        veil.set_alpha(200)
        veil.fill((0, 0, 0))
        darkened.blit(veil, (0, 0))
        screen.blit(darkened, (0, 0))
    else:
        screen.fill((10, 5, 5))

    # Apply overall fade-in via a full-screen alpha surface
    if alpha < 255:
        fade = pygame.Surface(screen.get_size())
        fade.fill((0, 0, 0))
        fade.set_alpha(255 - alpha)
        screen.blit(fade, (0, 0))

    cx = SCREEN_WIDTH // 2

    # ── "HAS MUERTO" title ──────────────────────────────────
    title = _TITLE_FONT.render("HAS MUERTO", True, _RED_BRIGHT)
    # subtle shadow
    shadow = _TITLE_FONT.render("HAS MUERTO", True, _RED_DARK)
    ty = 130
    screen.blit(shadow, (cx - shadow.get_width() // 2 + 4, ty + 4))
    screen.blit(title,  (cx - title.get_width()  // 2,     ty))

    # Decorative line under the title
    line_y = ty + title.get_height() + 12
    pygame.draw.line(screen, _RED_MID, (cx - 260, line_y), (cx + 260, line_y), 2)

    # ── Stats block ─────────────────────────────────────────
    stat_lines = [
        (f"Enemigos eliminados:  {stats.get('kills', 0)}", _WHITE),
        (f"Monedas acumuladas:   {stats.get('coins', 0)}", _YELLOW),
    ]
    sy = line_y + 28
    for text, color in stat_lines:
        surf = _STAT_FONT.render(text, True, color)
        screen.blit(surf, (cx - surf.get_width() // 2, sy))
        sy += 38

    # ── Options ─────────────────────────────────────────────
    oy = sy + 40
    for i, opt in enumerate(options):
        selected = (i == selected_index)
        _OPTION_FONT.bold = selected
        color  = _YELLOW if selected else _GREY
        prefix = "> " if selected else "  "
        surf = _OPTION_FONT.render(prefix + opt, True, color)
        screen.blit(surf, (cx - surf.get_width() // 2, oy + i * 58))

    # ── Hint ────────────────────────────────────────────────
    hint = _HINT_FONT.render("↑↓ para navegar   ENTER para confirmar", True, (90, 90, 90))
    screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 40))
