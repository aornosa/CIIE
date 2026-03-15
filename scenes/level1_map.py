import pygame
from core.camera import Camera
from core.collision.collider import Collider
from core.collision.collision_manager import CollisionManager
from core.collision.layers import LAYERS
from core.collision.quadtree import Rectangle
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, _CAM_BORDER_RADIUS

_BG_COLOR    = (20, 20, 28)
_FLOOR_COLOR = (45, 45, 55)
_WALL_COLOR  = (110, 90, 70)
ARENA_HALF = 1000
WALL_THICK = 80
ACX        = SCREEN_WIDTH  // 2
ACY        = SCREEN_HEIGHT // 2
CORRIDOR_W      = 240
CORRIDOR_H      = 800
NORTH_SQ        = int(ARENA_HALF * 1.2)
EXIT_DOOR_W     = 240
EXIT_CORRIDOR_W = 240
EXIT_CORRIDOR_H = 300
EXIT_SQ_HALF    = 400

def build_room_rects():
    cx, cy = ACX, ACY
    h      = ARENA_HALF

    north_top_y = cy - h - CORRIDOR_H - NORTH_SQ * 2
    exit_ctr_y  = north_top_y - EXIT_CORRIDOR_H - EXIT_SQ_HALF

    north_room_rect = pygame.Rect(
        cx - NORTH_SQ, cy - h - CORRIDOR_H - NORTH_SQ * 2,
        NORTH_SQ * 2, NORTH_SQ * 2)
    corridor_rect = pygame.Rect(
        cx - CORRIDOR_W // 2, cy - h - CORRIDOR_H,
        CORRIDOR_W, CORRIDOR_H)
    exit_corridor_rect = pygame.Rect(
        cx - EXIT_CORRIDOR_W // 2,
        north_top_y - EXIT_CORRIDOR_H,
        EXIT_CORRIDOR_W, EXIT_CORRIDOR_H)
    exit_room_rect = pygame.Rect(
        cx - EXIT_SQ_HALF,
        exit_ctr_y - EXIT_SQ_HALF,
        EXIT_SQ_HALF * 2, EXIT_SQ_HALF * 2)

    return north_room_rect, corridor_rect, exit_corridor_rect, exit_room_rect


def build_walls():
    cx, cy = ACX, ACY
    h, t   = ARENA_HALF, WALL_THICK
    door_w = 240

    north_top_y = cy - h - CORRIDOR_H - NORTH_SQ * 2

    # Cada segmento: (cx, cy, half_h, half_w) en coordenadas de Rectangle (centro + semidimensiones)
    wall_segments = [
        # Arena — pared superior (flancos del hueco de puerta norte)
        (cx - (h + door_w // 2) / 2,      cy - h - t // 2, t // 2, (h - door_w // 2) / 2),
        (cx + (h + door_w // 2) / 2,      cy - h - t // 2, t // 2, (h - door_w // 2) / 2),
        # Pasillo norte — paredes laterales
        (cx - CORRIDOR_W // 2 - t // 2,   cy - h - CORRIDOR_H // 2, CORRIDOR_H // 2, t // 2),
        (cx + CORRIDOR_W // 2 + t // 2,   cy - h - CORRIDOR_H // 2, CORRIDOR_H // 2, t // 2),
        # Sala norte — pared inferior (flancos del hueco hacia pasillo)
        (cx - (NORTH_SQ + CORRIDOR_W // 2) / 2, cy - h - CORRIDOR_H - t // 2, t // 2, (NORTH_SQ - CORRIDOR_W // 2) / 2),
        (cx + (NORTH_SQ + CORRIDOR_W // 2) / 2, cy - h - CORRIDOR_H - t // 2, t // 2, (NORTH_SQ - CORRIDOR_W // 2) / 2),
        # Sala norte — paredes laterales
        (cx - NORTH_SQ - t // 2,          cy - h - CORRIDOR_H - NORTH_SQ, NORTH_SQ, t // 2),
        (cx + NORTH_SQ + t // 2,          cy - h - CORRIDOR_H - NORTH_SQ, NORTH_SQ, t // 2),
        # Sala norte — pared superior (flancos del hueco de puerta de salida)
        (cx - (NORTH_SQ + t + EXIT_DOOR_W // 2) // 2, north_top_y - t // 2, t // 2, (NORTH_SQ + t - EXIT_DOOR_W // 2) // 2),
        (cx + (NORTH_SQ + t + EXIT_DOOR_W // 2) // 2, north_top_y - t // 2, t // 2, (NORTH_SQ + t - EXIT_DOOR_W // 2) // 2),
        # Pasillo de salida — paredes laterales
        (cx - EXIT_CORRIDOR_W // 2 - t // 2, north_top_y - EXIT_CORRIDOR_H // 2, EXIT_CORRIDOR_H // 2, t // 2),
        (cx + EXIT_CORRIDOR_W // 2 + t // 2, north_top_y - EXIT_CORRIDOR_H // 2, EXIT_CORRIDOR_H // 2, t // 2),
        # Sala salida — pared inferior (flancos del hueco hacia pasillo)
        (cx - (EXIT_SQ_HALF + EXIT_CORRIDOR_W // 2) // 2, north_top_y - EXIT_CORRIDOR_H - t // 2, t // 2, (EXIT_SQ_HALF - EXIT_CORRIDOR_W // 2) // 2),
        (cx + (EXIT_SQ_HALF + EXIT_CORRIDOR_W // 2) // 2, north_top_y - EXIT_CORRIDOR_H - t // 2, t // 2, (EXIT_SQ_HALF - EXIT_CORRIDOR_W // 2) // 2),
        # Sala salida — paredes laterales
        (cx - EXIT_SQ_HALF - t // 2,      north_top_y - EXIT_CORRIDOR_H - EXIT_SQ_HALF, EXIT_SQ_HALF, t // 2),
        (cx + EXIT_SQ_HALF + t // 2,      north_top_y - EXIT_CORRIDOR_H - EXIT_SQ_HALF, EXIT_SQ_HALF, t // 2),
        # Sala salida — pared superior
        (cx,                               north_top_y - EXIT_CORRIDOR_H - EXIT_SQ_HALF * 2 - t // 2, t // 2, EXIT_SQ_HALF + t),
        # Arena — pared inferior, izquierda, derecha
        (cx,                               cy + h + t // 2, t // 2, h + t),
        (cx - h - t // 2,                  cy, h, t // 2),
        (cx + h + t // 2,                  cy, h, t // 2),
    ]

    for wx, wy, wh, ww in wall_segments:
        Collider(object(), Rectangle(wx, wy, wh, ww), layer=LAYERS["terrain"], static=True)

    dx, dy = ACX, ACY - ARENA_HALF - WALL_THICK // 2
    door_collider = Collider(
        object(), Rectangle(dx, dy, WALL_THICK // 2, door_w // 2),
        layer=LAYERS["terrain"], static=True)

    north_top_y = ACY - ARENA_HALF - CORRIDOR_H - NORTH_SQ * 2
    ex, ey = ACX, north_top_y - WALL_THICK // 2
    exit_door_collider = Collider(
        object(), Rectangle(ex, ey, WALL_THICK // 2, door_w // 2),
        layer=LAYERS["terrain"], static=True)

    return door_collider, exit_door_collider


def draw_map(screen, camera, scene):
    cx_cam = int(camera.position.x) if camera else 0
    cy_cam = int(camera.position.y) if camera else 0

    ax = ACX - ARENA_HALF - cx_cam
    ay = ACY - ARENA_HALF - cy_cam
    arena_rect = pygame.Rect(ax, ay, ARENA_HALF * 2, ARENA_HALF * 2)
    #pygame.draw.rect(screen, _FLOOR_COLOR, arena_rect)
    pygame.draw.rect(screen, _WALL_COLOR,  arena_rect, WALL_THICK)

    if scene._north_room_rect and scene._corridor_rect:
        nr  = scene._north_room_rect.move(-cx_cam, -cy_cam)
        cr  = scene._corridor_rect.move(-cx_cam, -cy_cam)
        pygame.draw.rect(screen, (35, 35, 45), nr)
        pygame.draw.rect(screen, _WALL_COLOR,  nr, WALL_THICK)
        pygame.draw.rect(screen, (35, 35, 45), cr)
        pygame.draw.rect(screen, _WALL_COLOR,  (cr.x - WALL_THICK, cr.y, WALL_THICK, cr.height))
        pygame.draw.rect(screen, _WALL_COLOR,  (cr.right, cr.y, WALL_THICK, cr.height))
        # Tapa la junta entre la arena y el pasillo
        pygame.draw.rect(screen, (35, 35, 45), (cr.x - 2, cr.top - WALL_THICK - 2, cr.width + 4, WALL_THICK + 4))
        if not scene._door or scene._door.is_open:
            pygame.draw.rect(screen, _FLOOR_COLOR,
                             (cr.x - 2, cr.bottom - WALL_THICK - 2, cr.width + 4, WALL_THICK + 4))

    door_w = 240
    side   = (ARENA_HALF * 2 - door_w) // 2
    pygame.draw.rect(screen, _WALL_COLOR, (ax,                  ay - WALL_THICK, side,           WALL_THICK))
    pygame.draw.rect(screen, _WALL_COLOR, (ax + side + door_w,  ay - WALL_THICK, side,           WALL_THICK))
    pygame.draw.rect(screen, _WALL_COLOR, (ax,                  ay + ARENA_HALF * 2, ARENA_HALF * 2, WALL_THICK))
    pygame.draw.rect(screen, _WALL_COLOR, (ax - WALL_THICK,     ay, WALL_THICK,     ARENA_HALF * 2))
    pygame.draw.rect(screen, _WALL_COLOR, (ax + ARENA_HALF * 2, ay, WALL_THICK,     ARENA_HALF * 2))

    if scene._door:
        if not scene._door.is_open:
            dr = scene._door_rect.move(-cx_cam, -cy_cam)
            pygame.draw.rect(screen, (80, 50, 20), dr)
            pygame.draw.rect(screen, (20, 15, 10), dr, 4)
        scene._door.draw(screen, camera)

    if scene._exit_room_rect and scene._exit_corridor_rect:
        er  = scene._exit_room_rect.move(-cx_cam, -cy_cam)
        ecr = scene._exit_corridor_rect.move(-cx_cam, -cy_cam)
        pygame.draw.rect(screen, (25, 45, 35), er)
        pygame.draw.rect(screen, _WALL_COLOR,  er, WALL_THICK)
        pygame.draw.rect(screen, (25, 45, 35), ecr)
        pygame.draw.rect(screen, _WALL_COLOR,  (ecr.x - WALL_THICK, ecr.y, WALL_THICK, ecr.height))
        pygame.draw.rect(screen, _WALL_COLOR,  (ecr.right, ecr.y, WALL_THICK, ecr.height))
        pygame.draw.rect(screen, (25, 45, 35),
                         (ecr.x - 2, ecr.top - WALL_THICK - 2, ecr.width + 4, WALL_THICK + 4))
        if not scene._exit_door or scene._exit_door.is_open:
            pygame.draw.rect(screen, (35, 35, 45),
                             (ecr.x - 2, ecr.bottom - WALL_THICK - 2, ecr.width + 4, WALL_THICK + 4))
        if scene._north_room_rect:
            nr = scene._north_room_rect.move(-cx_cam, -cy_cam)
            # Tapa la junta entre la sala norte y el pasillo de salida
            pygame.draw.rect(screen, (35, 35, 45), (nr.centerx - 120, nr.y, 240, WALL_THICK + 2))

    if scene._exit_door and scene._exit_door_rect:
        if not getattr(scene._exit_door, "is_open", True):
            er = scene._exit_door_rect.move(-cx_cam, -cy_cam)
            pygame.draw.rect(screen, (80, 50, 20), er)
            pygame.draw.rect(screen, (20, 15, 10), er, 4)
        scene._exit_door.draw(screen, camera)

    if scene._north_room_sealed and scene._door_rect:
        pygame.draw.rect(screen, _WALL_COLOR, scene._door_rect.move(-cx_cam, -cy_cam))


def draw_reload_bar(screen, player, camera, weapon):
    elapsed  = (pygame.time.get_ticks() - weapon._reload_start_time) / 1000.0
    progress = min(elapsed / weapon.reload_time, 1.0)
    sp       = player.position - camera.position
    bw, bh   = 80, 8
    bx, by   = int(sp.x) - bw // 2, int(sp.y) + 32
    pygame.draw.rect(screen, (20, 20, 20),   (bx - 1, by - 1, bw + 2, bh + 2), border_radius=4)
    pygame.draw.rect(screen, (60, 60, 60),   (bx, by, bw, bh), border_radius=3)
    pygame.draw.rect(screen, (255, 160, 20), (bx, by, int(bw * progress), bh), border_radius=3)


def camera_follow(camera, target, delta_time, speed=10):
    target_relative = target - camera.position
    center          = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    offset          = target_relative - center
    distance        = offset.length()
    if distance > _CAM_BORDER_RADIUS:
        camera.move(offset.normalize() * (distance - _CAM_BORDER_RADIUS) * speed * delta_time)


def build_interactables(scene):
    from map.interactables.door import Door
    from item.item_drop_manager import HelicopterInteractable
    import scenes.level1_logic as logic

    cx, cy = ACX, ACY
    t      = WALL_THICK
    door_w = 240

    dx, dy           = cx, cy - ARENA_HALF - t // 2
    # Puerta norte: gratuita pero solo abre al completar oleada 10
    scene._door      = Door("Puerta Norte", (dx, dy), 0,
                            lambda: logic.on_north_door_open(scene),
                            unlock_condition=lambda: getattr(scene, "_zone1_complete", False))
    scene._door_rect = pygame.Rect(dx - door_w // 2, dy - t // 2, door_w, t)

    north_top_y           = cy - ARENA_HALF - CORRIDOR_H - NORTH_SQ * 2
    ex, ey                = cx, north_top_y - t // 2
    # Puerta salida: gratuita pero solo abre al completar oleada 25
    scene._exit_door      = Door("Puerta de Salida", (ex, ey), 0,
                                 lambda: logic.on_exit_door_open(scene),
                                 unlock_condition=lambda: getattr(scene, "_zone2_complete", False))
    scene._exit_door_rect = pygame.Rect(ex - door_w // 2, north_top_y - t, door_w, t)

    heli_y                    = north_top_y - EXIT_CORRIDOR_H - EXIT_SQ_HALF * 2
    scene._helicopter         = HelicopterInteractable((cx, heli_y), scene)
    scene._helicopter_spawned = True