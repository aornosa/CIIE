import pygame


def create_vision_mask(screen, player, radius, angle, length):
    mask = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 255))

    points = [player.position]

    start_angle = player.rotation - angle / 2
    end_angle = player.rotation + angle / 2

    for a in range(int(start_angle), int(end_angle) + 1, 2):
        vec = pygame.Vector2(1, 0).rotate(a)
        points.append(player.position + vec * radius)

    pygame.draw.polygon(mask, (255, 255, 255, 255), points)

    return mask


