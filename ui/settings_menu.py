import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_settings_menu(screen, options, selected_index):
    """Draw the settings/options menu."""
    # Dark overlay (works both standalone and on top of pause)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # Title
    title_font = pygame.font.SysFont("consolas", 48)
    title_font.bold = True
    title_surface = title_font.render("Opciones", True, (255, 255, 255))
    title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
    screen.blit(title_surface, (title_x, 200))

    # Menu options
    option_font = pygame.font.SysFont("consolas", 30)
    start_y = 340

    for i, option in enumerate(options):
        if i == selected_index:
            color = (255, 220, 50)
            option_font.bold = True
            prefix = "> "
        else:
            color = (200, 200, 200)
            option_font.bold = False
            prefix = "  "

        text_surface = option_font.render(prefix + option, True, color)
        text_x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
        screen.blit(text_surface, (text_x, start_y + i * 50))
