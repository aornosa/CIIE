import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

DIALOG_BOX_HEIGHT = 250
DIALOG_BOX_MARGIN = 20
DIALOG_BOX_Y_OFFSET = 150
PORTRAIT_SIZE     = 180
PORTRAIT_MARGIN   = 20
TEXT_MARGIN       = 20
OPTION_PADDING    = 10
COLOR_DIALOG_BG          = (20,  20,  30,  230)
COLOR_DIALOG_BORDER      = (200, 200, 220)
COLOR_TEXT               = (255, 255, 255)
COLOR_SPEAKER_NAME       = (255, 220, 100)
COLOR_OPTION_NORMAL      = (180, 180, 200)
COLOR_OPTION_SELECTED    = (255, 255, 100)
COLOR_OPTION_BG          = (40,  40,  60)
COLOR_OPTION_SELECTED_BG = (80,  80,  100)

# Caché de retratos indexada por ruta
_portrait_cache: dict = {}

def _get_portrait(path):
    if path in _portrait_cache:
        return _portrait_cache[path]
    try:
        surf = pygame.image.load(path).convert_alpha()
        _portrait_cache[path] = pygame.transform.smoothscale(surf, (PORTRAIT_SIZE, PORTRAIT_SIZE))
    except (pygame.error, FileNotFoundError):
        _portrait_cache[path] = None
    return _portrait_cache[path]


def draw_dialog_ui(screen, dialog_manager):
    if not dialog_manager.is_dialog_active:
        return
    current_node = dialog_manager.get_current_node()
    if not current_node:
        return

    box_y = SCREEN_HEIGHT - DIALOG_BOX_HEIGHT - DIALOG_BOX_MARGIN - DIALOG_BOX_Y_OFFSET

    cached = dialog_manager.get_cached_surface()
    if cached:
        screen.blit(cached, (DIALOG_BOX_MARGIN, box_y))
        return

    box_width = SCREEN_WIDTH - DIALOG_BOX_MARGIN * 2
    surf      = pygame.Surface((box_width, DIALOG_BOX_HEIGHT), pygame.SRCALPHA)
    surf.fill(COLOR_DIALOG_BG)
    pygame.draw.rect(surf, COLOR_DIALOG_BORDER, (0, 0, box_width, DIALOG_BOX_HEIGHT), 3)

    portrait_rect = pygame.Rect(PORTRAIT_MARGIN, PORTRAIT_MARGIN, PORTRAIT_SIZE, PORTRAIT_SIZE)
    pygame.draw.rect(surf, (60, 60, 80),         portrait_rect)
    pygame.draw.rect(surf, COLOR_DIALOG_BORDER,  portrait_rect, 2)
    portrait_img = _get_portrait(current_node.portrait) if current_node.portrait else None
    if portrait_img:
        surf.blit(portrait_img, portrait_rect.topleft)
    else:
        # Placeholder si no hay imagen de retrato
        ph = pygame.font.Font(None, 24).render("Portrait", True, COLOR_TEXT)
        surf.blit(ph, ph.get_rect(center=portrait_rect.center))

    text_x     = PORTRAIT_MARGIN + PORTRAIT_SIZE + TEXT_MARGIN
    text_width = box_width - text_x - TEXT_MARGIN
    text_y     = PORTRAIT_MARGIN

    font_name   = pygame.font.Font(None, 36)
    font_dialog = pygame.font.Font(None, 28)
    font_small  = pygame.font.Font(None, 24)

    surf.blit(font_name.render(current_node.speaker, True, COLOR_SPEAKER_NAME), (text_x, text_y))
    text_y += 45

    for line in wrap_text(current_node.text, text_width, font_dialog):
        surf.blit(font_dialog.render(line, True, COLOR_TEXT), (text_x, text_y))
        text_y += 32

    if current_node.options:
        text_y += 20
        for i, (option_text, _) in enumerate(current_node.options):
            selected   = (i == dialog_manager.selected_option)
            option_rect = pygame.Rect(text_x - 5, text_y - 5, text_width - 10, 35)
            pygame.draw.rect(surf, COLOR_OPTION_SELECTED_BG if selected else COLOR_OPTION_BG,
                             option_rect, border_radius=5)
            if selected:
                pygame.draw.rect(surf, COLOR_OPTION_SELECTED, option_rect, 2, border_radius=5)
            prefix = "> " if selected else "  "
            color  = COLOR_OPTION_SELECTED if selected else COLOR_OPTION_NORMAL
            surf.blit(font_dialog.render(prefix + option_text, True, color), (text_x, text_y))
            text_y += 40
    else:
        prompt = font_small.render("Press [E] or [Enter] to continue...", True, COLOR_OPTION_NORMAL)
        surf.blit(prompt, (text_x, DIALOG_BOX_HEIGHT - 35))

    dialog_manager.set_cached_surface(surf)
    screen.blit(surf, (DIALOG_BOX_MARGIN, box_y))


def wrap_text(text: str, max_width: int, font) -> list:
    """Divide el texto en líneas que caben en max_width píxeles."""
    words, lines, current = text.split(" "), [], []
    for word in words:
        test = " ".join(current + [word])
        if font.render(test, True, COLOR_TEXT).get_width() <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines