import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

_font_big   = None
_font_med   = None
_font_small = None


def _get_fonts():
    global _font_big, _font_med, _font_small
    if _font_big is None:
        _font_big   = pygame.font.SysFont("consolas", 28, bold=True)  # bajado de 36
        _font_med   = pygame.font.SysFont("consolas", 22, bold=True)  # bajado de 26
        _font_small = pygame.font.SysFont("consolas", 18)             # bajado de 20
    return _font_big, _font_med, _font_small


def draw_wave_hud(screen: pygame.Surface, wave_manager, player):
    font_big, font_med, font_small = _get_fonts()
    info = wave_manager.get_hud_info()

    panel_w, panel_h = 260, 100
    panel_x = SCREEN_WIDTH - panel_w - 20
    panel_y = 20

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((10, 10, 20, 180))
    pygame.draw.rect(panel, (80, 80, 100), (0, 0, panel_w, panel_h), 2, border_radius=6)
    screen.blit(panel, (panel_x, panel_y))

    wave_text = f"OLEADA  {info['wave']} / {info['total_waves']}"
    wave_surf = font_big.render(wave_text, True, (255, 220, 50))
    screen.blit(wave_surf, (panel_x + 12, panel_y + 8))

    enemy_color = (255, 80, 80) if info["enemies_left"] > 0 else (80, 255, 80)
    enemy_text = f"Enemigos: {info['enemies_left']}"
    enemy_surf = font_med.render(enemy_text, True, enemy_color)
    screen.blit(enemy_surf, (panel_x + 12, panel_y + 44))

    score_text = f"Pts: {player.score}"
    score_surf = font_small.render(score_text, True, (180, 255, 180))
    screen.blit(score_surf, (panel_x + 12, panel_y + 74))

    if info["state"] == "resting":
        _draw_rest_banner(screen, font_big, font_med, info)


def _draw_rest_banner(screen, font_big, font_med, info):
    timer = info["rest_timer"]
    next_wave = info["wave"] + 1
    total = info["total_waves"]

    lines = [
        (f"OLEADA {info['wave']} COMPLETADA!", (255, 220, 50), font_big),
        (f"Proxima oleada: {next_wave}/{total}", (200, 200, 200), font_med),
        (f"Comenzando en {timer:.1f}s...", (255, 100, 100), font_med),
    ]

    line_h = 40
    total_h = len(lines) * line_h + 30
    banner_w = 620
    bx = SCREEN_WIDTH // 2 - banner_w // 2
    by = SCREEN_HEIGHT // 2 - total_h // 2 - 40

    banner = pygame.Surface((banner_w, total_h), pygame.SRCALPHA)
    banner.fill((10, 10, 20, 200))
    pygame.draw.rect(banner, (100, 100, 130), (0, 0, banner_w, total_h), 2, border_radius=8)
    screen.blit(banner, (bx, by))

    for i, (text, color, font) in enumerate(lines):
        surf = font.render(text, True, color)
        screen.blit(surf, (bx + banner_w // 2 - surf.get_width() // 2, by + 15 + i * line_h))