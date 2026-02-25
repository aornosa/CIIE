import pygame

FONT_30 = pygame.font.SysFont("consolas", 30, bold=True)
FONT_25 = pygame.font.SysFont("consolas", 25, bold=True)
FONT_12 = pygame.font.SysFont("consolas", 12, bold=True)
FONT_28 = pygame.font.SysFont("consolas", 28)

def draw_weapon_box(screen, weapon, position):
    box_size = (550, 400)
    # Draw box background
    draw_box(screen, position, box_size, (50, 50, 50))
    # Draw weapon representation (placeholder)
    if weapon:
        screen.blit(weapon.asset, (position[0] + 100, position[1] + 150))
        # Draw weapon name
        FONT_30.bold = True
        text_surface = FONT_30.render(weapon.name, True, (255, 255, 255))
        screen.blit(text_surface, (position[0] + 30, position[1] + 40))
        # Draw weapon damage
        FONT_25.bold = True
        damage_text = f"Damage: {weapon.damage}"
        text_surface = FONT_25.render(damage_text, True, (200, 200, 200))
        screen.blit(text_surface, (position[0] + 40, position[1] + 80))
    else:
        # Draw none text
        font = pygame.font.SysFont("consolas", 25)
        font.bold = True
        text_surface = font.render("{ No Weapon }", True, (200, 200, 200))
        screen.blit(text_surface, (position[0] + 190, position[1] + 195))

def draw_item_box(screen, item, position):
    draw_box(screen, position, (100, 100), (50, 50, 50))
    if item:
        item.asset = pygame.transform.scale(item.asset, (60, 60))
        screen.blit(item.asset, (position[0] + 20, position[1] + 20))
        # Draw item name
        FONT_12.bold = True
        text_surface = FONT_12.render(item.name, True, (255, 255, 255))
        screen.blit(text_surface, (position[0] + 10, position[1]))

def draw_player_status(screen, player, position):
    # Draw status background
    draw_box(screen, (position[0], position[1]), (300, 400), (30, 30, 30))
    # Draw stats
    font = pygame.font.SysFont("consolas", 28)

    health_text = f"Health: {player.health}/{player.get_stat('max_health')}"
    speed_text = f"Speed: {player.get_stat('speed')}"

    health_surface = font.render(health_text, True, (255, 0, 0))
    speed_surface = font.render(speed_text, True, (0, 255, 0))

    screen.blit(health_surface, (position[0]+20, position[1]+ 20))
    screen.blit(speed_surface, (position[0]+20, position[1] + 50))


def draw_box(screen, position, size, color):
    pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]))