import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

SLOT_COUNT   = 6
SLOT_SIZE    = 64
SLOT_GAP     = 8
BORDER       = 2
TOTAL_WIDTH  = SLOT_COUNT * SLOT_SIZE + (SLOT_COUNT - 1) * SLOT_GAP
BAR_X        = (SCREEN_WIDTH - TOTAL_WIDTH) // 2
BAR_Y        = SCREEN_HEIGHT - SLOT_SIZE - 20   
C_BG          = (30,  30,  35,  200)  
C_BG_EMPTY    = (20,  20,  22,  140)
C_BORDER      = (90,  90, 100)
C_CONSUMABLE  = (255, 220,  50)       
C_NON_USABLE  = (60,   60,  70)        
C_LABEL       = (200, 200, 200)
C_LABEL_USABLE= (255, 255, 180)
C_ACTIVE_BG   = (70,  65,  20,  220)  
_font_label = None
_font_count = None

def _get_fonts():
    global _font_label, _font_count
    if _font_label is None:
        _font_label = pygame.font.SysFont("consolas", 18, bold=True)
        _font_count = pygame.font.SysFont("consolas", 14)
    return _font_label, _font_count


def draw_hotkey_bar(screen, player):
    font_label, font_count = _get_fonts()
    inventory = player.inventory

    # Superficie con alpha para el fondo
    bar_surf = pygame.Surface(
        (TOTAL_WIDTH + SLOT_GAP, SLOT_SIZE + SLOT_GAP),
        pygame.SRCALPHA
    )

    for i in range(SLOT_COUNT):
        slot_x = i * (SLOT_SIZE + SLOT_GAP)
        slot_rect = pygame.Rect(slot_x, 0, SLOT_SIZE, SLOT_SIZE)

        item = inventory.items[i] if i < len(inventory.items) else None
        is_consumable = item is not None and item.type == "consumable"

        bg_color = C_ACTIVE_BG if is_consumable else (C_BG if item else C_BG_EMPTY)
        pygame.draw.rect(bar_surf, bg_color, slot_rect, border_radius=6)

        border_color = C_CONSUMABLE if is_consumable else (C_NON_USABLE if item else C_BORDER)
        pygame.draw.rect(bar_surf, border_color, slot_rect, BORDER, border_radius=6)

        if item is not None:
            icon = pygame.transform.scale(item.asset, (SLOT_SIZE - 14, SLOT_SIZE - 14))
            if not is_consumable:
                icon.set_alpha(120)
            bar_surf.blit(icon, (slot_x + 7, 7))

        label_color = C_LABEL_USABLE if is_consumable else C_LABEL
        label = font_label.render(str(i + 1), True, label_color)
        bar_surf.blit(label, (slot_x + 4, 2))

    screen.blit(bar_surf, (BAR_X, BAR_Y))
