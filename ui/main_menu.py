import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Cache fonts at module level to avoid recreating them every frame
TITLE_FONT = pygame.font.SysFont("consolas", 72)
TITLE_FONT.bold = True
OPTION_FONT = pygame.font.SysFont("consolas", 36)


def draw_main_menu(screen, options, selected_index):
    """Draw the main menu screen."""
    # Background
    screen.fill((20, 20, 30))

    # Title
    title_surface = TITLE_FONT.render("Armengard", True, (255, 255, 255))
    title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
    screen.blit(title_surface, (title_x, 150))

    # Menu options
    option_font = OPTION_FONT
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