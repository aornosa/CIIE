import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

STYLE = {
    "title_color":      (255, 255, 255),
    "title_size":       48,
    "tab_active_color": (255, 220,  50),
    "tab_idle_color":   (160, 160, 160),
    "tab_size":         26,
    "tab_y":            280,
    "tab_gap":          40,
    "key_color":        (255, 220,  50),
    "key_size":         26,
    "desc_color":       (210, 210, 210),
    "desc_size":        26,
    "row_start_y":      360,
    "row_gap":          52,
    "key_col_x":        0.25,
    "desc_col_x":       0.48,
    "hint_color":       (100, 100, 100),
    "hint_size":        20,
    "separator_color":  (60,  60,  60),
    "box_color":        (30,  30,  40,  220),
    "box_padding":      40,
}

_font_cache: dict[tuple, pygame.font.Font] = {}


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        f = pygame.font.SysFont("consolas", size)
        f.bold = bold
        _font_cache[key] = f
    return _font_cache[key]


def draw_keybindings_menu(
    screen: pygame.Surface,
    categories: list[str],
    active_page: int,
    entries: list[tuple[str, str]],
) -> None:
    s = STYLE

    screen.fill((20, 20, 30))

    title_surf = _font(s["title_size"], bold=True).render("Controles", True, s["title_color"])
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 190))

    _draw_tabs(screen, categories, active_page)

    box_x    = int(SCREEN_WIDTH * s["key_col_x"]) - s["box_padding"]
    box_y    = s["row_start_y"] - s["box_padding"] // 2
    box_w    = SCREEN_WIDTH - 2 * box_x
    box_h    = len(entries) * s["row_gap"] + s["box_padding"] * 2
    box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box_surf.fill(s["box_color"])
    screen.blit(box_surf, (box_x, box_y))

    header_y = s["row_start_y"] - 4
    _render(screen, "Tecla",   s["key_col_x"],  header_y, s["key_size"],  s["tab_idle_color"], bold=True)
    _render(screen, "Acción",  s["desc_col_x"], header_y, s["desc_size"], s["tab_idle_color"], bold=True)
    pygame.draw.line(
        screen, s["separator_color"],
        (box_x + 8,         header_y + s["key_size"] + 6),
        (box_x + box_w - 8, header_y + s["key_size"] + 6), 1
    )

    for i, (key_text, desc_text) in enumerate(entries):
        y = s["row_start_y"] + s["key_size"] + 14 + i * s["row_gap"]
        _render(screen, key_text,  s["key_col_x"],  y, s["key_size"],  s["key_color"])
        _render(screen, desc_text, s["desc_col_x"], y, s["desc_size"], s["desc_color"])

    hint_surf = _font(s["hint_size"]).render(
        "← → Cambiar categoría    Enter / Esc  Volver", True, s["hint_color"]
    )
    screen.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, SCREEN_HEIGHT - 60))


def _draw_tabs(screen: pygame.Surface, categories: list[str], active: int) -> None:
    s = STYLE
    tab_font_active = _font(s["tab_size"], bold=True)
    tab_font_idle   = _font(s["tab_size"], bold=False)

    widths = [
        tab_font_active.size(f"[ {c} ]")[0] if i == active
        else tab_font_idle.size(c)[0]
        for i, c in enumerate(categories)
    ]
    total_w = sum(widths) + s["tab_gap"] * (len(categories) - 1)
    x = SCREEN_WIDTH // 2 - total_w // 2

    for i, cat in enumerate(categories):
        if i == active:
            surf = tab_font_active.render(f"[ {cat} ]", True, s["tab_active_color"])
        else:
            surf = tab_font_idle.render(cat, True, s["tab_idle_color"])
        screen.blit(surf, (x, s["tab_y"]))
        x += widths[i] + s["tab_gap"]


def _render(
    screen: pygame.Surface,
    text: str,
    rel_x: float,
    y: int,
    size: int,
    color: tuple,
    bold: bool = False,
) -> None:
    surf = _font(size, bold).render(text, True, color)
    screen.blit(surf, (int(SCREEN_WIDTH * rel_x), y))
