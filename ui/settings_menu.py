import pygame

TITLE_FONT       = None
OPTION_FONT      = None
OPTION_FONT_BOLD = None
HINT_FONT        = None

_BAR_STEPS = 10   # bloques totales de la barra


def _get_fonts():
    global TITLE_FONT, OPTION_FONT, OPTION_FONT_BOLD, HINT_FONT
    if TITLE_FONT is None:
        TITLE_FONT       = pygame.font.SysFont("consolas", 48, bold=True)
        OPTION_FONT      = pygame.font.SysFont("consolas", 30, bold=False)
        OPTION_FONT_BOLD = pygame.font.SysFont("consolas", 30, bold=True)
        HINT_FONT        = pygame.font.SysFont("consolas", 20, bold=False)
    return TITLE_FONT, OPTION_FONT, OPTION_FONT_BOLD, HINT_FONT


def draw_settings_menu(screen, options, selected_index):
    """
    options: lista de dict
      {"label": str}               → entrada normal (ENTER para activar)
      {"label": str, "slider": float}  → slider de volumen (0.0-1.0, ◄/► para cambiar)
    """
    title_font, option_font, option_font_bold, hint_font = _get_fonts()

    cx = screen.get_width()  // 2
    H  = screen.get_height()

    screen.fill((20, 20, 30))

    # Título
    title_surf = title_font.render("Opciones", True, (255, 255, 255))
    screen.blit(title_surf, (cx - title_surf.get_width() // 2, int(H * 0.18)))

    start_y = int(H * 0.36)
    row_h   = 70

    for i, option in enumerate(options):
        selected   = (i == selected_index)
        label      = option["label"]
        has_slider = "slider" in option
        y          = start_y + i * row_h

        color  = (255, 220, 50)  if selected else (200, 200, 200)
        font   = option_font_bold if selected else option_font
        prefix = "> " if selected else "  "

        label_surf = font.render(prefix + label, True, color)

        if has_slider:
            value = max(0.0, min(1.0, option["slider"]))
            filled   = round(value * _BAR_STEPS)
            bar_str  = "█" * filled + "░" * (_BAR_STEPS - filled)
            pct_str  = f"{int(value * 100):3d}%"

            arrow_color = (255, 220, 50) if selected else (100, 100, 140)
            bar_color   = (255, 220, 50) if selected else (160, 160, 200)

            arrow_l  = font.render("◄", True, arrow_color)
            arrow_r  = font.render("►", True, arrow_color)
            bar_surf = font.render(bar_str,  True, bar_color)
            pct_surf = font.render(pct_str,  True, color)

            gap = 12
            total_w = (label_surf.get_width() + gap * 2 +
                       arrow_l.get_width()  + gap +
                       bar_surf.get_width() + gap +
                       arrow_r.get_width()  + gap +
                       pct_surf.get_width())
            x = cx - total_w // 2

            screen.blit(label_surf, (x, y));               x += label_surf.get_width() + gap * 2
            screen.blit(arrow_l,    (x, y));               x += arrow_l.get_width()    + gap
            screen.blit(bar_surf,   (x, y));               x += bar_surf.get_width()   + gap
            screen.blit(arrow_r,    (x, y));               x += arrow_r.get_width()    + gap
            screen.blit(pct_surf,   (x, y))
        else:
            screen.blit(label_surf, (cx - label_surf.get_width() // 2, y))

    # Pista de controles al pie
    hint = hint_font.render("◄ ►  ajustar volumen       ↑ ↓  navegar       ESC  volver", True, (100, 100, 120))
    screen.blit(hint, (cx - hint.get_width() // 2, int(H * 0.88)))
