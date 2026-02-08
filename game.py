import pygame

from character_scripts.player.inventory import show_inventory
from game_math import utils as math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, _CAM_BORDER_RADIUS
from ui import ui_manager

from core.camera import Camera
from character_scripts.player.player import Player
from character_scripts.character_controller import CharacterController
from weapons.ranged.ranged import Ranged
from runtime.round_manager import *
from status_effects import StatusEffect

player = Player("assets/player/survivor-idle_rifle_0.png", (0.0,0.0))
controller = CharacterController( 250, player)
camera = Camera()

enemies = spawn_enemies(5)

test_weapon = Ranged("assets/weapons/ak47.png", "AK-47", 60, 1000,
                     "rifle", 30, 0.1, 2)
# Test weapon on inventory
player.inventory.add_weapon(test_weapon, "primary")


# Bool state flags (change into enumerated state manager later)
inventory_is_open = False
can_attack = True
can_aim = True

# Main game loop
def game_loop(screen, clock, im):
    # global vars (change later)
    global inventory_is_open
    global can_attack
    global can_aim

    # Get delta time (time between frames)
    delta_time = clock.get_time() / 1000.0

    # Update Movement
    movement = pygame.Vector2(im.actions["move_x"], im.actions["move_y"])

    # Crosshair follows mouse
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())


    # Make camera follow player
    if im.actions["look_around"]:
        camera_follow(mouse_pos, camera, delta_time, speed=5,position_relative=False)
    else:
        camera_follow(player.position, camera, delta_time)


    # Hide mouse cursor
    pygame.mouse.set_visible(False)

    # Get current speed before calculating
    controller.speed = player.get_stat("speed")

    # Toggle inventory
    if im.actions["inventory"]:
        im.actions["inventory"] = False  # Reset action
        inventory_is_open = not inventory_is_open
        print("Inventory toggled:", inventory_is_open)

    # Player game logic
    if im.actions["attack"] or im.actions["aim"]:
        # Slow player
        player.add_effect(StatusEffect("assets/effects/ads","Aiming Down Sights", {"speed": -70}, -1))


        # Look where shooting
        direction_to_mouse = mouse_pos - (player.position - camera.position)
        target_angle = direction_to_mouse.angle_to(pygame.Vector2(0, -1))  # relative to up
        player.rotation = math.lerp_angle(player.rotation, target_angle, 10 * delta_time)
    elif movement.length() > 0.:  # Only rotate if there's movement
        target_angle = movement.angle_to(pygame.Vector2(0, -1)) # relative to up
        player.rotation = math.lerp_angle(player.rotation, target_angle, 7.5 * delta_time)

    if not im.actions["attack"] and not im.actions["aim"]:
        player.remove_effect("Aiming Down Sights")


    # Draw enemies for testing
    for enemy in enemies:
        enemy.draw(screen, camera)


    # Move and draw player
    controller.move(movement, delta_time)
    camera.move((im.actions["look_x"]* delta_time * 300, im.actions["look_y"]* delta_time * 300)) #Testing
    player.draw(screen, camera)

    # Draw inventory on top if open
    if inventory_is_open:
        can_aim = False
        can_attack = False
        show_inventory(screen, player)
    else:
        can_aim = True
        can_attack = True

    # Draw crosshair
    screen.blit(pygame.transform.scale(pygame.image.load("assets/crosshair.png"), (40, 40)), (mouse_pos - (20, 20)))

    # Draw UI last
    ui_manager.draw_overlay(screen, player)


def camera_follow(target, cam, delta_time, speed=10, position_relative=True):
    target_relative_pos = target - cam.position if position_relative else target
    camera_center = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    center_offset = target_relative_pos - camera_center

    distance_from_center = center_offset.length()
    if distance_from_center > _CAM_BORDER_RADIUS:
        # Calculate how much to move camera
        excess_distance = distance_from_center - _CAM_BORDER_RADIUS
        move_direction = center_offset.normalize()

        # Move camera towards player smoothly
        camera_move = move_direction * excess_distance * speed * delta_time  # Bigger = snappier
        camera.move(camera_move)