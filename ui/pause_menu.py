import pygame

TITLE_FONT        = None
OPTION_FONT       = None
OPTION_FONT_BOLD  = None


def _get_fonts():
    global TITLE_FONT, OPTION_FONT, OPTION_FONT_BOLD
    if TITLE_FONT is None:
        TITLE_FONT       = pygame.font.SysFont("consolas", 52, bold=True)
        OPTION_FONT      = pygame.font.SysFont("consolas", 32, bold=False)
        OPTION_FONT_BOLD = pygame.font.SysFont("consolas", 32, bold=True)
    return TITLE_FONT, OPTION_FONT, OPTION_FONT_BOLD


def draw_pause_menu(screen, options, selected_index):
    title_font, option_font, option_font_bold = _get_fonts()

    cx = screen.get_width()  // 2
    H  = screen.get_height()

    screen.fill((20, 20, 30))

    title_surface = title_font.render("PAUSA", True, (255, 255, 255))
    screen.blit(title_surface, (cx - title_surface.get_width() // 2, int(H * 0.30)))

    start_y = int(H * 0.45)
    for i, option in enumerate(options):
        if i == selected_index:
            color  = (255, 220, 50)
            font   = option_font_bold
            prefix = "> "
        else:
            color  = (200, 200, 200)
            font   = option_font
            prefix = "  "

        text_surface = font.render(prefix + option, True, color)
        screen.blit(text_surface, (cx - text_surface.get_width() // 2, start_y + i * 55))