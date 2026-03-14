import pygame

_TITLE_FONT       = None
_OPTION_FONT      = None
_OPTION_FONT_BOLD = None
_HINT_FONT        = None
_BAR_STEPS = 10

def _fonts():
    global _TITLE_FONT, _OPTION_FONT, _OPTION_FONT_BOLD, _HINT_FONT
    if _TITLE_FONT is None:
        _TITLE_FONT       = pygame.font.SysFont("consolas", 48, bold=True)
        _OPTION_FONT      = pygame.font.SysFont("consolas", 30)
        _OPTION_FONT_BOLD = pygame.font.SysFont("consolas", 30, bold=True)
        _HINT_FONT        = pygame.font.SysFont("consolas", 20)


def draw_settings_menu(screen, options, selected_index):
    _fonts()
    cx      = screen.get_width() // 2
    H       = screen.get_height()
    start_y = int(H * 0.36)
    row_h   = 70

    screen.fill((20, 20, 30))

    title = _TITLE_FONT.render("Opciones", True, (255, 255, 255))
    screen.blit(title, (cx - title.get_width() // 2, int(H * 0.18)))

    for i, option in enumerate(options):
        selected   = (i == selected_index)
        y          = start_y + i * row_h
        font       = _OPTION_FONT_BOLD if selected else _OPTION_FONT
        color      = (255, 220, 50) if selected else (200, 200, 200)
        prefix     = "> " if selected else "  "
        label_surf = font.render(prefix + option["label"], True, color)

        if "slider" in option:
            _draw_slider_row(screen, font, label_surf, option["slider"], color, selected, cx, y)
        else:
            screen.blit(label_surf, (cx - label_surf.get_width() // 2, y))

    hint = _HINT_FONT.render(
        "◄ ►  ajustar volumen       ↑ ↓  navegar       ESC  volver",
        True, (100, 100, 120))
    screen.blit(hint, (cx - hint.get_width() // 2, int(H * 0.88)))


def _draw_slider_row(screen, font, label_surf, value, color, selected, cx, y):
    """Dibuja una fila de slider: label ◄ ████░░ ► pct%"""
    value = max(0.0, min(1.0, value))
    filled   = round(value * _BAR_STEPS)
    bar_str  = "█" * filled + "░" * (_BAR_STEPS - filled)

    arrow_color = (255, 220, 50) if selected else (100, 100, 140)
    bar_color   = (255, 220, 50) if selected else (160, 160, 200)

    arrow_l  = font.render("◄",               True, arrow_color)
    arrow_r  = font.render("►",               True, arrow_color)
    bar_surf = font.render(bar_str,            True, bar_color)
    pct_surf = font.render(f"{int(value * 100):3d}%", True, color)

    gap     = 12
    total_w = (label_surf.get_width() + gap * 2
               + arrow_l.get_width()  + gap
               + bar_surf.get_width() + gap
               + arrow_r.get_width()  + gap
               + pct_surf.get_width())

    x = cx - total_w // 2
    for surf, extra_gap in [
        (label_surf, gap * 2),
        (arrow_l,    gap),
        (bar_surf,   gap),
        (arrow_r,    gap),
        (pct_surf,   0),
    ]:
        screen.blit(surf, (x, y))
        x += surf.get_width() + extra_gap