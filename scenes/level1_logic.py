"""Lógica del flujo del nivel 1: cutscene, oleadas, puertas, contacto y muerte."""
import pygame

from core.collision.collider import Collider
from core.collision.collision_manager import CollisionManager
from core.collision.layers import LAYERS
from core.collision.quadtree import Rectangle
from character_scripts.character_controller import CharacterController
from runtime.round_manager import WaveManager, cleanup_dead_enemies
from scenes.level1_map import ACX, ACY, ARENA_HALF, CORRIDOR_H, NORTH_SQ, WALL_THICK

_CUTSCENE_ENEMY_SPAWNS = [
    (ACX - 500, ACY - 350), (ACX + 550, ACY - 400),
    (ACX - 450, ACY + 500), (ACX + 600, ACY + 450),
    (ACX + 50,  ACY - 750),
]


def update_enemies(scene, delta_time):
    """Actualiza enemigos iniciales (pre-wave) o los wave managers activos."""
    kills = 0

    if scene._wave_manager is not None:
        wm   = scene._wave_manager
        prev = len(wm.enemies)
        wm.update(delta_time)
        # wm puede haberse destruido en on_waves_complete durante el update
        if scene._wave_manager is not None:
            kills += prev - len(scene._wave_manager.enemies)
    else:
        for enemy in scene.enemies:
            if enemy.is_alive() and getattr(enemy, "brain", None):
                enemy.brain.update(delta_time)
            elif enemy.is_alive() and getattr(enemy, "_controller", None):
                to_player = scene.player.position - enemy.position
                if to_player.length() > 0:
                    enemy._controller.move(to_player.normalize(), delta_time)
                    enemy.rotation = to_player.angle_to(pygame.Vector2(0, -1))
                enemy._hit_flash_timer = max(0.0, getattr(enemy, "_hit_flash_timer", 0) - delta_time)
        prev = len(scene.enemies)
        cleanup_dead_enemies(scene.enemies)
        kills += prev - len(scene.enemies)

    if scene._wave_manager_north is not None:
        prev = len(scene._wave_manager_north.enemies)
        scene._wave_manager_north.update(delta_time)
        kills += prev - len(scene._wave_manager_north.enemies)

    if kills > 0 and scene.player:
        wave = 0
        if scene._wave_manager:
            wave = scene._wave_manager.current_wave
        elif scene._wave_manager_north:
            wave = scene._wave_manager_north.current_wave
        # Monedas por kill escalan con la oleada para que la tienda siga siendo relevante
        if wave <= 5:   coins_per_kill = 15
        elif wave <= 10: coins_per_kill = 25
        elif wave <= 15: coins_per_kill = 40
        elif wave <= 20: coins_per_kill = 60
        else:            coins_per_kill = 80
        scene.player.add_coins(kills * coins_per_kill)
        scene._total_kills += kills


def update_idle_timeout(scene, delta_time):
    """Elimina enemigos restantes si el jugador deja de disparar demasiado tiempo."""
    all_enemies = all_enemies_list(scene)
    if scene._idle_shot_timer >= 0:
        if all_enemies:
            scene._idle_shot_timer -= delta_time
            if scene._idle_shot_timer <= 0:
                for e in all_enemies:
                    e.take_damage(e.health)
                scene._idle_shot_timer = -1.0
        else:
            scene._idle_shot_timer = -1.0


def update_puddles(scene, delta_time):
    """Actualiza charcos tóxicos cuando no hay wave manager activo."""
    if scene._wave_manager is None and scene._wave_manager_north is None:
        for puddle in list(scene._toxic_puddles):
            puddle.update(delta_time, scene.player)
        scene._toxic_puddles[:] = [p for p in scene._toxic_puddles if p.is_alive]


def update_flow(scene, delta_time):
    """Gestiona las transiciones de estado del nivel: sala norte, oleadas, diálogos."""
    dialog_active = scene._dialog_manager and scene._dialog_manager.is_dialog_active

    if (not scene._north_room_entered
            and scene._north_room_rect
            and scene.player
            and scene._north_room_rect.collidepoint(scene.player.position)
            and not dialog_active):
        scene._north_room_entered = True
        seal_north_door(scene)
        from dialogs.audres_dialogs import create_audres_north_room_entry
        scene._dialog_manager.start_dialog(create_audres_north_room_entry())

    if (scene._north_room_entered
            and scene._wave_manager_north is None
            and not dialog_active):
        create_north_wave_manager(scene)

    if scene._enemies_spawned and not scene._shop_hint_triggered and not dialog_active:
        if not scene.enemies:
            if scene._wave_clear_timer < 0:
                scene._wave_clear_timer = 1.5
            else:
                scene._wave_clear_timer -= delta_time
                if scene._wave_clear_timer <= 0:
                    scene._shop_hint_triggered = True
                    scene._shop_unlocked       = True
                    scene._wave_clear_timer    = -1.0
                    from dialogs.audres_dialogs import create_audres_shop_hint
                    scene._dialog_manager.start_dialog(create_audres_shop_hint())
        else:
            scene._wave_clear_timer = -1.0

    if (scene._shop_hint_triggered
            and scene._wave_manager is None
            and scene._door is not None
            and not scene._door.is_open
            and not dialog_active):
        create_wave_manager(scene)

    # Desbloquea la puerta de salida cuando el jugador completa la oleada 25
    if (scene._wave_manager_north is not None
            and scene._wave_manager_north.current_wave >= 25
            and not scene._wave_manager_north.enemies
            and not scene._wave_manager_north._spawn_queue
            and not getattr(scene, "_zone2_complete", False)):
        scene._zone2_complete = True

    if (scene._wave2_clear_timer >= 0
            and not scene._wave2_clear_triggered
            and not dialog_active):
        scene._wave2_clear_timer -= delta_time
        if scene._wave2_clear_timer <= 0:
            scene._wave2_clear_timer    = -1.0
            scene._wave2_clear_triggered = True
            from dialogs.audres_dialogs import create_audres_wave2_clear
            scene._dialog_manager.start_dialog(create_audres_wave2_clear())


def update_cutscene(scene, delta_time):
    if scene._cutscene_phase == "walking":
        if scene.audres and scene._audres_walk_target:
            to = scene._audres_walk_target - scene.audres.position
            if to.length() > 8:
                scene.audres.position += to.normalize() * 300 * delta_time
                scene.audres.rotation  = to.angle_to(pygame.Vector2(0, -1)) + 180
            else:
                scene._cutscene_phase = "dialog"
                scene._dialog_manager.start_dialog(scene._audres_intro_tree)
    elif scene._cutscene_phase == "dialog":
        if not scene._dialog_manager.is_dialog_active:
            finish_cutscene(scene)


def finish_cutscene(scene):
    if scene.audres:
        scene.audres.destroy()
    scene.audres           = None
    scene._cutscene_active = False
    scene._cutscene_phase  = "idle"

    # Resincroniza el movimiento con el estado real del teclado para evitar
    # que teclas soltadas durante la cutscene dejen el personaje moviéndose
    if scene.director and scene.director._input_handler:
        keys = pygame.key.get_pressed()
        ih   = scene.director._input_handler
        ih.actions["move_x"] = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        ih.actions["move_y"] = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

    from character_scripts.enemy.enemy_types import InfectedCommon
    from character_scripts.enemy.enemy_brain import InfectedCommonBrain
    for pos in _CUTSCENE_ENEMY_SPAWNS:
        enemy = InfectedCommon(position=pos)
        ctrl  = CharacterController(enemy.speed, enemy)
        enemy._controller = ctrl
        enemy.brain       = InfectedCommonBrain(enemy, ctrl, scene.player)
        enemy._player_ref = scene.player
        enemy._contact_cd = 1.0
        enemy.no_reward   = True
        scene.enemies.append(enemy)
    scene._enemies_spawned = True


def create_wave_manager(scene):
    # Zona 1: exactamente 10 oleadas. Al terminar la oleada 10 deja de spawnear
    # pero la puerta norte no se abre sola — requiere 100k puntos
    scene._wave_manager = WaveManager(
        player=scene.player, total_waves=10,
        arena_center=(ACX, ACY), arena_half=ARENA_HALF,
        arena_mix=True, puddle_list=scene._toxic_puddles)
    scene._wave_manager.set_on_complete(lambda: on_waves_complete(scene))


def create_north_wave_manager(scene):
    # Zona 2: siempre arranca en oleada 11 independientemente de cuánto
    # se haya farmeado en zona 1, y escala infinito desde ahí
    north_cy = ACY - ARENA_HALF - CORRIDOR_H - NORTH_SQ
    scene._wave_manager_north = WaveManager(
        player=scene.player, total_waves=None,
        arena_center=(ACX, north_cy), arena_half=NORTH_SQ,
        arena_mix=True, puddle_list=scene._toxic_puddles,
        start_wave=11, hp_scale_per_wave=0.15)


def on_waves_complete(scene):
    # Oleada 10 completada — desbloquea la puerta norte para que el jugador pueda abrirla
    scene._zone1_complete = True
    if not scene._wave2_clear_triggered and not scene._going_level_complete:
        scene._wave2_clear_timer = 1.5


def on_north_door_open(scene):
    if scene._door_collider:
        cm = CollisionManager._active
        if cm:
            cm.static_qtree.remove(scene._door_collider)
        CollisionManager.static_colliders.discard(scene._door_collider)
        CollisionManager.static_dirty = True
        scene._door_collider = None

    if scene._wave_manager:
        for e in list(scene._wave_manager.enemies):
            e._player_ref = None
            e.take_damage(e.health)
        scene._wave_manager.enemies.clear()
        scene._wave_manager = None
    for e in list(scene.enemies):
        e._player_ref = None
        e.take_damage(e.health)
    scene.enemies.clear()
    scene._toxic_puddles.clear()


def on_exit_door_open(scene):
    if scene._exit_door_collider:
        cm = CollisionManager._active
        if cm:
            cm.static_qtree.remove(scene._exit_door_collider)
        CollisionManager.static_colliders.discard(scene._exit_door_collider)
        CollisionManager.static_dirty = True
        scene._exit_door_collider = None

    if scene._wave_manager_north is not None:
        for e in list(scene._wave_manager_north.enemies):
            e.take_damage(e.health)
        scene._wave_manager_north.enemies.clear()
    scene._wave_manager_north = None

    from dialogs.audres_dialogs import create_audres_exit_door
    if scene._dialog_manager:
        scene._dialog_manager.start_dialog(create_audres_exit_door())


def seal_north_door(scene):
    scene._north_room_sealed = True
    cx, cy = ACX, ACY
    h, t   = ARENA_HALF, WALL_THICK
    dw     = 240
    scene._north_seal_collider = Collider(
        object(), Rectangle(cx, cy - h - t // 2, t // 2, dw // 2),
        layer=LAYERS["terrain"], static=True)


def check_enemy_contact(scene, delta_time):
    hits = [
        h for h in scene.player.collider.check_collision(layers=[LAYERS["enemy"]])
        if hasattr(h, "owner") and h.owner is not None and h.owner.is_alive()
    ]
    for h in hits:
        enemy = h.owner
        cd = getattr(enemy, "_contact_cd", 0.0)
        if cd > 0:
            enemy._contact_cd = cd - delta_time
            continue
        scene.player.take_damage(10)
        enemy._contact_cd = 0.75
        break


def check_player_death(scene):
    if scene.player and not scene.player.is_alive():
        from scenes.game_over_scene import GameOverScene
        scene.director.replace(GameOverScene(stats={
            "kills": scene._total_kills,
            "coins": scene.player.coins,
        }))


def all_enemies_list(scene) -> list:
    out = list(scene._wave_manager.enemies if scene._wave_manager else scene.enemies)
    if scene._wave_manager_north:
        out += list(scene._wave_manager_north.enemies)
    return out