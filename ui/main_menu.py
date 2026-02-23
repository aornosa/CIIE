import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_main_menu(screen, options, selected_index):
    """Draw the main menu screen."""
    # Background
    screen.fill((20, 20, 30))

    # Title
    title_font = pygame.font.SysFont("consolas", 72)
    title_font.bold = True
    title_surface = title_font.render("Armengard", True, (255, 255, 255))
    title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
    screen.blit(title_surface, (title_x, 150))

    # Menu options
    option_font = pygame.font.SysFont("consolas", 36)
    start_y = 350

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
        screen.blit(text_surface, (text_x, start_y + i * 60))
