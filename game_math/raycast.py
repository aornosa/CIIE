import pygame
import math

def raycast(origin, direction, max_distance, targets):
    """
    Cast a ray from origin in the given direction and check for collisions with targets.

    :param origin: Starting point of the ray (pygame.Vector2)
    :param direction: Normalized direction vector (pygame.Vector2)
    :param max_distance: Maximum distance the ray can travel
    :param targets: List of target objects with get_position() and get_radius() methods
    :return: The first target hit or None if no hit
    """
    end_point = origin + direction * max_distance

    for target in targets:
        target_pos = target.get_position()
        target_radius = target.get_radius()

        # Check if the ray intersects with the target's circle
        to_target = target_pos - origin
        projection_length = to_target.dot(direction)

        if 0 <= projection_length <= max_distance:
            closest_point = origin + direction * projection_length
            distance_to_target = (closest_point - target_pos).length()

            if distance_to_target <= target_radius:
                return target  # Hit detected
    return None  # No hit