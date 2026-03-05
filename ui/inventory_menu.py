import pygame

FONT_30 = pygame.font.SysFont("consolas", 30, bold=True)
FONT_25 = pygame.font.SysFont("consolas", 25, bold=True)
FONT_12 = pygame.font.SysFont("consolas", 12, bold=True)
FONT_28 = pygame.font.SysFont("consolas", 28)
COLOR_SELECTED_BORDER = (255, 220, 50)
COLOR_SELECTED_BG     = (80, 70, 20)
ITEM_SLOT_ORIGIN = (100, 550)
ITEM_SLOT_SIZE   = 100
ITEM_SLOT_GAP    = 110
ITEM_COLS        = 6

def get_item_slot_rect(index: int) -> pygame.Rect:
    col = index % ITEM_COLS
    row = index // ITEM_COLS
    x = ITEM_SLOT_ORIGIN[0] + col * ITEM_SLOT_GAP
    y = ITEM_SLOT_ORIGIN[1] + row * ITEM_SLOT_GAP
    return pygame.Rect(x, y, ITEM_SLOT_SIZE, ITEM_SLOT_SIZE)


def get_clicked_item_index(mouse_pos, inventory) -> int:
    for i in range(len(inventory.items)):
        rect = get_item_slot_rect(i)
        if rect.collidepoint(mouse_pos):
            return i
    return -1

def draw_weapon_box(screen, weapon, position):
    box_size = (550, 400)
    draw_box(screen, position, box_size, (50, 50, 50))
    if weapon:
        screen.blit(weapon.asset, (position[0] + 100, position[1] + 150))
        text_surface = FONT_30.render(weapon.name, True, (255, 255, 255))
        screen.blit(text_surface, (position[0] + 30, position[1] + 40))
        damage_text = f"Damage: {weapon.damage}"
        text_surface = FONT_25.render(damage_text, True, (200, 200, 200))
        screen.blit(text_surface, (position[0] + 40, position[1] + 80))
    else:
        font = pygame.font.SysFont("consolas", 25)
        text_surface = font.render("{ No Weapon }", True, (200, 200, 200))
        screen.blit(text_surface, (position[0] + 190, position[1] + 195))


def draw_item_box(screen, item, position, selected=False):
    bg_color = COLOR_SELECTED_BG if selected else (50, 50, 50)
    draw_box(screen, position, (100, 100), bg_color)

    # Borde resaltado si está seleccionado
    if selected:
        pygame.draw.rect(screen, COLOR_SELECTED_BORDER,
                         (position[0], position[1], 100, 100), 3)

    if item:
        scaled = pygame.transform.scale(item.asset, (60, 60))
        screen.blit(scaled, (position[0] + 20, position[1] + 20))
        text_surface = FONT_12.render(item.name, True, (255, 255, 255))
        screen.blit(text_surface, (position[0] + 5, position[1] + 2))

        # Indicador de consumible
        if item.type == "consumable":
            hint = FONT_12.render("[F] usar", True, COLOR_SELECTED_BORDER)
            screen.blit(hint, (position[0] + 5, position[1] + 82))


def draw_player_status(screen, player, position):
    draw_box(screen, (position[0], position[1]), (300, 400), (30, 30, 30))
    font = pygame.font.SysFont("consolas", 28)

    health_text = f"Health: {player.health}/{player.get_stat('max_health')}"
    speed_text  = f"Speed:  {player.get_stat('speed')}"

    # Mostrar adicción si existe
    from item.consumable import _get_addiction
    addiction = _get_addiction(player)
    addiction_text = f"Adicción Fénix: {addiction}" if addiction > 0 else ""

    screen.blit(font.render(health_text,   True, (255, 80,  80)),  (position[0]+20, position[1]+20))
    screen.blit(font.render(speed_text,    True, (80,  255, 80)),  (position[0]+20, position[1]+55))
    if addiction_text:
        font_small = pygame.font.SysFont("consolas", 22)
        screen.blit(font_small.render(addiction_text, True, (255, 120, 0)), (position[0]+20, position[1]+90))


def draw_box(screen, position, size, color):
    pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]))