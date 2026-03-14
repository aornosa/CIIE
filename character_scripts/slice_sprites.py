import pygame

def slice_spritesheet(sheet, cell_size, rows, cols):
    frames = []
    for ry in range(rows):
        for rx in range(cols):
            rect = pygame.Rect(rx * cell_size[0], ry * cell_size[1], *cell_size)
            frames.append(sheet.subsurface(rect))
    return frames