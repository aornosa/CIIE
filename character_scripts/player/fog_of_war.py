import pygame

OPACITY = 0.6

def create_vision_mask(screen, player, camera, radius, player_radius, angle):
    opacity = int(255 * OPACITY)
    screen_size = screen.get_size()
    mask = pygame.Surface(screen_size, pygame.SRCALPHA)
    mask.fill((0, 0, 0, opacity))

    # Draw circle around the player
    pygame.draw.circle(mask, (255, 255, 255, 0), player.position-camera.position, player_radius)

    points = [player.position-camera.position+pygame.Vector2(player_radius, 0).rotate(-player.rotation),
              player.position-camera.position+pygame.Vector2(-player_radius, 0).rotate(-player.rotation)]

    start_angle = -player.rotation - angle / 2 -90
    end_angle = -player.rotation + angle / 2 -90

    for a in range(int(start_angle), int(end_angle) + 1, 2):
        vec = pygame.Vector2(1, 0).rotate(a)
        points.append(player.position -camera.position + vec * radius)

    pygame.draw.polygon(mask, (0, 0, 0, 0), points)

    return mask

## Duplicated code. Fix later
def create_visibility_mask(screen, player, camera, radius, player_radius, angle):
    screen_size = screen.get_size()

    mask = pygame.Surface(screen_size, pygame.SRCALPHA)
    mask.fill((255, 255, 255, 0))

    player_pos = player.position - camera.position

    # visible circle
    pygame.draw.circle(mask, (255, 255, 255, 255), player_pos, player_radius)

    points = [
        player_pos + pygame.Vector2(player_radius, 0).rotate(-player.rotation),
        player_pos + pygame.Vector2(-player_radius, 0).rotate(-player.rotation)
    ]

    start_angle = -player.rotation - angle / 2 - 90
    end_angle = -player.rotation + angle / 2 - 90

    for a in range(int(start_angle), int(end_angle) + 1, 2):
        vec = pygame.Vector2(1, 0).rotate(a)
        points.append(player_pos + vec * radius)

    pygame.draw.polygon(mask, (255, 255, 255, 255), points)

    return mask

