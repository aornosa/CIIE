from __future__ import annotations
from character_scripts.player.inventory import show_inventory
from core.audio.audio_manager import AudioManager
from core.collision.collision_manager import CollisionManager
from core.collision.quadtree import Rectangle
from game_math import utils as math
from item.item_instance import ItemInstance
from item.item_loader import ItemRegistry
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, _CAM_BORDER_RADIUS
from ui import ui_manager
from ui.fps_counter import FPS_Counter
from ui.dialog import draw_dialog_ui
from ui.inventory_menu import get_clicked_item_index
from core.camera import Camera
from character_scripts.player.player import Player
from character_scripts.player.fog_of_war import *
from character_scripts.character_controller import CharacterController
from weapons.ranged.ranged_types import *
from weapons.melee.melee import Melee
from weapons.melee.melee_types import *
from weapons.weapon_controller import WeaponController
from runtime.round_manager import WaveManager
from core.status_effects import StatusEffect
from dialogs.dialog_manager import DialogManager
from dialogs.test_dialogs import create_test_dialog_simple
from character_scripts.npc.npc import NPC
from map.interactables.interaction_manager import InteractionManager
from map.interactables.door import Door
from map.map_loader import MapLoader

map_loader = MapLoader()
loaded_map = map_loader.load_map("test.json")
map_loader.map = loaded_map

tile_images = MapLoader.load_tileset_to_dict('assets/tiles/Dungeon_Tileset.png')

world_bounds = Rectangle(-2000, -2000, 4000, 4000)
camera = Camera()

CollisionManager(world_bounds, camera)
ItemRegistry()
ItemRegistry.load("assets/items/item_data.json")
AudioManager()

player = Player("assets/player/survivor-idle_rifle_0.png", (1600.0, 800.0))
controller = CharacterController(250, player)
weapon_controller = WeaponController(player)
wave_manager = WaveManager(player, total_waves=10)

ak47 = AK47()
tactical_knife = TacticalKnife()

player.inventory.add_weapon(player, tactical_knife, "secondary")
player.inventory.add_weapon(player, ak47, "primary")
player.inventory.add_item(ItemInstance(ItemRegistry.get("ammo_clip_762")))
player.inventory.add_item(ItemInstance(ItemRegistry.get("health_injector")))
player.inventory.add_item(ItemInstance(ItemRegistry.get("stim_patch")))
player.inventory.add_item(ItemInstance(ItemRegistry.get("adrenaline_shot")))
player.inventory.add_item(ItemInstance(ItemRegistry.get("rad_suppressor")))

AudioManager.instance().set_listener(player.audio_listener)

crosshair      = pygame.image.load("assets/crosshair.png").convert_alpha()
ads_se         = StatusEffect("assets/effects/ads", "Aiming Down Sights", {"speed": -70}, -1)
dialog_manager = DialogManager()
test_npc       = NPC(name="npc", position=(300, 200), dialog_tree=create_test_dialog_simple())
interaction_manager = InteractionManager()

door_1 = Door(
    name="Sala 2",
    position=(1800, 800),
    cost=500,
    on_open=lambda: print("[MAP] Sala 2 desbloqueada")
)

inventory_is_open = False
FOG_ENABLE = 0
if FOG_ENABLE:
    fow = FogOfWar(player, camera)

FPS_Counter()


def game_loop(screen, clock, im):
    global inventory_is_open

    delta_time = clock.get_time() / 1000.0

    # ── Muerte del jugador ─────────────────────────────────────────────────────
    if not player.is_alive():
        wave_manager.notify_player_dead()
        return

    # ── Oleadas ────────────────────────────────────────────────────────────────
    wave_manager.update(delta_time, screen)
    enemies = wave_manager.enemies

    # ── Mapa ───────────────────────────────────────────────────────────────────
    map_loader.draw_active_chunks(screen, camera.position, tile_images, player)

    # ── Diálogos ───────────────────────────────────────────────────────────────
    dialog_manager.input_handler = im
    dialog_manager.handle_input(im.get_keys_pressed(), im.get_keys_just_pressed())

    # ── Input ──────────────────────────────────────────────────────────────────
    movement  = pygame.Vector2(0, 0) if dialog_manager.is_dialog_active \
                else pygame.Vector2(im.actions["move_x"], im.actions["move_y"])
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

    # ── Cámara ─────────────────────────────────────────────────────────────────
    if im.actions["look_around"]:
        camera_follow(mouse_pos, camera, delta_time, speed=5, position_relative=False)
    else:
        target = player.position - pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        camera.position = camera.position.lerp(target, min(15 * delta_time, 1.0))

    pygame.mouse.set_visible(False)
    controller.speed = player.get_stat("speed")

    # ── Interacciones ──────────────────────────────────────────────────────────
    if not dialog_manager.is_dialog_active:
        interaction_manager.check_interaction(player, im)

    # ── Inventario ─────────────────────────────────────────────────────────────
    if im.actions["inventory"] and not dialog_manager.is_dialog_active:
        im.actions["inventory"] = False
        inventory_is_open = not inventory_is_open

    if im.actions["use_item"]:
        player.inventory.use_selected_item(player)

    if im.actions["hotkey_slot"] >= 0:
        player.inventory.use_consumable_hotkey(im.actions["hotkey_slot"], player)

    # ── Rotación jugador hacia ratón ───────────────────────────────────────────
    active_weapon      = player.inventory.get_weapon(player.inventory.active_weapon_slot)
    direction_to_mouse = mouse_pos - (player.position - camera.position)

    if direction_to_mouse.length() > 5:
        target_angle = direction_to_mouse.angle_to(pygame.Vector2(0, -1))
        lerp_speed   = 20 * delta_time if (im.actions["attack"] or im.actions["aim"]) else 12 * delta_time
        player.set_rotation(math.lerp_angle(player.rotation, target_angle, lerp_speed) + 0.164)

    if im.actions["attack"] or im.actions["aim"]:
        player.add_effect(ads_se)
    else:
        player.remove_effect("Aiming Down Sights")

    # ── Trail de disparo ───────────────────────────────────────────────────────
    try:
        if im.actions["attack"] and isinstance(active_weapon, Ranged) and active_weapon.can_shoot():
            direction = pygame.Vector2(0, -1).rotate(-player.rotation)
            active_weapon.play_trail_effect(
                screen,
                (player.position - camera.position)
                + direction * active_weapon.muzzle_offset[0]
                + direction.rotate(90) * active_weapon.muzzle_offset[1],
                direction,
            )
    except Exception:
        pass

    # ── Actualizar armas y mover jugador ──────────────────────────────────────
    weapon_controller.update(im, delta_time)
    controller.move(movement, delta_time)

    # ── Render: enemigos ───────────────────────────────────────────────────────
    entity_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for enemy in enemies:
        enemy.draw(entity_surface, camera)

    if FOG_ENABLE:
        entity_surface.blit(fow.visibility_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    screen.blit(entity_surface, (0, 0))

    # ── Render: items, jugador, puertas ───────────────────────────────────────
    player.inventory.drop_manager.draw(screen, camera)
    player.draw(screen, camera)
    door_1.draw(screen, camera)

    if isinstance(active_weapon, Melee):
        active_weapon.draw_attack_cone(screen, camera)

    # ── Inventario abierto ─────────────────────────────────────────────────────
    if inventory_is_open:
        if pygame.mouse.get_pressed()[0]:
            idx = get_clicked_item_index(pygame.mouse.get_pos(), player.inventory)
            if idx >= 0:
                player.inventory.select_item(idx)
        if im.actions.get("click_drop"):
            im.actions["click_drop"] = False
            player.inventory.click_drop_item(mouse_pos)
        show_inventory(screen, player)
    else:
        im.actions["click_drop"] = False

    # ── HUD y diálogo ──────────────────────────────────────────────────────────
    screen.blit(pygame.transform.scale(crosshair, (40, 40)), (mouse_pos - (20, 20)))
    ui_manager.draw_overlay(screen, player, wave_manager)
    draw_dialog_ui(screen, dialog_manager)


def camera_follow(target, cam, delta_time, speed=10, position_relative=True):
    target_relative_pos  = target - cam.position if position_relative else target
    camera_center        = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    center_offset        = target_relative_pos - camera_center
    distance_from_center = center_offset.length()
    if distance_from_center > _CAM_BORDER_RADIUS:
        excess_distance = distance_from_center - _CAM_BORDER_RADIUS
        camera.move(center_offset.normalize() * excess_distance * speed * delta_time)