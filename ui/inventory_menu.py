import pygame

def draw_weapon_box(screen, weapon, position):
    box_size = (550, 400)
    # Draw box background
    draw_box(screen, position, box_size, (50, 50, 50))
    # Draw weapon representation (placeholder)
    if weapon:
        draw_box(screen, (position[0] + 50, position[1] + 50), (400, 300), (100, 100, 100))
    else:
        # Draw none text
        font = pygame.font.SysFont("consolas", 25)
        font.bold = True
        text_surface = font.render("{ No Weapon }", True, (200, 200, 200))
        screen.blit(text_surface, (position[0] + 190, position[1] + 195))

def draw_item_box(screen, item, position):
    draw_box(screen, position, (100, 100), (50, 50, 50))

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