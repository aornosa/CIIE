import pygame

from game_math import utils as math
from ui import ui_manager

from core.camera import Camera
from character_scripts.player.player import Player
from character_scripts.character_controller import CharacterController
from runtime.round_manager import *
from status_effects import StatusEffect

player = Player("assets/player/survivor-idle_rifle_0.png", (0.0,0.0))
controller = CharacterController( 200, player)
camera = Camera()

enemies = spawn_enemies(5)



def game_loop(screen, clock, im):
    # Get delta time (time between frames)
    delta_time = clock.get_time() / 1000.0

    # Update Movement
    movement = pygame.Vector2(im.actions["move_x"], im.actions["move_y"])

    # Crosshair follows mouse
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    screen.blit(pygame.transform.scale(pygame.image.load("assets/crosshair.png"), (40, 40)), mouse_pos - (20, 20))

    # Hide mouse cursor
    pygame.mouse.set_visible(False)

    # Get current speed before calculating
    controller.speed = player.get_stat("speed")

    # Player game logic
    if im.actions["attack"] or im.actions["aim"]:
        # Slow player
        player.add_effect(StatusEffect("","Aiming Down Sights", {"speed": -70}, -1))


        # Look where shooting
        direction_to_mouse = mouse_pos - player.position
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

    # Draw UI last
    ui_manager.draw_overlay(screen, player)

