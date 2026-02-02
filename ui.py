import pygame
from settings import *

def draw_overlay(screen, player):
    # draw_health_bar(screen, (SCREEN_WIDTH-420, 20), player.health, player.get_stat("max_health"))
    draw_score(screen, player.score, (SCREEN_WIDTH-60, SCREEN_HEIGHT-100))
    # draw_minimap(screen, screen.player.position, screen.entities, (10, 10),
    draw_effect_icons(screen, player.effects, (10, SCREEN_HEIGHT - 50))
    if 0: # Change for toggleable
        draw_inventory(screen, screen.player.inventory, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))

def draw_health_bar(screen, position, health, max_health):
    bar_width = 400
    bar_height = 35
    health_bar_rect = pygame.Rect(position[0], position[1], bar_width * health/max_health, bar_height)
    border_rect = pygame.Rect(position[0], position[1], bar_width, bar_height)
    pygame.draw.rect(screen, (255, 0, 0), health_bar_rect)
    pygame.draw.rect(screen, (255, 255, 255), border_rect, 2)

def draw_score(screen, score, position):
    pass

def draw_minimap(screen, player_position, entities, position, size):
    pass

def draw_effect_icons(screen, effects, position):
    pass

# Make it toggleable
def draw_inventory(screen, inventory, position):
    pass