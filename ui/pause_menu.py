import pygame

_TITLE_FONT       = None
_OPTION_FONT      = None
_OPTION_FONT_BOLD = None

def _fonts():
    global _TITLE_FONT, _OPTION_FONT, _OPTION_FONT_BOLD
    if _TITLE_FONT is None:
        _TITLE_FONT       = pygame.font.SysFont("consolas", 52, bold=True)
        _OPTION_FONT      = pygame.font.SysFont("consolas", 32)
        _OPTION_FONT_BOLD = pygame.font.SysFont("consolas", 32, bold=True)

def draw_pause_menu(screen, options, selected_index):
    _fonts()
    cx      = screen.get_width() // 2
    H       = screen.get_height()
    start_y = int(H * 0.45)

    screen.fill((20, 20, 30))

    title = _TITLE_FONT.render("PAUSA", True, (255, 255, 255))
    screen.blit(title, (cx - title.get_width() // 2, int(H * 0.30)))

    for i, option in enumerate(options):
        selected = (i == selected_index)
        font     = _OPTION_FONT_BOLD if selected else _OPTION_FONT
        color    = (255, 220, 50) if selected else (200, 200, 200)
        prefix   = "> " if selected else "  "
        surf     = font.render(prefix + option, True, color)
        screen.blit(surf, (cx - surf.get_width() // 2, start_y + i * 55))