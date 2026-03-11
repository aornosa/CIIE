"""
Pantalla de nivel completado — reutilizable para todos los niveles.
"""
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

_TITLE_FONT  = None
_STAT_FONT   = None
_OPTION_FONT = None
_HINT_FONT   = None

_GREEN_DARK   = (10,  80,  30)
_GREEN_MID    = (30, 160,  60)
_GREEN_BRIGHT = (80, 230, 100)
_WHITE        = (255, 255, 255)
_GREY         = (160, 160, 160)
_YELLOW       = (255, 215,   0)
_GOLD         = (255, 200,  50)


def _fonts():
    global _TITLE_FONT, _STAT_FONT, _OPTION_FONT, _HINT_FONT
    if _TITLE_FONT is None:
        _TITLE_FONT  = pygame.font.SysFont("consolas", 68, bold=True)
        _STAT_FONT   = pygame.font.SysFont("consolas", 30)
        _OPTION_FONT = pygame.font.SysFont("consolas", 34)
        _HINT_FONT   = pygame.font.SysFont("consolas", 22)


def draw_level_complete_screen(
    screen, frozen_frame, level_name, stats, options, selected_index, alpha
):
    """
    screen          – pygame.Surface to draw onto
    frozen_frame    – last rendered Surface of the level (may be None)
    level_name      – e.g. "Nivel 1"
    stats           – dict with keys: kills, coins
    options         – list of option strings
    selected_index  – currently highlighted option index
    alpha           – 0-255 fade-in progress
    """
    _fonts()

    # ── Darkened frozen game frame beneath ──────────────────
    if frozen_frame:
        darkened = frozen_frame.copy()
        veil = pygame.Surface(darkened.get_size())
        veil.set_alpha(180)
        veil.fill((0, 0, 0))
        darkened.blit(veil, (0, 0))
        screen.blit(darkened, (0, 0))
    else:
        screen.fill((5, 15, 10))

    # ── Full-screen fade-in ──────────────────────────────────
    if alpha < 255:
        fade = pygame.Surface(screen.get_size())
        fade.fill((0, 0, 0))
        fade.set_alpha(255 - alpha)
        screen.blit(fade, (0, 0))

    cx = SCREEN_WIDTH // 2

    # ── Title: "NIVEL X COMPLETADO" ─────────────────────────
    title_text = f"{level_name.upper()} COMPLETADO"
    title  = _TITLE_FONT.render(title_text, True, _GREEN_BRIGHT)
    shadow = _TITLE_FONT.render(title_text, True, _GREEN_DARK)
    ty = 120
    screen.blit(shadow, (cx - shadow.get_width() // 2 + 4, ty + 4))
    screen.blit(title,  (cx - title.get_width()  // 2,     ty))

    # Decorative line
    line_y = ty + title.get_height() + 12
    pygame.draw.line(screen, _GREEN_MID, (cx - 280, line_y), (cx + 280, line_y), 2)

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
    oy = sy + 50
    for i, opt in enumerate(options):
        is_sel = (i == selected_index)
        color  = _GOLD if is_sel else _GREY
        prefix = "> " if is_sel else "  "
        surf = _OPTION_FONT.render(prefix + opt, True, color)
        screen.blit(surf, (cx - surf.get_width() // 2, oy))
        oy += 50

    # ── Hint at the bottom ──────────────────────────────────
    hint = _HINT_FONT.render("↑↓ seleccionar   ENTER confirmar", True, _GREY)
    screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 50))
