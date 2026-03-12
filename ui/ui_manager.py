import pygame
from weapons.ranged.ranged import Ranged
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

FONT_28 = None
FONT_22 = None
FONT_18 = None

_last_hp        = None
_flash_alpha    = 0.0
_FLASH_PEAK     = 90
_FLASH_DECAY    = 70


def _get_fonts():
    global FONT_28, FONT_22, FONT_18
    if FONT_28 is None:
        FONT_28 = pygame.font.SysFont("consolas", 28, bold=True)
        FONT_22 = pygame.font.SysFont("consolas", 22, bold=True)
        FONT_18 = pygame.font.SysFont("consolas", 18)
    return FONT_28, FONT_22, FONT_18


SLOT_COUNT  = 6
SLOT_SIZE   = 64
SLOT_GAP    = 8
TOTAL_WIDTH = SLOT_COUNT * SLOT_SIZE + (SLOT_COUNT - 1) * SLOT_GAP
BAR_X       = (SCREEN_WIDTH - TOTAL_WIDTH) // 2
BAR_Y       = SCREEN_HEIGHT - SLOT_SIZE - 20

PANEL_W = 260
PANEL_H = 70
PANEL_Y = BAR_Y


def draw_overlay(screen, player, wave_manager=None, delta_time=0.016):
    global _last_hp, _flash_alpha

    font_big, font_med, font_sml = _get_fonts()

    current_hp = player.health
    if _last_hp is not None and current_hp < _last_hp:
        _flash_alpha = _FLASH_PEAK
    _last_hp = current_hp

    _draw_hotkey_bar(screen, player, font_sml)
    _draw_health(screen, player, font_med)
    _draw_weapon(screen, player, font_big, font_med, font_sml)
    _draw_interaction_tooltip(screen, player)
    if wave_manager is not None:
        _draw_wave_hud(screen, wave_manager, player, font_big, font_med, font_sml)

    if _flash_alpha > 0:
        _draw_damage_flash(screen, delta_time)


def _draw_damage_flash(screen, delta_time):
    global _flash_alpha
    W, H = screen.get_width(), screen.get_height()
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((180, 0, 0, int(_flash_alpha)))
    screen.blit(overlay, (0, 0))
    _flash_alpha = max(0.0, _flash_alpha - _FLASH_DECAY * delta_time)


def _draw_health(screen, player, font_med):
    hp     = max(0, player.health)
    hp_max = max(1, player.get_stat("max_health"))
    ratio  = hp / hp_max
    panel_x = 20

    panel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    panel.fill((10, 10, 20, 180))
    pygame.draw.rect(panel, (80, 80, 100), (0, 0, PANEL_W, PANEL_H), 2, border_radius=6)
    screen.blit(panel, (panel_x, PANEL_Y))

    screen.blit(font_med.render("VIDA", True, (180, 180, 180)), (panel_x + 12, PANEL_Y + 8))
    val = font_med.render(f"{hp} / {hp_max}", True, (255, 255, 255))
    screen.blit(val, (panel_x + PANEL_W - val.get_width() - 12, PANEL_Y + 8))

    bar_x, bar_y, bar_w, bar_h = panel_x + 12, PANEL_Y + 42, PANEL_W - 24, 14
    color = (60, 220, 90) if ratio > 0.6 else (230, 190, 40) if ratio > 0.3 else (220, 50, 50)
    pygame.draw.rect(screen, (30, 15, 15), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    pygame.draw.rect(screen, color, (bar_x, bar_y, max(2, int(bar_w * ratio)), bar_h), border_radius=3)
    pygame.draw.rect(screen, (80, 80, 100), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)


def _draw_weapon(screen, player, font_big, font_med, font_sml):
    weapon  = player.inventory.get_weapon(player.inventory.active_weapon_slot)
    panel_x = SCREEN_WIDTH - PANEL_W - 20

    panel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    panel.fill((10, 10, 20, 180))
    pygame.draw.rect(panel, (80, 80, 100), (0, 0, PANEL_W, PANEL_H), 2, border_radius=6)
    screen.blit(panel, (panel_x, PANEL_Y))

    if weapon is None:
        screen.blit(font_med.render("Sin arma", True, (130, 130, 130)), (panel_x + 12, PANEL_Y + 22))
        return

    screen.blit(font_med.render(weapon.name, True, (180, 180, 220)), (panel_x + 12, PANEL_Y + 8))

    if isinstance(weapon, Ranged):
        clip, clip_max = weapon.current_clip, weapon.clip_size
        if weapon.is_reloading():
            screen.blit(font_big.render("RECARGANDO", True, (230, 140, 30)), (panel_x + 12, PANEL_Y + 38))
        else:
            ammo_color = (220, 50, 50) if clip / max(1, clip_max) <= 0.25 else (220, 220, 180)
            screen.blit(font_big.render(f"{clip} / {clip_max}", True, ammo_color), (panel_x + 12, PANEL_Y + 38))
            res_txt = font_sml.render(f"[{_get_reserve(weapon)}]", True, (130, 130, 110))
            screen.blit(res_txt, (panel_x + PANEL_W - res_txt.get_width() - 12, PANEL_Y + 44))
    else:
        screen.blit(font_big.render("MELEE", True, (255, 160, 40)), (panel_x + 12, PANEL_Y + 38))


def _get_reserve(weapon) -> int:
    if weapon.parent is None:
        return 0
    total = 0
    for item in weapon.parent.inventory.items:
        if hasattr(item, "ammo") and item.ammo and item.ammo.ammo_type == weapon.ammo_type:
            total += item.current_ammo if hasattr(item, "current_ammo") and item.current_ammo else item.ammo.capacity
    return total


def _draw_hotkey_bar(screen, player, font_sml):
    inventory = player.inventory
    bar_surf  = pygame.Surface((TOTAL_WIDTH + SLOT_GAP, SLOT_SIZE + SLOT_GAP), pygame.SRCALPHA)

    for i in range(SLOT_COUNT):
        slot_x        = i * (SLOT_SIZE + SLOT_GAP)
        slot_rect     = pygame.Rect(slot_x, 0, SLOT_SIZE, SLOT_SIZE)
        item          = inventory.items[i] if i < len(inventory.items) else None
        # FIX: guard para items sin atributo .type (e.g. TacticalKnife directo en inventario)
        item_type     = getattr(item, "type", None)
        is_consumable = item is not None and item_type == "consumable"

        bg_color     = (70, 65, 20, 220) if is_consumable else ((30, 30, 35, 200) if item else (20, 20, 22, 140))
        border_color = (255, 220, 50)    if is_consumable else ((60, 60, 70)       if item else (90, 90, 100))

        pygame.draw.rect(bar_surf, bg_color,     slot_rect, border_radius=6)
        pygame.draw.rect(bar_surf, border_color, slot_rect, 2, border_radius=6)

        if item is not None:
            try:
                icon = pygame.transform.scale(item.asset, (SLOT_SIZE - 14, SLOT_SIZE - 14))
                if not is_consumable:
                    icon.set_alpha(120)
                bar_surf.blit(icon, (slot_x + 7, 7))
            except Exception:
                pass

        label_color = (255, 255, 180) if is_consumable else (200, 200, 200)
        bar_surf.blit(font_sml.render(str(i + 1), True, label_color), (slot_x + 4, 2))

    screen.blit(bar_surf, (BAR_X, BAR_Y))


def _draw_interaction_tooltip(screen, player):
    from map.interactables.interaction_manager import InteractionManager
    tooltip = InteractionManager().get_tooltip_in_range(player)
    if not tooltip:
        return
    font    = pygame.font.SysFont("consolas", 28)
    padding = 12
    surface = font.render(tooltip, True, (255, 255, 180))
    bg_rect = pygame.Rect(
        screen.get_width() // 2 - surface.get_width() // 2 - padding,
        screen.get_height() - 120,
        surface.get_width() + padding * 2,
        surface.get_height() + padding
    )
    bg = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 180))
    screen.blit(bg, bg_rect.topleft)
    screen.blit(surface, (bg_rect.x + padding, bg_rect.y + padding // 2))


def _draw_wave_hud(screen, wave_manager, player, font_big, font_med, font_sml):
    info    = wave_manager.get_hud_info()
    panel_w = 260
    panel_h = 100
    panel_x = SCREEN_WIDTH - panel_w - 20
    panel_y = 20

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((10, 10, 20, 180))
    pygame.draw.rect(panel, (80, 80, 100), (0, 0, panel_w, panel_h), 2, border_radius=6)
    screen.blit(panel, (panel_x, panel_y))

    screen.blit(font_big.render(f"OLEADA  {info['wave']} / {info['total_waves']}", True, (255, 220, 50)),
                (panel_x + 12, panel_y + 8))

    enemy_color = (255, 80, 80) if info["enemies_left"] > 0 else (80, 255, 80)
    screen.blit(font_med.render(f"Enemigos: {info['enemies_left']}", True, enemy_color),
                (panel_x + 12, panel_y + 44))

    screen.blit(font_sml.render(f"Pts: {player.score}", True, (180, 255, 180)),
                (panel_x + 12, panel_y + 74))
    screen.blit(font_sml.render(f"$ {getattr(player, 'coins', 0)}", True, (255, 220, 80)),
                (panel_x + 120, panel_y + 74))
def _draw_next_wave_banner(screen, font_big, font_med, info):
    """Banner minimalista: número de oleada entrante + cuenta atrás."""
    next_wave = info['wave'] + 1
    total     = info['total_waves']
    secs      = info['rest_timer']

    line1 = font_big.render(f"OLEADA {next_wave} / {total}", True, (255, 220, 50))
    line2 = font_med.render(f"Comenzando en {secs:.1f}s", True, (200, 200, 200))

    banner_w = max(line1.get_width(), line2.get_width()) + 80
    banner_h = 96
    bx = SCREEN_WIDTH  // 2 - banner_w // 2
    by = SCREEN_HEIGHT // 2 - banner_h // 2 - 60

    banner = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
    banner.fill((10, 10, 20, 210))
    pygame.draw.rect(banner, (100, 100, 130), (0, 0, banner_w, banner_h), 2, border_radius=8)
    screen.blit(banner, (bx, by))

    screen.blit(line1, (bx + banner_w // 2 - line1.get_width() // 2, by + 12))
    screen.blit(line2, (bx + banner_w // 2 - line2.get_width() // 2, by + 56))