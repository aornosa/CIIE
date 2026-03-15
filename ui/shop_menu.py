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
    surf = _get_portrait(_PORTRAIT_PATH)

    panel_w = _PORTRAIT_SIZE
    panel_h = _PORTRAIT_SIZE + 54
    panel_x = SCREEN_WIDTH // 2 - 360 - panel_w - 20
    panel_y = 80

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((15, 12, 25, 230))
    screen.blit(panel, (panel_x, panel_y))

    if surf:
        scaled = pygame.transform.smoothscale(surf, (_PORTRAIT_SIZE, _PORTRAIT_SIZE))
        screen.blit(scaled, (panel_x, panel_y))
    else:
        pygame.draw.rect(screen, (80, 80, 90), (panel_x, panel_y, _PORTRAIT_SIZE, _PORTRAIT_SIZE))

    pygame.draw.rect(screen, (180, 160, 255), (panel_x, panel_y, panel_w, _PORTRAIT_SIZE), 2)

    VENDOR_FONT.bold = True
    name_surf = VENDOR_FONT.render("AUDReS-01", True, (200, 185, 255))
    VENDOR_FONT.bold = False
    screen.blit(name_surf, (panel_x + panel_w // 2 - name_surf.get_width() // 2,
                             panel_y + _PORTRAIT_SIZE + 6))


def _get_current_value_label(item, player):
    if player is None:
        return ""
    t = item["type"]
    if t == "stat":
        val = player.get_stat(item["stat"])
        try:    return f"Actual: {int(val)}"
        except: return f"Actual: {val}"
    if t == "weapon":
        weapon = player.inventory.get_weapon(player.inventory.active_weapon_slot)
        if weapon is not None:
            val = getattr(weapon, item["attr"], None)
            if val is None:
                return "Sin atributo"
            try:
                return f"Actual: {val:.2f}" if isinstance(val, float) else f"Actual: {int(val)}"
            except: return f"Actual: {val}"
        return "Sin arma"
    if t == "heal":
        return f"HP: {int(player.health)} / {int(player.get_stat('max_health'))}"
    return ""


def draw_shop_menu(screen, catalog, selected_index, player_coins, message="", player=None, owned_items=None):
    owned_items = owned_items or set()

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    _draw_vendor_portrait(screen)

    TITLE_FONT.bold = True
    title_surface = TITLE_FONT.render("TIENDA", True, (255, 255, 255))
    screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 80))

    COIN_FONT.bold = True
    coin_surface = COIN_FONT.render(f"Monedas: {player_coins}", True, (255, 215, 0))
    screen.blit(coin_surface, (SCREEN_WIDTH // 2 - coin_surface.get_width() // 2, 150))

    start_y = 230
    row_h   = 92
    gap_x   = 24

    portrait_right = (SCREEN_WIDTH // 2 - 360 - _PORTRAIT_SIZE - 20) + _PORTRAIT_SIZE
    content_left   = max(SCREEN_WIDTH // 2 - 520, portrait_right + 24)
    content_right  = SCREEN_WIDTH - 80
    card_w         = max(320, (content_right - content_left - gap_x) // 2)
    col_x          = [content_left, content_left + card_w + gap_x]

    for i, item in enumerate(catalog):
        is_selected = (i == selected_index)
        row_i       = i // 2
        col_i       = i % 2
        row_y       = start_y + row_i * row_h
        item_x      = col_x[col_i]

        # Arma única ya poseída — mostrar en gris con badge "Comprada"
        weapon_name = item["name"].split(" (")[0]
        is_owned    = item.get("unique") and weapon_name in owned_items and \
                      item.get("type") in ("buy_weapon", "dash")
        can_afford  = player_coins >= item["cost"]

        if is_selected:
            bar = pygame.Rect(item_x - 8, row_y - 6, card_w + 16, 76)
            pygame.draw.rect(screen, (255, 220, 50), bar, 2, border_radius=6)

        if is_owned:
            name_color = (90, 90, 90)
            OPTION_FONT.bold = False
            prefix = "  "
        elif is_selected:
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
        screen.blit(name_surface, (item_x, row_y))

        desc_color   = (90, 90, 90) if is_owned else ((170, 170, 170) if can_afford else (80, 80, 80))
        DESC_FONT.bold = False
        desc_surface = DESC_FONT.render(item["desc"], True, desc_color)
        screen.blit(desc_surface, (item_x, row_y + 30))

        # Badge "Comprada" para armas únicas ya poseídas
        if is_owned:
            badge = STAT_FONT.render("Comprada", True, (90, 90, 90))
            screen.blit(badge, (item_x + card_w - badge.get_width(), row_y + 32))
        else:
            cur_label = _get_current_value_label(item, player)
            if cur_label:
                badge_color = (100, 220, 255) if can_afford else (60, 100, 110)
                cur_surf = STAT_FONT.render(cur_label, True, badge_color)
                screen.blit(cur_surf, (item_x + card_w - cur_surf.get_width(), row_y + 32))

            cost_color   = (255, 215, 0) if can_afford else (150, 70, 70)
            OPTION_FONT.bold = is_selected
            cost_surface = OPTION_FONT.render(f"${item['cost']}", True, cost_color)
            screen.blit(cost_surface, (item_x + card_w - cost_surface.get_width(), row_y))

    rows     = (len(catalog) + 1) // 2
    close_y  = start_y + rows * row_h + 20
    is_close = selected_index >= len(catalog)

    OPTION_FONT.bold = is_close
    color  = (255, 220, 50) if is_close else (200, 200, 200)
    prefix = "> " if is_close else "  "
    close_surface = OPTION_FONT.render(f"{prefix}Cerrar [P]", True, color)
    content_center_x = content_left + (card_w * 2 + gap_x) // 2
    screen.blit(close_surface, (content_center_x - close_surface.get_width() // 2, close_y))

    if message:
        MSG_FONT.bold = True
        msg_color = (100, 255, 100) if "comprado" in message.lower() or "añadida" in message.lower() else (255, 100, 100)
        msg_surface = MSG_FONT.render(message, True, msg_color)
        screen.blit(msg_surface, (content_center_x - msg_surface.get_width() // 2, close_y + 70))