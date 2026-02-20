from character_scripts.player.inventory import show_inventory
from core.collision.collision_manager import CollisionManager
from core.collision.quadtree import Rectangle

from game_math import utils as math
from item.item_loader import ItemRegistry

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
ItemRegistry()
ItemRegistry.load("assets/items/item_data.json")


player = Player("assets/player/survivor-idle_rifle_0.png", (0.0,0.0))
controller = CharacterController( 250, player)

enemies = spawn_enemies(5)

test_weapon = Ranged("assets/weapons/AK47.png", "AK-47", 60, 1500,
                     "7.62", 30, 0.1, 2, muzzle_offset=(20, 20))


# Test weapon on inventory
player.inventory.add_weapon(player, test_weapon, "primary")
player.inventory.add_item(ItemRegistry.get("ammo_clip_762"))
player.inventory.add_item(ItemRegistry.get("health_injector"))

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

if FOG_ENABLE:
    fow = FogOfWar(player, camera)
FPS_Counter()

# Main game loop
def game_loop(screen, clock, im):
    # global vars (change later)
    global inventory_is_open
    global can_attack
    global can_aim
    global attack_ready_time
    global fow

    # Refactor to render independently
    test_weapon.emitter.surface = screen
    test_weapon.emitter.camera = camera

    # Get delta time (time between frames)
    delta_time = clock.get_time() / 1000.0
    
    # Handle dialog input (takes priority when active)
    # InputHandler now manages all key state
    dialog_manager.input_handler = im  # Set reference
    dialog_manager.handle_input(im.get_keys_pressed(), im.get_keys_just_pressed())

    # Update Movement (disabled during dialog)
    if dialog_manager.is_dialog_active:
        movement = pygame.Vector2(0, 0)
    else:
        movement = pygame.Vector2(im.actions["move_x"], im.actions["move_y"])

    # Crosshair follows mouse
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

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
            test_npc.interact(player)
    
    # Toggle inventory (disabled during dialog)
    if im.actions["inventory"] and not dialog_manager.is_dialog_active:
        im.actions["inventory"] = False  # Reset action
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
        # Slow player
        player.add_effect(ads_se)


        # Look where shooting
        direction_to_mouse = mouse_pos - (player.position - camera.position)
        target_angle = direction_to_mouse.angle_to(pygame.Vector2(0, -1))  # relative to up
        player.set_rotation(math.lerp_angle(player.rotation, target_angle, 10 * delta_time)+0.164)

        # Shoot if attacking
        if im.actions["attack"] and can_attack:
            direction = pygame.Vector2(0, -1).rotate(-player.rotation)
            if isinstance(active_weapon, Ranged):
                active_weapon.play_trail_effect(screen, (player.position - camera.position)
                                                                  + direction * 35 + direction.rotate(90) * 15
                                                                  , direction)
            if active_weapon is not None and can_attack:
                active_weapon.shoot()

    elif movement.length() > 0.:  # Only rotate if there's movement
        target_angle = movement.angle_to(pygame.Vector2(0, -1)) # relative to up
        player.rotation = math.lerp_angle(player.rotation, target_angle, 7.5 * delta_time)

    if not im.actions["attack"] and not im.actions["aim"]:
        player.remove_effect("Aiming Down Sights")


    # create fog of war
    visibility_mask = None
    if FOG_ENABLE:
        visibility_mask = fow.visibility_mask

    entity_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # draw enemies/items onto entity surface
    for enemy in enemies:
        enemy.draw(entity_surface, camera)
    
    # Draw NPC
    #test_npc.draw(entity_surface, camera)

    if FOG_ENABLE:
        # clip entities using mask
        entity_surface.blit(visibility_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # draw result
    screen.blit(entity_surface, (0, 0))

    # Move and draw player
    controller.move(movement, delta_time)
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
    screen.blit(pygame.transform.scale(crosshair, (40, 40)),
                (mouse_pos - (20, 20)))

    # Draw UI last
    ui_manager.draw_overlay(screen, player)
    
    # Draw dialog UI (must be last, on top of everything)
    draw_dialog_ui(screen, dialog_manager)


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