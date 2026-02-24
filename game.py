from character_scripts.player.inventory import show_inventory
from core.collision.collision_manager import CollisionManager
from core.collision.quadtree import Rectangle

from game_math import utils as math

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, _CAM_BORDER_RADIUS
from ui import ui_manager
from ui.fps_counter import FPS_Counter
from ui.dialog import draw_dialog_ui

from core.camera import Camera
from character_scripts.player.player import Player
from character_scripts.player.fog_of_war import *
from character_scripts.character_controller import CharacterController
from weapons.ranged.ranged import Ranged
from runtime.round_manager import *
from core.status_effects import StatusEffect
from dialogs.dialog_manager import DialogManager
from dialogs.test_dialogs import create_test_dialog_simple
from map.interactables.npc import NPC

# Predeclaration
world_bounds = Rectangle(-2000, -2000, 4000, 4000)
camera = Camera()

# Monolite Build Order
CollisionManager(world_bounds, camera)
FPS_Counter()


player = Player("assets/player/survivor-idle_rifle_0.png", (0.0,0.0))
controller = CharacterController( 250, player)

enemies = spawn_enemies(5)

test_weapon = Ranged("assets/weapons/AK47.png", "AK-47", 60, 1500,
                     "rifle", 30, 0.1, 2, muzzle_offset=(20, 20))


# Test weapon on inventory
player.inventory.add_weapon(player, test_weapon, "primary")

# Make crosshair
crosshair = pygame.image.load("assets/crosshair.png").convert_alpha()

# Status effects
ads_se = StatusEffect("assets/effects/ads","Aiming Down Sights", {"speed": -70}, -1)

# Dialog System
dialog_manager = DialogManager()

# Test NPC with dialog
test_npc = NPC(
    name="npc",
    dialog_tree=create_test_dialog_simple(),
    position=(300, 200)
)

# Bool state flags (change into enumerated state manager later)
inventory_is_open = False
can_attack = True
attack_ready_time = 0
can_aim = True

FOG_ENABLE = 0 # Very resource intensive, need to optimize before enabling.

# Shared state updated by game_update, read by game_render
_last_movement = pygame.Vector2(0, 0)
_last_mouse_pos = pygame.Vector2(0, 0)


def game_update(delta_time, im):
    """Update all game logic (input, movement, combat, AI). No drawing."""
    global inventory_is_open
    global can_attack
    global can_aim
    global attack_ready_time
    global _last_movement
    global _last_mouse_pos

    # Handle dialog input (takes priority when active)
    dialog_manager.input_handler = im
    dialog_manager.handle_input(im.get_keys_pressed(), im.get_keys_just_pressed())

    # Update Movement (disabled during dialog)
    if dialog_manager.is_dialog_active:
        _last_movement = pygame.Vector2(0, 0)
    else:
        _last_movement = pygame.Vector2(im.actions["move_x"], im.actions["move_y"])

    movement = _last_movement

    # Crosshair follows mouse
    _last_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    mouse_pos = _last_mouse_pos

    # Make camera follow player
    if im.actions["look_around"]:
        camera_follow(mouse_pos, camera, delta_time, speed=5, position_relative=False)
    else:
        camera_follow(player.position, camera, delta_time)

    # Hide mouse cursor
    pygame.mouse.set_visible(False)

    # Get current speed before calculating
    controller.speed = player.get_stat("speed")

    # Check NPC interaction
    if im.actions["interact"] and not dialog_manager.is_dialog_active:
        im.actions["interact"] = False
        if test_npc.is_player_in_range(player.position):
            test_npc.interact(player, dialog_manager)
    
    # Toggle inventory (disabled during dialog)
    if im.actions["inventory"] and not dialog_manager.is_dialog_active:
        im.actions["inventory"] = False
        inventory_is_open = not inventory_is_open
        print("Inventory toggled:", inventory_is_open)

    if im.actions["swap_weapon"]:
        im.actions["swap_weapon"] = False
        player.inventory.swap_weapons()
        print("Active slot:", player.inventory.active_weapon_slot)

    active_weapon = player.inventory.get_weapon(player.inventory.active_weapon_slot)

    if im.actions["reload"]:
        im.actions["reload"] = False
        if active_weapon is not None:
            active_weapon.reload()

    # Player game logic
    if im.actions["attack"] or im.actions["aim"]:
        player.add_effect(ads_se)

        direction_to_mouse = mouse_pos - (player.position - camera.position)
        target_angle = direction_to_mouse.angle_to(pygame.Vector2(0, -1))
        player.set_rotation(math.lerp_angle(player.rotation, target_angle, 10 * delta_time)+0.164)

        if im.actions["attack"] and can_attack:
            if active_weapon is not None and can_attack:
                active_weapon.shoot()

    elif movement.length() > 0.:
        target_angle = movement.angle_to(pygame.Vector2(0, -1))
        player.rotation = math.lerp_angle(player.rotation, target_angle, 7.5 * delta_time)

    if not im.actions["attack"] and not im.actions["aim"]:
        player.remove_effect("Aiming Down Sights")

    # Move player
    controller.move(movement, delta_time)

    # Inventory state
    if inventory_is_open:
        can_aim = False
        can_attack = False
    else:
        can_aim = True
        can_attack = True


def game_render(screen):
    """Draw the current game state. No logic updates."""
    mouse_pos = _last_mouse_pos

    # Weapon particle emitter needs screen ref
    test_weapon.emitter.surface = screen
    test_weapon.emitter.camera = camera

    # Trail effect (visual only – uses last known state)
    active_weapon = player.inventory.get_weapon(player.inventory.active_weapon_slot)
    if active_weapon and isinstance(active_weapon, Ranged):
        direction = pygame.Vector2(0, -1).rotate(-player.rotation)
        # Only play trail when attacking (check mouse button directly)
        if pygame.mouse.get_pressed()[0]:
            active_weapon.play_trail_effect(
                screen,
                (player.position - camera.position) + direction * 35 + direction.rotate(90) * 15,
                direction,
            )

    # Fog of war
    visibility_mask = None
    if FOG_ENABLE:
        fog_mask = create_vision_mask(screen, player, camera, 1800, 250, 80)
        screen.blit(fog_mask, (0, 0))
        visibility_mask = create_visibility_mask(screen, player, camera, 1800, 250, 80)

    entity_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    for enemy in enemies:
        enemy.draw(entity_surface, camera)

    #test_npc.draw(entity_surface, camera)

    if FOG_ENABLE:
        entity_surface.blit(visibility_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    screen.blit(entity_surface, (0, 0))

    # Draw player
    player.draw(screen, camera)

    # Draw inventory on top if open
    if inventory_is_open:
        show_inventory(screen, player)

    # Draw crosshair
    screen.blit(pygame.transform.scale(crosshair, (40, 40)),
                (mouse_pos - (20, 20)))

    # Draw UI last
    ui_manager.draw_overlay(screen, player)

    # Draw dialog UI (must be last, on top of everything)
    draw_dialog_ui(screen, dialog_manager)


# Legacy wrapper – keeps old call sites working if needed
def game_loop(screen, clock, im):
    delta_time = clock.get_time() / 1000.0
    game_update(delta_time, im)
    game_render(screen)


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