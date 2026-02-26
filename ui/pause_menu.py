import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_pause_menu(screen, options, selected_index):
    """Draw the pause menu overlay on top of the frozen game."""
    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    # Title
    title_font = pygame.font.SysFont("consolas", 52)
    title_font.bold = True
    title_surface = title_font.render("PAUSA", True, (255, 255, 255))
    title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
    screen.blit(title_surface, (title_x, 250))

    # Menu options
    option_font = pygame.font.SysFont("consolas", 32)
    start_y = 380

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
        screen.blit(text_surface, (text_x, start_y + i * 55))
