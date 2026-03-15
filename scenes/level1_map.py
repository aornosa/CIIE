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

ARENA_HALF      = 1000
WALL_THICK      = 80
ACX             = SCREEN_WIDTH  // 2
ACY             = SCREEN_HEIGHT // 2
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

    dx, dy      = cx, cy - ARENA_HALF - t // 2
    scene._door = Door("Puerta Norte", (dx, dy), 0,
                       lambda: logic.on_north_door_open(scene),
                       unlock_condition=lambda: getattr(scene, "_zone1_complete", False))
    scene._door_rect = pygame.Rect(dx - door_w // 2, dy - t // 2, door_w, t)

    north_top_y           = cy - ARENA_HALF - CORRIDOR_H - NORTH_SQ * 2
    ex, ey                = cx, north_top_y - t // 2
    scene._exit_door      = Door("Puerta de Salida", (ex, ey), 0,
                                 lambda: logic.on_exit_door_open(scene),
                                 unlock_condition=lambda: getattr(scene, "_zone2_complete", False))
    scene._exit_door_rect = pygame.Rect(ex - door_w // 2, north_top_y - t, door_w, t)

    heli_y                    = north_top_y - EXIT_CORRIDOR_H - EXIT_SQ_HALF * 2
    scene._helicopter         = HelicopterInteractable((cx, heli_y), scene)
    scene._helicopter_spawned = True