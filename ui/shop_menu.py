import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

TITLE_FONT  = pygame.font.SysFont("consolas", 52)
COIN_FONT   = pygame.font.SysFont("consolas", 36)
OPTION_FONT = pygame.font.SysFont("consolas", 28)
DESC_FONT   = pygame.font.SysFont("consolas", 22)
MSG_FONT    = pygame.font.SysFont("consolas", 28)


def draw_shop_menu(screen, catalog, selected_index, player_coins, message=""):
    # ── Semi-transparent overlay over the frozen game frame ──
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # ── Title ──
    TITLE_FONT.bold = True
    title_surface = TITLE_FONT.render("TIENDA", True, (255, 255, 255))
    screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 80))

    # ── Coins ──
    COIN_FONT.bold = True
    coin_surface = COIN_FONT.render(f"Monedas: {player_coins}", True, (255, 215, 0))
    screen.blit(coin_surface, (SCREEN_WIDTH // 2 - coin_surface.get_width() // 2, 150))

    # ── Catalog items ──
    start_y = 240
    spacing = 75

    for i, item in enumerate(catalog):
        is_selected = (i == selected_index)
        can_afford = player_coins >= item["cost"]

        row_y = start_y + i * spacing

        # Highlight bar for selected item
        if is_selected:
            bar = pygame.Rect(SCREEN_WIDTH // 2 - 360, row_y - 6, 720, 66)
            pygame.draw.rect(screen, (255, 220, 50), bar, 2, border_radius=6)

        # Name
        if is_selected:
            name_color = (255, 220, 50)
            prefix = "> "
            OPTION_FONT.bold = True
        elif not can_afford:
            name_color = (100, 100, 100)
            prefix = "  "
            OPTION_FONT.bold = False
        else:
            name_color = (220, 220, 220)
            prefix = "  "
            OPTION_FONT.bold = False

        name_surface = OPTION_FONT.render(f"{prefix}{item['name']}", True, name_color)
        screen.blit(name_surface, (SCREEN_WIDTH // 2 - 340, row_y))

        # Description
        desc_color = (170, 170, 170) if can_afford else (80, 80, 80)
        DESC_FONT.bold = False
        desc_surface = DESC_FONT.render(item["desc"], True, desc_color)
        screen.blit(desc_surface, (SCREEN_WIDTH // 2 - 340, row_y + 30))

        # Cost (right-aligned)
        cost_color = (255, 215, 0) if can_afford else (150, 70, 70)
        OPTION_FONT.bold = is_selected
        cost_surface = OPTION_FONT.render(f"${item['cost']}", True, cost_color)
        screen.blit(cost_surface, (SCREEN_WIDTH // 2 + 320 - cost_surface.get_width(), row_y))

    # ── "Cerrar" option ──
    close_y = start_y + len(catalog) * spacing + 20
    is_close = selected_index >= len(catalog)

    if is_close:
        color = (255, 220, 50)
        prefix = "> "
        OPTION_FONT.bold = True
    else:
        color = (200, 200, 200)
        prefix = "  "
        OPTION_FONT.bold = False

    close_surface = OPTION_FONT.render(f"{prefix}Cerrar [P]", True, color)
    screen.blit(close_surface, (SCREEN_WIDTH // 2 - close_surface.get_width() // 2, close_y))

    # ── Feedback message ──
    if message:
        MSG_FONT.bold = True
        if "comprado" in message.lower():
            msg_color = (100, 255, 100)
        else:
            msg_color = (255, 100, 100)
        msg_surface = MSG_FONT.render(message, True, msg_color)
        screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, close_y + 70))
