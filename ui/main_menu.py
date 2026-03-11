import pygame

TITLE_FONT        = None
OPTION_FONT       = None
OPTION_FONT_BOLD  = None
VERSION_FONT      = None

# ── Cambiar este número para verificar la build ──
BUILD_VERSION = "0.1.0"


def _get_fonts():
    global TITLE_FONT, OPTION_FONT, OPTION_FONT_BOLD, VERSION_FONT
    if TITLE_FONT is None:
        TITLE_FONT       = pygame.font.SysFont("consolas", 72, bold=True)
        OPTION_FONT      = pygame.font.SysFont("consolas", 36, bold=False)
        OPTION_FONT_BOLD = pygame.font.SysFont("consolas", 36, bold=True)
        VERSION_FONT     = pygame.font.SysFont("consolas", 20)
    return TITLE_FONT, OPTION_FONT, OPTION_FONT_BOLD


def draw_main_menu(screen, options, selected_index):
    title_font, option_font, option_font_bold = _get_fonts()

    cx = screen.get_width()  // 2
    H  = screen.get_height()

    screen.fill((20, 20, 30))

    title_surface = title_font.render("Armengard", True, (255, 255, 255))
    screen.blit(title_surface, (cx - title_surface.get_width() // 2, H // 4))

    start_y = int(H * 0.42)
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
        screen.blit(text_surface, (cx - text_surface.get_width() // 2, start_y + i * 60))

    # Version number — bottom right corner
    ver_surface = VERSION_FONT.render(f"v{BUILD_VERSION}", True, (200, 200, 200))
    screen.blit(ver_surface, (screen.get_width() - ver_surface.get_width() - 20, H - 40))
