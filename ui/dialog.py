import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

# UI Constants
DIALOG_BOX_HEIGHT = 250
DIALOG_BOX_MARGIN = 20
DIALOG_BOX_Y_OFFSET = 150
PORTRAIT_SIZE = 180
PORTRAIT_MARGIN = 20
TEXT_MARGIN = 20
OPTION_PADDING = 10

# Colors
COLOR_DIALOG_BG = (20, 20, 30, 230)
COLOR_DIALOG_BORDER = (200, 200, 220)
COLOR_TEXT = (255, 255, 255)
COLOR_SPEAKER_NAME = (255, 220, 100)
COLOR_OPTION_NORMAL = (180, 180, 200)
COLOR_OPTION_SELECTED = (255, 255, 100)
COLOR_OPTION_BG = (40, 40, 60)
COLOR_OPTION_SELECTED_BG = (80, 80, 100)

def draw_dialog_ui(screen, dialog_manager):
    if not dialog_manager.is_dialog_active:
        return
    
    current_node = dialog_manager.get_current_node()
    if not current_node:
        return
    
    box_y = SCREEN_HEIGHT - DIALOG_BOX_HEIGHT - DIALOG_BOX_MARGIN - DIALOG_BOX_Y_OFFSET
    box_width = SCREEN_WIDTH - (DIALOG_BOX_MARGIN * 2)
    
    dialog_surface = pygame.Surface((box_width, DIALOG_BOX_HEIGHT), pygame.SRCALPHA)
    dialog_surface.fill(COLOR_DIALOG_BG)
    
    pygame.draw.rect(dialog_surface, COLOR_DIALOG_BORDER, 
                    (0, 0, box_width, DIALOG_BOX_HEIGHT), 3)
    
    # Portrait placeholder
    portrait_x = PORTRAIT_MARGIN
    portrait_y = PORTRAIT_MARGIN
    portrait_rect = pygame.Rect(portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE)
    pygame.draw.rect(dialog_surface, (60, 60, 80), portrait_rect)
    pygame.draw.rect(dialog_surface, COLOR_DIALOG_BORDER, portrait_rect, 2)
    
    font_small = pygame.font.Font(None, 24)
    portrait_text = font_small.render("Portrait", True, COLOR_TEXT)
    portrait_text_rect = portrait_text.get_rect(center=portrait_rect.center)
    dialog_surface.blit(portrait_text, portrait_text_rect)
    
    # Text area
    text_x = portrait_x + PORTRAIT_SIZE + TEXT_MARGIN
    text_y = PORTRAIT_MARGIN
    text_width = box_width - text_x - TEXT_MARGIN
    
    font_name = pygame.font.Font(None, 36)
    speaker_text = font_name.render(current_node.speaker, True, COLOR_SPEAKER_NAME)
    dialog_surface.blit(speaker_text, (text_x, text_y))
    
    font_dialog = pygame.font.Font(None, 28)
    text_y += 45
    wrapped_lines = wrap_text(current_node.text, text_width, font_dialog)
    
    for line in wrapped_lines:
        line_surface = font_dialog.render(line, True, COLOR_TEXT)
        dialog_surface.blit(line_surface, (text_x, text_y))
        text_y += 32
    
    # Options or continue prompt
    if current_node.options:
        text_y += 20
        for i, (option_text, _) in enumerate(current_node.options):
            is_selected = (i == dialog_manager.selected_option)
            
            option_bg_color = COLOR_OPTION_SELECTED_BG if is_selected else COLOR_OPTION_BG
            option_rect = pygame.Rect(text_x - 5, text_y - 5, 
                                     text_width - 10, 35)
            pygame.draw.rect(dialog_surface, option_bg_color, option_rect, border_radius=5)
            
            if is_selected:
                pygame.draw.rect(dialog_surface, COLOR_OPTION_SELECTED, option_rect, 2, border_radius=5)
            
            option_color = COLOR_OPTION_SELECTED if is_selected else COLOR_OPTION_NORMAL
            prefix = "> " if is_selected else "  "
            option_surface = font_dialog.render(prefix + option_text, True, option_color)
            dialog_surface.blit(option_surface, (text_x, text_y))
            
            text_y += 40
    else:
        text_y = DIALOG_BOX_HEIGHT - 35
        font_small = pygame.font.Font(None, 24)
        prompt = font_small.render("Press [E] or [Enter] to continue...", True, COLOR_OPTION_NORMAL)
        dialog_surface.blit(prompt, (text_x, text_y))
    
    screen.blit(dialog_surface, (DIALOG_BOX_MARGIN, box_y))


def wrap_text(text, max_width, font):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, COLOR_TEXT)
        
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def draw_dialogue_box(screen, text, position, size):
    pass

def format_dialogue_text(text, max_width, font):
    pass
