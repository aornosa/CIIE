import pygame

from core.collision.collision_manager import CollisionManager


def raycast_segment(start, end, *, layers=None, tags=None, include_self=False, ignore=None):
    """
    Segment cast from start -> end against all colliders.

    Returns:
        (hit_collider, hit_point, t) or (None, None, None)
        - hit_point: pygame.Vector2 of first impact
        - t: float in [0, 1] along the segment
    """
    sx, sy = float(start[0]), float(start[1])
    ex, ey = float(end[0]), float(end[1])

    candidates = []
    if hasattr(CollisionManager, "static_colliders"):
        candidates.extend(CollisionManager.static_colliders)
    if hasattr(CollisionManager, "dynamic_colliders"):
        candidates.extend(CollisionManager.dynamic_colliders)

    dx = ex - sx
    dy = ey - sy

    tagset = None
    if tags is not None:
        tagset = tags if isinstance(tags, (set, frozenset)) else set(tags)

    best_col = None
    best_t = float("inf")
    best_pt = None

    for col in candidates:
        if col is None:
            continue
        if ignore is not None and col is ignore:
            continue
        if not include_self and ignore is None and col is None:
            continue

        if layers is not None and col.layer not in layers:
            continue
        if tagset is not None and col.tag not in tagset:
            continue

        clipped = col.rect.to_rect().clipline((sx, sy), (ex, ey))
        if not clipped:
            continue

        (x1, y1), (x2, y2) = clipped

        # Choose entry point closest to start
        d1 = (x1 - sx) * (x1 - sx) + (y1 - sy) * (y1 - sy)
        d2 = (x2 - sx) * (x2 - sx) + (y2 - sy) * (y2 - sy)
        hx, hy = (x1, y1) if d1 <= d2 else (x2, y2)

        # Parameter t along segment
        if abs(dx) >= abs(dy):
            t = (hx - sx) / dx if dx != 0.0 else 0.0
        else:
            t = (hy - sy) / dy if dy != 0.0 else 0.0

        if 0.0 <= t <= 1.0 and t < best_t:
            best_t = t
            best_col = col
            best_pt = pygame.Vector2(hx, hy)

    if best_col is None:
        return None, None, None
    return best_col, best_pt, best_t