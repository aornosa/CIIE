import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.dialog import _get_portrait

TITLE_FONT   = pygame.font.SysFont("consolas", 52)
COIN_FONT    = pygame.font.SysFont("consolas", 36)
OPTION_FONT  = pygame.font.SysFont("consolas", 28)
DESC_FONT    = pygame.font.SysFont("consolas", 22)
MSG_FONT     = pygame.font.SysFont("consolas", 28)
VENDOR_FONT  = pygame.font.SysFont("consolas", 22)
STAT_FONT    = pygame.font.SysFont("consolas", 20)

_PORTRAIT_PATH = "assets/characters/audres/portrait_shop.jpg"
_PORTRAIT_SIZE = 220


def _draw_vendor_portrait(screen):
    """Draw Audrey's portrait panel to the left of the shop content area."""
    surf = _get_portrait(_PORTRAIT_PATH)

    panel_w = _PORTRAIT_SIZE
    panel_h = _PORTRAIT_SIZE + 54

    # Place the panel to the left of the centered content block,
    # vertically aligned with the title (y ≈ 80)
    panel_x = SCREEN_WIDTH // 2 - 360 - panel_w - 20
    panel_y = 80

    # Dark backing panel
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((15, 12, 25, 230))
    screen.blit(panel, (panel_x, panel_y))

    # Portrait image (or grey placeholder)
    if surf:
        scaled = pygame.transform.smoothscale(surf, (_PORTRAIT_SIZE, _PORTRAIT_SIZE))
        screen.blit(scaled, (panel_x, panel_y))
    else:
        pygame.draw.rect(screen, (80, 80, 90), (panel_x, panel_y, _PORTRAIT_SIZE, _PORTRAIT_SIZE))

    # Border around portrait
    pygame.draw.rect(screen, (180, 160, 255), (panel_x, panel_y, panel_w, _PORTRAIT_SIZE), 2)

    # Name label
    VENDOR_FONT.bold = True
    name_surf = VENDOR_FONT.render("AUDReS-01", True, (200, 185, 255))
    VENDOR_FONT.bold = False
    nx = panel_x + panel_w // 2 - name_surf.get_width() // 2
    ny = panel_y + _PORTRAIT_SIZE + 6
    screen.blit(name_surf, (nx, ny))


def _get_current_value_label(item, player):
    """Return a short string showing the player's current value for this upgrade."""
    if player is None:
        return ""
    if item["type"] == "stat":
        val = player.get_stat(item["stat"])
        return f"Actual: {int(val)}"
    if item["type"] == "weapon":
        weapon = player.inventory.get_weapon(player.inventory.active_weapon_slot)
        if weapon is not None:
            val = getattr(weapon, item["attr"], "—")
            return f"Actual: {int(val)}"
        return "Sin arma"
    if item["type"] == "heal":
        return f"HP: {int(player.health)} / {int(player.get_stat('max_health'))}"
    return ""


def draw_shop_menu(screen, catalog, selected_index, player_coins, message="", player=None):
    # ── Semi-transparent overlay over the frozen game frame ──
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # ── Vendor portrait (Audrey, top-left) ───────────────────
    _draw_vendor_portrait(screen)

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

        # Current-value badge (right side of description row)
        cur_label = _get_current_value_label(item, player)
        if cur_label:
            badge_color = (100, 220, 255) if can_afford else (60, 100, 110)
            cur_surf = STAT_FONT.render(cur_label, True, badge_color)
            screen.blit(cur_surf, (SCREEN_WIDTH // 2 + 320 - cur_surf.get_width(), row_y + 32))

        # Cost (right-aligned, top of row)
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
