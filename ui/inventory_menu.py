import pygame

# Layout consumibles
ITEM_SLOT_ORIGIN = (100, 680)
ITEM_SLOT_SIZE   = 96
ITEM_SLOT_GAP    = 110
ITEM_COLS        = 8

# Layout armas del inventario
WEAPON_INV_ORIGIN = (100, 530)
WEAPON_INV_SIZE   = 96
WEAPON_INV_GAP    = 130
WEAPON_INV_MAX    = 3

# Colores
COLOR_SLOT_BG          = (50,  50,  50)
COLOR_SLOT_HOVER_BG    = (80,  75,  40)
COLOR_SLOT_SELECTED_BG = (80,  70,  20)
COLOR_SLOT_BORDER      = (70,  70,  80)
COLOR_HOVER_BORDER     = (255, 220, 50)
COLOR_SELECTED_BORDER  = (255, 220, 50)
COLOR_EMPTY_SLOT       = (30,  30,  35)
COLOR_CONSUMABLE_HINT  = (180, 255, 120)
COLOR_WEAPON_BADGE     = (80,  140, 255)
COLOR_WEAPON_BORDER    = (80,  140, 255)
COLOR_TOOLTIP_BG       = (15,  15,  25, 210)
COLOR_TOOLTIP_TEXT     = (255, 255, 200)

_FONTS: dict = {}


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = pygame.font.SysFont("consolas", size, bold=bold)
    return _FONTS[key]


def get_item_slot_rect(index: int) -> pygame.Rect:
    # Solo cuenta consumibles — index es posición en la lista filtrada
    col = index % ITEM_COLS
    row = index // ITEM_COLS
    x   = ITEM_SLOT_ORIGIN[0] + col * ITEM_SLOT_GAP
    y   = ITEM_SLOT_ORIGIN[1] + row * ITEM_SLOT_GAP
    return pygame.Rect(x, y, ITEM_SLOT_SIZE, ITEM_SLOT_SIZE)


def get_weapon_inv_slot_rect(index: int) -> pygame.Rect:
    x = WEAPON_INV_ORIGIN[0] + index * WEAPON_INV_GAP
    y = WEAPON_INV_ORIGIN[1]
    return pygame.Rect(x, y, WEAPON_INV_SIZE, WEAPON_INV_SIZE)


def _consumables(inventory) -> list:
    return [item for item in inventory.items
            if getattr(item, "type", None) != "weapon_item"]


def _weapons_in_inv(inventory) -> list:
    return [item for item in inventory.items
            if getattr(item, "type", None) == "weapon_item"]


def get_clicked_item_index(mouse_pos, inventory) -> int:
    consumable_items = _consumables(inventory)
    for i, item in enumerate(consumable_items):
        if get_item_slot_rect(i).collidepoint(mouse_pos):
            return inventory.items.index(item)
    return -1


def _get_hovered_consumable_index(mouse_pos, inventory) -> int:
    consumable_items = _consumables(inventory)
    for i in range(len(consumable_items)):
        if get_item_slot_rect(i).collidepoint(mouse_pos):
            return i
    return -1


def _get_hovered_weapon_inv_index(mouse_pos, inventory) -> int:
    weapons = _weapons_in_inv(inventory)
    for i in range(len(weapons)):
        if get_weapon_inv_slot_rect(i).collidepoint(mouse_pos):
            return i
    return -1


def draw_item_box(screen, item, position, selected=False, hovered=False):
    rect   = pygame.Rect(position[0], position[1], ITEM_SLOT_SIZE, ITEM_SLOT_SIZE)
    is_wpn = getattr(item, "type", None) == "weapon_item"

    if hovered and item:    bg = COLOR_SLOT_HOVER_BG
    elif selected:          bg = COLOR_SLOT_SELECTED_BG
    elif item:              bg = COLOR_SLOT_BG
    else:                   bg = COLOR_EMPTY_SLOT

    pygame.draw.rect(screen, bg, rect, border_radius=5)

    if is_wpn:              border_color, border_w = COLOR_WEAPON_BORDER, 3
    elif hovered and item:  border_color, border_w = COLOR_HOVER_BORDER, 3
    elif selected:          border_color, border_w = COLOR_SELECTED_BORDER, 3
    else:                   border_color, border_w = COLOR_SLOT_BORDER, 1

    pygame.draw.rect(screen, border_color, rect, border_w, border_radius=5)

    if item:
        icon = pygame.transform.scale(item.asset, (ITEM_SLOT_SIZE - 16, ITEM_SLOT_SIZE - 16))
        screen.blit(icon, (position[0] + 8, position[1] + 8))
        if is_wpn:
            screen.blit(_font(11, bold=True).render("ARMA", True, COLOR_WEAPON_BADGE),
                        (position[0] + 4, position[1] + ITEM_SLOT_SIZE - 16))
        elif item.type == "consumable":
            screen.blit(_font(11).render("USAR", True, COLOR_CONSUMABLE_HINT),
                        (position[0] + 4, position[1] + ITEM_SLOT_SIZE - 16))


def _draw_weapon_inv_section(screen, inventory, mouse_pos, pending_weapon_item):
    weapons = _weapons_in_inv(inventory)
    hovered_idx = _get_hovered_weapon_inv_index(mouse_pos, inventory)

    label = _font(18, bold=True).render("ARMAS EN MOCHILA", True, (140, 160, 200))
    screen.blit(label, (WEAPON_INV_ORIGIN[0], WEAPON_INV_ORIGIN[1] - 24))

    for i in range(WEAPON_INV_MAX):
        item    = weapons[i] if i < len(weapons) else None
        rect    = get_weapon_inv_slot_rect(i)
        hovered = (i == hovered_idx) and item is not None
        draw_item_box(screen, item, rect.topleft, hovered=hovered)
        if item:
            name = _font(13).render(item.name, True, (200, 200, 200))
            screen.blit(name, (rect.x + rect.w // 2 - name.get_width() // 2,
                                rect.y + rect.h + 4))


def _draw_tooltip(screen, item, slot_rect: pygame.Rect):
    lines = [
        (item.name,        _font(22, bold=True), COLOR_TOOLTIP_TEXT),
        (item.description, _font(18),            (200, 200, 200)),
    ]
    if getattr(item, "type", None) == "weapon_item":
        lines.append(("Clic izq → elegir slot", _font(16), (160, 220, 255)))

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


def draw_slot_assign_overlay(screen, weapon_item) -> None:
    sw, sh = screen.get_size()
    bw, bh = 500, 220
    bx     = sw // 2 - bw // 2
    by     = sh // 2 - bh // 2

    panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
    panel.fill((20, 20, 35, 235))
    pygame.draw.rect(panel, (80, 140, 255), (0, 0, bw, bh), 2, border_radius=10)
    screen.blit(panel, (bx, by))

    title = _font(22, bold=True).render(f"Equipar: {weapon_item.name}", True, (255, 255, 255))
    screen.blit(title, (bx + bw // 2 - title.get_width() // 2, by + 16))

    subtitle = _font(17).render("¿En qué ranura?", True, (160, 160, 210))
    screen.blit(subtitle, (bx + bw // 2 - subtitle.get_width() // 2, by + 46))

    options = [
        ("[1]  Primario",   (60, 140, 60),  (90, 200, 90)),
        ("[2]  Secundario", (60, 80,  160), (90, 120, 220)),
        ("[ESC] Cancelar",  (110, 40, 40),  (170, 60, 60)),
    ]
    btn_w, btn_h = 360, 36
    gap          = 8
    btn_x        = bx + bw // 2 - btn_w // 2
    btn_y_start  = by + 82

    for i, (label, base_col, _) in enumerate(options):
        ry = btn_y_start + i * (btn_h + gap)
        r  = pygame.Rect(btn_x, ry, btn_w, btn_h)
        pygame.draw.rect(screen, base_col, r, border_radius=6)
        pygame.draw.rect(screen, (130, 130, 180), r, 1, border_radius=6)
        txt = _font(18, bold=True).render(label, True, (255, 255, 255))
        screen.blit(txt, (btn_x + btn_w // 2 - txt.get_width() // 2,
                          ry + btn_h // 2 - txt.get_height() // 2))

    note = _font(14).render("Arma anterior → inventario (o suelo si está lleno)", True, (160, 140, 90))
    screen.blit(note, (bx + bw // 2 - note.get_width() // 2, by + bh - 22))


def get_overlay_rects() -> dict:
    return {}


def _draw_controls_hint(screen: pygame.Surface):
    grid_right = ITEM_SLOT_ORIGIN[0] + ITEM_COLS * ITEM_SLOT_GAP + 10
    box_x      = grid_right
    box_y      = ITEM_SLOT_ORIGIN[1]
    box_w      = 260
    box_h      = 80
    pad        = 12

    box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box.fill((20, 20, 30, 200))
    screen.blit(box, (box_x, box_y))
    pygame.draw.rect(screen, (70, 70, 90), (box_x, box_y, box_w, box_h), 1, border_radius=4)

    lines = [("LMB", "  usar objeto"), ("RMB", "  soltar al suelo")]
    for i, (key, desc) in enumerate(lines):
        y         = box_y + pad + i * 26
        key_surf  = _font(17, bold=True).render(key, True, (255, 220, 50))
        desc_surf = _font(17).render(desc, True, (180, 180, 180))
        screen.blit(key_surf,  (box_x + pad, y))
        screen.blit(desc_surf, (box_x + pad + key_surf.get_width(), y))


def draw_inventory_screen(screen: pygame.Surface, player, mouse_pos,
                           pending_weapon_item=None):
    """Dibuja el inventario. Si pending_weapon_item no es None muestra el overlay de asignación de slot."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    title = _font(42, bold=True).render("INVENTARIO", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 30))

    draw_weapon_box(screen, player.inventory.primary_weapon,   (100, 100))
    draw_weapon_box(screen, player.inventory.secondary_weapon, (700, 100))
    draw_player_status(screen, player, (1300, 100))

    # Sección de armas en mochila
    _draw_weapon_inv_section(screen, player.inventory, mouse_pos, pending_weapon_item)

    # Sección de consumibles
    consumable_items = _consumables(player.inventory)
    hovered_c_idx    = _get_hovered_consumable_index(mouse_pos, player.inventory)
    tooltip_item     = None
    tooltip_rect     = None

    label = _font(18, bold=True).render("CONSUMIBLES", True, (140, 200, 140))
    screen.blit(label, (ITEM_SLOT_ORIGIN[0], ITEM_SLOT_ORIGIN[1] - 24))

    for i, item in enumerate(consumable_items):
        selected = (player.inventory.items.index(item) == player.inventory.selected_item_index)
        hovered  = (i == hovered_c_idx)
        rect     = get_item_slot_rect(i)
        draw_item_box(screen, item, rect.topleft, selected=selected, hovered=hovered)
        screen.blit(_font(14).render(str(i + 1), True, (160, 160, 160)), (rect.x + 4, rect.y + 2))
        if hovered:
            tooltip_item = item
            tooltip_rect = rect

    # Slots vacíos restantes
    for i in range(len(consumable_items), 16):
        draw_item_box(screen, None, get_item_slot_rect(i).topleft)

    if tooltip_item and tooltip_rect and pending_weapon_item is None:
        _draw_tooltip(screen, tooltip_item, tooltip_rect)

    _draw_controls_hint(screen)

    if pending_weapon_item is not None:
        draw_slot_assign_overlay(screen, pending_weapon_item)