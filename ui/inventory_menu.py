"""
ui/inventory_menu.py
---------------------
Menú de inventario con hover highlight, tooltips y gestión de interacciones.
Todas las fonts se inicializan lazy para evitar crash si pygame no está listo.
"""
import pygame

# ── Layout (debe coincidir con inventory.py click_drop_item) ──────────────────
ITEM_SLOT_ORIGIN = (100, 550)
ITEM_SLOT_SIZE   = 96        # 96×96 como en click_drop_item del repo
ITEM_SLOT_GAP    = 110       # espaciado entre slots
ITEM_COLS        = 6

# ── Colores ───────────────────────────────────────────────────────────────────
COLOR_SLOT_BG          = (50,  50,  50)
COLOR_SLOT_HOVER_BG    = (80,  75,  40)
COLOR_SLOT_SELECTED_BG = (80,  70,  20)
COLOR_SLOT_BORDER      = (70,  70,  80)
COLOR_HOVER_BORDER     = (255, 220, 50)
COLOR_SELECTED_BORDER  = (255, 220, 50)
COLOR_EMPTY_SLOT       = (30,  30,  35)
COLOR_CONSUMABLE_HINT  = (180, 255, 120)
COLOR_DROP_HINT        = (255, 130, 100)
COLOR_TOOLTIP_BG       = (15,  15,  25, 210)
COLOR_TOOLTIP_TEXT     = (255, 255, 200)

_FONTS: dict = {}


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = pygame.font.SysFont("consolas", size, bold=bold)
    return _FONTS[key]


# ── Geometría de slots ────────────────────────────────────────────────────────

def get_item_slot_rect(index: int) -> pygame.Rect:
    col = index % ITEM_COLS
    row = index // ITEM_COLS
    x = ITEM_SLOT_ORIGIN[0] + col * ITEM_SLOT_GAP
    y = ITEM_SLOT_ORIGIN[1] + row * ITEM_SLOT_GAP
    return pygame.Rect(x, y, ITEM_SLOT_SIZE, ITEM_SLOT_SIZE)


def get_clicked_item_index(mouse_pos, inventory) -> int:
    for i in range(len(inventory.items)):
        if get_item_slot_rect(i).collidepoint(mouse_pos):
            return i
    return -1


def _get_hovered_index(mouse_pos, inventory) -> int:
    for i in range(inventory.max_size):
        if get_item_slot_rect(i).collidepoint(mouse_pos):
            return i
    return -1


# ── Dibujado de un slot ───────────────────────────────────────────────────────

def draw_item_box(screen, item, position, selected=False, hovered=False):
    rect = pygame.Rect(position[0], position[1], ITEM_SLOT_SIZE, ITEM_SLOT_SIZE)

    if hovered and item:
        bg = COLOR_SLOT_HOVER_BG
    elif selected:
        bg = COLOR_SLOT_SELECTED_BG
    elif item:
        bg = COLOR_SLOT_BG
    else:
        bg = COLOR_EMPTY_SLOT

    pygame.draw.rect(screen, bg, rect, border_radius=5)

    if hovered and item:
        border_color, border_w = COLOR_HOVER_BORDER, 3
    elif selected:
        border_color, border_w = COLOR_SELECTED_BORDER, 3
    else:
        border_color, border_w = COLOR_SLOT_BORDER, 1

    pygame.draw.rect(screen, border_color, rect, border_w, border_radius=5)

    if item:
        icon = pygame.transform.scale(item.asset, (ITEM_SLOT_SIZE - 16, ITEM_SLOT_SIZE - 16))
        screen.blit(icon, (position[0] + 8, position[1] + 8))

        # Número de slot (esquina sup-izq)
        screen.blit(_font(12).render(str(0), True, (160, 160, 160)),
                    (position[0] + 4, position[1] + 2))

        if item.type == "consumable":
            screen.blit(_font(11).render("USAR", True, COLOR_CONSUMABLE_HINT),
                        (position[0] + 4, position[1] + ITEM_SLOT_SIZE - 16))


# ── Tooltip flotante ──────────────────────────────────────────────────────────

def _draw_tooltip(screen, item, slot_rect: pygame.Rect):
    lines = [
        (item.name,        _font(22, bold=True), COLOR_TOOLTIP_TEXT),
        (item.description, _font(18),            (200, 200, 200)),
    ]


    padding = 10
    surfs = [f.render(t, True, col) for t, f, col in lines]
    w = max(s.get_width() for s in surfs) + padding * 2
    h = sum(s.get_height() + 4 for s in surfs) + padding * 2

    tx = slot_rect.x
    ty = slot_rect.y - h - 8
    if tx + w > screen.get_width():
        tx = screen.get_width() - w - 4
    if ty < 4:
        ty = slot_rect.bottom + 8

    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill(COLOR_TOOLTIP_BG)
    pygame.draw.rect(bg, (100, 100, 130), (0, 0, w, h), 1, border_radius=4)
    screen.blit(bg, (tx, ty))

    cy = ty + padding
    for surf in surfs:
        screen.blit(surf, (tx + padding, cy))
        cy += surf.get_height() + 4


# ── Weapon box ────────────────────────────────────────────────────────────────

def draw_weapon_box(screen, weapon, position):
    box_w, box_h = 550, 400
    pygame.draw.rect(screen, (40, 40, 50), (*position, box_w, box_h), border_radius=8)
    pygame.draw.rect(screen, (70, 70, 90), (*position, box_w, box_h), 2, border_radius=8)
    if weapon:
        screen.blit(_font(28, bold=True).render(weapon.name, True, (255, 255, 255)),
                    (position[0] + 30, position[1] + 40))
        screen.blit(_font(22).render(f"Daño: {weapon.damage}", True, (200, 200, 200)),
                    (position[0] + 40, position[1] + 78))
        icon = pygame.transform.scale(weapon.asset, (180, 180))
        screen.blit(icon, (position[0] + 185, position[1] + 130))
    else:
        screen.blit(_font(22).render("{ Sin arma }", True, (140, 140, 140)),
                    (position[0] + 180, position[1] + 185))


# ── Player status ─────────────────────────────────────────────────────────────

def draw_player_status(screen, player, position):
    pygame.draw.rect(screen, (30, 30, 30), (*position, 300, 400), border_radius=8)
    pygame.draw.rect(screen, (70, 70, 90), (*position, 300, 400), 2, border_radius=8)

    hp     = player.health
    hp_max = player.get_stat("max_health")
    screen.blit(_font(26).render(f"Vida: {hp}/{hp_max}", True, (255, 80, 80)),
                (position[0] + 20, position[1] + 20))
    screen.blit(_font(26).render(f"Vel: {player.get_stat('speed')}", True, (80, 255, 80)),
                (position[0] + 20, position[1] + 55))

    from item.consumable import _get_addiction
    addiction = _get_addiction(player)
    if addiction > 0:
        screen.blit(_font(20).render(f"Adicción: {addiction}", True, (255, 120, 0)),
                    (position[0] + 20, position[1] + 90))


# ── Pantalla completa ─────────────────────────────────────────────────────────

def draw_inventory_screen(screen: pygame.Surface, player, mouse_pos):
    """
    Dibuja el inventario completo.
    Llamar desde level1_scene.render() cuando _inventory_open es True.
    mouse_pos puede ser pygame.Vector2 o tuple.
    """
    # Fondo semitransparente
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    # Título
    title = _font(42, bold=True).render("INVENTARIO", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 30))


    # Paneles de armas y status
    draw_weapon_box(screen, player.inventory.primary_weapon,   (100, 100))
    draw_weapon_box(screen, player.inventory.secondary_weapon, (700, 100))
    draw_player_status(screen, player, (1300, 100))

    # Slots de items
    hovered_idx   = _get_hovered_index(mouse_pos, player.inventory)
    tooltip_item  = None
    tooltip_rect  = None

    for i in range(player.inventory.max_size):
        item     = player.inventory.items[i] if i < len(player.inventory.items) else None
        selected = (i == player.inventory.selected_item_index)
        hovered  = (i == hovered_idx) and item is not None
        rect     = get_item_slot_rect(i)

        draw_item_box(screen, item, rect.topleft, selected=selected, hovered=hovered)

        # Número de slot encima del slot (1-based)
        screen.blit(_font(14).render(str(i + 1), True, (160, 160, 160)),
                    (rect.x + 4, rect.y + 2))

        if hovered:
            tooltip_item = item
            tooltip_rect = rect

    # Tooltip al final (encima de todo lo demás)
    if tooltip_item and tooltip_rect:
        _draw_tooltip(screen, tooltip_item, tooltip_rect)