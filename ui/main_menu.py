import pygame

BUILD_VERSION = "0.1.0"

_TITLE_FONT       = None
_OPTION_FONT      = None
_OPTION_FONT_BOLD = None
_VERSION_FONT     = None

def _fonts():
    global _TITLE_FONT, _OPTION_FONT, _OPTION_FONT_BOLD, _VERSION_FONT
    if _TITLE_FONT is None:
        _TITLE_FONT       = pygame.font.SysFont("consolas", 72, bold=True)
        _OPTION_FONT      = pygame.font.SysFont("consolas", 36)
        _OPTION_FONT_BOLD = pygame.font.SysFont("consolas", 36, bold=True)
        _VERSION_FONT     = pygame.font.SysFont("consolas", 20)


def draw_main_menu(screen, options, selected_index):
    _fonts()
    cx     = screen.get_width() // 2
    H      = screen.get_height()
    start_y = int(H * 0.42)

    screen.fill((20, 20, 30))

    title = _TITLE_FONT.render("Armengard", True, (255, 255, 255))
    screen.blit(title, (cx - title.get_width() // 2, H // 4))

    for i, option in enumerate(options):
        selected = (i == selected_index)
        font     = _OPTION_FONT_BOLD if selected else _OPTION_FONT
        color    = (255, 220, 50) if selected else (200, 200, 200)
        prefix   = "> " if selected else "  "
        surf     = font.render(prefix + option, True, color)
        screen.blit(surf, (cx - surf.get_width() // 2, start_y + i * 60))

    ver = _VERSION_FONT.render(f"v{BUILD_VERSION}", True, (200, 200, 200))
    screen.blit(ver, (screen.get_width() - ver.get_width() - 20, H - 40))