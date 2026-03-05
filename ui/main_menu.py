import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

TITLE_FONT = pygame.font.SysFont("consolas", 72)
TITLE_FONT.bold = True
OPTION_FONT = pygame.font.SysFont("consolas", 36)


def draw_main_menu(screen, options, selected_index):
    screen.fill((20, 20, 30))

    title_surface = TITLE_FONT.render("Armengard", True, (255, 255, 255))
    screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 150))

    start_y = 350
    for i, option in enumerate(options):
        if i == selected_index:
            color = (255, 220, 50)
            OPTION_FONT.bold = True
            prefix = "> "
        else:
            color = (200, 200, 200)
            OPTION_FONT.bold = False
            prefix = "  "

        text_surface = OPTION_FONT.render(prefix + option, True, color)
        screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, start_y + i * 60))
