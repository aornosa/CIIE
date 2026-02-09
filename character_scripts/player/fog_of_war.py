import pygame


def create_vision_mask(screen, player, camera, radius, player_radius, angle):
    screen_size = screen.get_size()
    mask = pygame.Surface(screen_size, pygame.SRCALPHA)
    mask.fill((0, 0, 0, 200))

    # Draw circle around the player
    pygame.draw.circle(mask, (255, 255, 255, 0), player.position-camera.position, player_radius)

    points = [player.position-camera.position+pygame.Vector2(player_radius, 0).rotate(-player.rotation),
              player.position-camera.position+pygame.Vector2(-player_radius, 0).rotate(-player.rotation)]

    start_angle = -player.rotation - angle / 2 -90
    end_angle = -player.rotation + angle / 2 -90

    for a in range(int(start_angle), int(end_angle) + 1, 2):
        vec = pygame.Vector2(1, 0).rotate(a)
        points.append(player.position -camera.position + vec * radius)

    pygame.draw.polygon(mask, (255, 255, 255, 255), points)

    return mask


