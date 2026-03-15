import pygame
from core.audio.audio_manager import AudioManager
from core.camera import Camera
from core.collision.collision_manager import CollisionManager
from core.collision.quadtree import Rectangle
from core.monolite_behaviour import MonoliteBehaviour
from core.scene import Scene
from core.status_effects import StatusEffect
from character_scripts.character_controller import CharacterController
from character_scripts.npc.npc import NPC
from character_scripts.player.player import Player
from dialogs.dialog_manager import DialogManager
from ui.dialog import draw_dialog_ui
from item.item_loader import ItemRegistry
from ui import ui_manager
from weapons.ranged.ranged import Ranged
from weapons.melee.melee import Melee
from weapons.melee.melee_types import TacticalKnife
from weapons.weapon_controller import WeaponController
import scenes.level1_map   as lmap
import scenes.level1_logic as logic


def _destroy_enemy(enemy):
    if hasattr(enemy, "audio_emitter") and enemy.audio_emitter:
        enemy.audio_emitter.destroy()
    if hasattr(enemy, "collider") and enemy.collider:
        CollisionManager.dynamic_colliders.discard(enemy.collider)
        CollisionManager.static_colliders.discard(enemy.collider)


class Level1Scene(Scene):

    def __init__(self):
        super().__init__()
        self._last_frame             = None
        self.player                  = None
        self.controller              = None
        self.camera                  = None
        self.weapon_controller       = None
        self.enemies: list           = []
        self._toxic_puddles: list    = []
        self._contact_dmg_cd         = 1.0
        self._dialog_manager         = None
        self.audres                  = None
        self._audres_intro_tree      = None
        self._cutscene_active        = False
        self._cutscene_phase         = "idle"
        self._audres_walk_target     = None
        self._wave_manager           = None
        self._wave_manager_north     = None
        self._zone1_complete         = False
        self._zone2_complete         = False
        self._enemies_spawned        = False
        self._shop_hint_triggered    = False
        self._shop_unlocked          = False
        self._wave_clear_timer       = -1.0
        self._wave2_clear_triggered  = False
        self._wave2_clear_timer      = -1.0
        self._going_level_complete   = False
        self._total_kills            = 0
        self._inventory_open         = False
        self._inv_right_click        = False
        self._aim_was_pressed        = False
        self._pending_weapon_item    = None
        self._pending_weapon_index   = -1
        self._door                   = None
        self._door_rect              = None
        self._door_collider          = None
        self._north_room_rect        = None
        self._corridor_rect          = None
        self._north_room_entered     = False
        self._north_room_sealed      = False
        self._north_seal_collider    = None
        self._exit_door              = None
        self._exit_door_rect         = None
        self._exit_door_collider     = None
        self._exit_room_rect         = None
        self._exit_corridor_rect     = None
        self._helicopter             = None
        self._helicopter_spawned     = False
        self._idle_shot_timer        = -1.0
        self._IDLE_SHOT_TIMEOUT      = 40.0
        self.crosshair               = pygame.image.load("assets/crosshair.png").convert_alpha()
        # Tiles visuales
        self._tile_floor             = None
        self._tile_wall_h            = None  # pared horizontal
        self._tile_wall_v            = None  # pared vertical (ud_wall rotado 90)
        self._tile_door              = None

    # ------------------------------------------------------------------
    # Tiles
    # ------------------------------------------------------------------
    def _load_tiles(self):
        def load(path, size):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)

        t = lmap.WALL_THICK  # 80px

        self._tile_floor  = load("assets/map/floor.png",        (128, 128))
        self._tile_wall_h = load("assets/map/up_down_wall.png", (128, t))
        # Pared vertical: mismo tile rotado 90 grados → t ancho, 128 alto
        base              = load("assets/map/up_down_wall.png", (128, t))
        self._tile_wall_v = pygame.transform.rotate(base, 90)
        self._tile_door   = load("assets/map/door.png",          (240, t))

    def _blit_h(self, screen, world_x, world_y, total_w):
        """Repite el tile horizontal, recortando el último si no cabe exacto."""
        tile = self._tile_wall_h
        tw   = tile.get_width()
        th   = tile.get_height()
        cx   = int(self.camera.position.x)
        cy   = int(self.camera.position.y)
        sw, sh = screen.get_size()
        x = world_x
        while x < world_x + total_w:
            sx = x - cx
            sy = world_y - cy
            remaining = (world_y + total_w) - x  # unused for h, use width remaining
            rem_w = min(tw, (world_x + total_w) - x)
            if -tw < sx < sw and -th < sy < sh:
                if rem_w < tw:
                    screen.blit(tile.subsurface(pygame.Rect(0, 0, rem_w, th)), (sx, sy))
                else:
                    screen.blit(tile, (sx, sy))
            x += tw

    def _blit_v(self, screen, world_x, world_y, total_h):
        """Repite el tile vertical, recortando el último si no cabe exacto."""
        tile = self._tile_wall_v
        tw   = tile.get_width()
        th   = tile.get_height()
        cx   = int(self.camera.position.x)
        cy   = int(self.camera.position.y)
        sw, sh = screen.get_size()
        y = world_y
        while y < world_y + total_h:
            sx = world_x - cx
            sy = y - cy
            rem_h = min(th, (world_y + total_h) - y)
            if -tw < sx < sw and -th < sy < sh:
                if rem_h < th:
                    screen.blit(tile.subsurface(pygame.Rect(0, 0, tw, rem_h)), (sx, sy))
                else:
                    screen.blit(tile, (sx, sy))
            y += th

    def _blit_floor(self, screen, world_x, world_y, w, h):
        tile   = self._tile_floor
        tw, th = tile.get_width(), tile.get_height()
        cx     = int(self.camera.position.x)
        cy     = int(self.camera.position.y)
        sw, sh = screen.get_size()
        y = world_y
        while y < world_y + h:
            x = world_x
            while x < world_x + w:
                sx, sy = x - cx, y - cy
                if -tw < sx < sw and -th < sy < sh:
                    screen.blit(tile, (sx, sy))
                x += tw
            y += th

    def _blit_once(self, screen, tile, world_cx, world_cy):
        cx = int(self.camera.position.x)
        cy = int(self.camera.position.y)
        screen.blit(tile, (world_cx - tile.get_width() // 2 - cx,
                            world_cy - tile.get_height() // 2 - cy))

    def _draw_map_tiles(self, screen):
        if self._tile_floor is None:
            return

        cx, cy  = lmap.ACX, lmap.ACY
        h       = lmap.ARENA_HALF
        t       = lmap.WALL_THICK
        dw      = 240
        cw      = lmap.CORRIDOR_W
        ch      = lmap.CORRIDOR_H
        nsq     = lmap.NORTH_SQ
        esq     = lmap.EXIT_SQ_HALF
        ecw     = lmap.EXIT_CORRIDOR_W
        ech     = lmap.EXIT_CORRIDOR_H

        # Posiciones clave
        arena_l  = cx - h
        arena_r  = cx + h
        arena_t  = cy - h
        arena_b  = cy + h
        north_b  = arena_t - ch          # base del pasillo norte
        north_t  = north_b - nsq * 2    # tope sala norte
        exit_b   = north_t - ech         # base del pasillo salida
        exit_t   = exit_b - esq * 2     # tope sala salida

        # ── Suelos ──────────────────────────────────────────────────────
        self._blit_floor(screen, arena_l,       arena_t,  h * 2,   h * 2)
        self._blit_floor(screen, cx - cw // 2,  north_b,  cw,      ch)
        self._blit_floor(screen, cx - nsq,      north_t,  nsq * 2, nsq * 2)
        self._blit_floor(screen, cx - ecw // 2, exit_b,   ecw,     ech)
        self._blit_floor(screen, cx - esq,      exit_t,   esq * 2, esq * 2)

        # ── Paredes arena ───────────────────────────────────────────────
        # inferior (esquinas incluidas)
        self._blit_h(screen, arena_l - t,   arena_b,    h * 2 + t * 2)
        # superior izq y der (hueco puerta norte en centro)
        self._blit_h(screen, arena_l - t,   arena_t - t, h - dw // 2 + t)
        self._blit_h(screen, cx + dw // 2,  arena_t - t, h - dw // 2 + t)
        # laterales (sin esquinas — las cubre la pared h)
        self._blit_v(screen, arena_l - t,   arena_t,    h * 2)
        self._blit_v(screen, arena_r,       arena_t,    h * 2)

        # ── Paredes pasillo norte ───────────────────────────────────────
        self._blit_v(screen, cx - cw // 2 - t, north_b, ch)
        self._blit_v(screen, cx + cw // 2,      north_b, ch)

        # ── Paredes sala norte ──────────────────────────────────────────
        # inferior izq y der (flancos del hueco hacia pasillo, con esquinas)
        self._blit_h(screen, cx - nsq - t,    arena_t - ch, nsq - cw // 2 + t)
        self._blit_h(screen, cx + cw // 2,    arena_t - ch, nsq - cw // 2 + t)
        # laterales
        self._blit_v(screen, cx - nsq - t,  north_t, nsq * 2)
        self._blit_v(screen, cx + nsq,      north_t, nsq * 2)
        # superior izq y der (hueco puerta salida, con esquinas)
        self._blit_h(screen, cx - nsq - t,  north_t - t, nsq - dw // 2 + t)
        self._blit_h(screen, cx + dw // 2,  north_t - t, nsq - dw // 2 + t)

        # ── Paredes pasillo salida ──────────────────────────────────────
        self._blit_v(screen, cx - ecw // 2 - t, exit_b, ech)
        self._blit_v(screen, cx + ecw // 2,      exit_b, ech)

        # ── Paredes sala salida ─────────────────────────────────────────
        # inferior (con esquinas)
        self._blit_h(screen, cx - esq - t, exit_b - ech, esq * 2 + t * 2)
        # laterales
        self._blit_v(screen, cx - esq - t, exit_t, esq * 2)
        self._blit_v(screen, cx + esq,     exit_t, esq * 2)
        # superior (con esquinas)
        self._blit_h(screen, cx - esq - t, exit_t - t, esq * 2 + t * 2)

        # ── Puertas (siempre al final para quedar encima) ───────────────
        if self._tile_door and (not self._door or not self._door.is_open):
            self._blit_once(screen, self._tile_door, cx, arena_t - t // 2)
        if self._tile_door and (not self._exit_door or not self._exit_door.is_open):
            self._blit_once(screen, self._tile_door, cx, north_t - t // 2)

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    def on_enter(self):
        MonoliteBehaviour.time_scale = 1.0
        pygame.mouse.set_visible(False)
        if self.director and self.director._input_handler:
            ih = self.director._input_handler
            ih.actions["move_x"] = 0
            ih.actions["move_y"] = 0
        if self.player is None:
            self._build_level()

    def on_exit(self):
        MonoliteBehaviour.time_scale = 0.0
        self._teardown_level()

    def on_pause(self):
        MonoliteBehaviour.time_scale = 0.0

    def on_resume(self):
        MonoliteBehaviour.time_scale = 1.0
        pygame.mouse.set_visible(False)

    def _build_level(self):
        CollisionManager.dynamic_colliders.clear()
        CollisionManager.static_colliders.clear()
        if CollisionManager._active is not None:
            CollisionManager._active.dynamic_qtree.clear()
            CollisionManager._active.static_qtree.clear()
            CollisionManager.static_dirty = True
        else:
            CollisionManager(Rectangle(-12000, -12000, 24000, 24000))

        if AudioManager._instance is None:
            AudioManager._instance = AudioManager()
        if not ItemRegistry._items:
            ItemRegistry()
        if not ItemRegistry._items:
            ItemRegistry.load("assets/items/item_data.json")

        self.player     = Player("assets/player/survivor-idle_rifle_0.png",
                                 (lmap.ACX, lmap.ACY))
        self.controller = CharacterController(250, self.player)
        AudioManager.instance().set_listener(self.player.audio_listener)

        from weapons.ranged.ranged_types import AK47
        weapon = AK47()
        self.player.inventory.add_weapon(self.player, weapon, "primary")
        self.player.inventory.add_weapon(self.player, TacticalKnife(), "secondary")
        if hasattr(weapon, "emitter"):
            weapon.emitter.enabled = False

        from item.item_instance import ItemInstance
        for item_id in ["stim_patch", "stim_patch", "health_injector",
                        "adrenaline_shot", "rad_suppressor"]:
            try:
                self.player.inventory.add_item(ItemInstance(ItemRegistry.get(item_id)))
            except Exception:
                pass

        self.camera          = Camera()
        self._toxic_puddles  = []
        self.enemies         = []
        self._contact_dmg_cd = 1.0

        ads_effect = StatusEffect("assets/effects/ads", "Aiming Down Sights", {"speed": -30}, -1)
        self.weapon_controller = WeaponController(self.player, self.camera, ads_effect)

        (self._north_room_rect,
         self._corridor_rect,
         self._exit_corridor_rect,
         self._exit_room_rect) = lmap.build_room_rects()

        # Colliders desde Tiled
        from map.map_loader import MapLoader
        map_json  = MapLoader.load_map("assets/map/level1.tmj")
        door_cols = MapLoader.load_colliders_from_json(
            map_json, offset_x=lmap.ACX, offset_y=lmap.ACY)
        self._door_collider      = door_cols.get('door_north')
        self._exit_door_collider = door_cols.get('door_exit')

        lmap.build_interactables(self)
        self._load_tiles()

        cx, cy = lmap.ACX, lmap.ACY
        h      = lmap.ARENA_HALF

        from dialogs.audres_dialogs import create_audres_intro
        self._audres_intro_tree = create_audres_intro()
        self.audres = NPC(
            name="AUDReS-01",
            position=(cx, cy - h + 100),
            dialog_tree=None,
            sprite_path="assets/characters/audres/sprite_topdown.jpg",
            scale=0.16)

        self._dialog_manager = DialogManager()
        self._dialog_manager.end_dialog()

        self._cutscene_active    = True
        self._cutscene_phase     = "walking"
        self._audres_walk_target = pygame.Vector2(cx, cy - 200)

    def _teardown_level(self):
        if self.player:
            inv = self.player.inventory
            for slot in ("primary", "secondary"):
                w = inv.get_weapon(slot)
                if w is not None:
                    emitter = getattr(w, "emitter", None) or getattr(w, "impact_emitter", None)
                    if emitter is not None:
                        emitter.destroy()
                    if hasattr(w, "destroy"):
                        w.destroy()
            if hasattr(inv, "drop_manager") and inv.drop_manager is not None:
                inv.drop_manager.destroy()
            if hasattr(self.player, "audio_emitter") and self.player.audio_emitter:
                self.player.audio_emitter.destroy()
            if hasattr(self.player, "audio_listener") and self.player.audio_listener:
                self.player.audio_listener.destroy()

        for mgr in [self._wave_manager, self._wave_manager_north]:
            if mgr is not None:
                for e in list(mgr.enemies):
                    _destroy_enemy(e)
        for e in list(self.enemies):
            _destroy_enemy(e)

        CollisionManager.dynamic_colliders.clear()
        CollisionManager.static_colliders.clear()
        if CollisionManager._active is not None:
            CollisionManager._active.dynamic_qtree.clear()
            CollisionManager._active.static_qtree.clear()

        self.player = self.controller = self.weapon_controller = self.audres = None
        self._cutscene_active        = False
        self._cutscene_phase         = "idle"
        self._audres_walk_target     = None
        self._enemies_spawned        = False
        self._shop_hint_triggered    = False
        self._shop_unlocked          = False
        self._wave_clear_timer       = -1.0
        self._wave_manager           = None
        self._wave_manager_north     = None
        self._toxic_puddles          = []
        self._wave2_clear_triggered  = False
        self._wave2_clear_timer      = -1.0
        self._going_level_complete   = False
        self._total_kills            = 0
        self._contact_dmg_cd         = 1.0
        self._pending_weapon_item    = None
        self._pending_weapon_index   = -1
        self._tile_floor             = None
        self._tile_wall_h            = None
        self._tile_wall_v            = None
        self._tile_door              = None

        from map.interactables.interaction_manager import InteractionManager
        if self._door:
            InteractionManager().unregister(self._door)
        self._door = self._door_collider = None

        if self._exit_door:
            InteractionManager().unregister(self._exit_door)
        self._exit_door          = None
        self._exit_door_collider = None
        self._exit_door_rect     = None
        self._exit_room_rect     = None
        self._exit_corridor_rect = None

        if self._helicopter:
            self._helicopter._unregister()
        self._helicopter         = None
        self._helicopter_spawned = False
        self._idle_shot_timer    = -1.0
        self._north_room_entered  = False
        self._north_room_sealed   = False
        self._north_seal_collider = None

        if self._dialog_manager:
            self._dialog_manager.end_dialog()
        self._dialog_manager = None

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def handle_events(self, input_handler):
        aim_now = input_handler.actions.get("aim", False)
        self._inv_right_click = aim_now and not self._aim_was_pressed
        self._aim_was_pressed = aim_now

        if self._pending_weapon_item is not None:
            keys = input_handler.keys_just_pressed
            if pygame.K_1 in keys:
                self._handle_weapon_assign("primary")
            elif pygame.K_2 in keys:
                self._handle_weapon_assign("secondary")
            elif pygame.K_ESCAPE in keys or input_handler.actions.get("inventory"):
                self._pending_weapon_item  = None
                self._pending_weapon_index = -1
                input_handler.actions["inventory"] = False
            return

        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

        if self._cutscene_active:
            if self._dialog_manager and self._dialog_manager.is_dialog_active:
                self._dialog_manager.handle_input(
                    pygame.key.get_pressed(), input_handler.keys_just_pressed)
            for key in input_handler.actions:
                val = input_handler.actions[key]
                input_handler.actions[key] = 0 if isinstance(val, (int, float)) else False
            return

        if self._dialog_manager and self._dialog_manager.is_dialog_active:
            if input_handler.actions.get("shop"):
                input_handler.actions["shop"] = False
                if self._shop_unlocked:
                    from scenes.shop_scene import ShopScene
                    self.director.push(ShopScene(self, self.player))
                return
            self._dialog_manager.handle_input(
                pygame.key.get_pressed(), input_handler.keys_just_pressed)
            return

        if input_handler.actions.get("shop"):
            input_handler.actions["shop"] = False
            if self._shop_unlocked:
                from scenes.shop_scene import ShopScene
                self.director.push(ShopScene(self, self.player))
            return

        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().check_interaction(self.player, input_handler)

        if input_handler.actions.get("inventory"):
            input_handler.actions["inventory"] = False
            self._inventory_open = not self._inventory_open
            pygame.mouse.set_visible(self._inventory_open)
            return

        if self._inventory_open:
            from ui.inventory_menu import (get_item_slot_rect, get_weapon_inv_slot_rect,
                                           _weapons_in_inv, _consumables)
            mouse_pos = input_handler.mouse_position
            if input_handler.actions.get("click_drop"):
                input_handler.actions["click_drop"] = False
                input_handler.actions["attack"]     = False
                weapons = _weapons_in_inv(self.player.inventory)
                for i, item in enumerate(weapons):
                    if get_weapon_inv_slot_rect(i).collidepoint(mouse_pos):
                        self._pending_weapon_item  = item
                        self._pending_weapon_index = self.player.inventory.items.index(item)
                        return
                consumables = _consumables(self.player.inventory)
                for i, item in enumerate(consumables):
                    if get_item_slot_rect(i).collidepoint(mouse_pos):
                        real_idx = self.player.inventory.items.index(item)
                        self.player.inventory.use_consumable_hotkey(real_idx, self.player)
                        break
            if self._inv_right_click:
                self._inv_right_click = False
                self.player.inventory.click_drop_item(mouse_pos)
            return

        if input_handler.actions["hotkey_slot"] >= 0:
            slot = input_handler.actions["hotkey_slot"]
            self.player.inventory.select_item(slot)
            self.player.inventory.use_consumable_hotkey(slot, self.player)
        if input_handler.actions["use_item"]:
            self.player.inventory.use_selected_item(self.player)
        if input_handler.actions["dash"]:
            self.player.try_dash(self.weapon_controller)

    def _handle_weapon_assign(self, slot: str):
        self.player.inventory.equip_weapon_from_item(
            self.player, self._pending_weapon_item, self._pending_weapon_index, slot)
        self._pending_weapon_item  = None
        self._pending_weapon_index = -1

    # ------------------------------------------------------------------
    # Update / render
    # ------------------------------------------------------------------
    def update(self, delta_time):
        from core.audio.music_manager import MusicManager
        MusicManager.instance().set_category("idle")

        if self._cutscene_active:
            logic.update_cutscene(self, delta_time)
            return

        dialog_active = self._dialog_manager and self._dialog_manager.is_dialog_active
        MonoliteBehaviour.time_scale = 0.0 if dialog_active else 1.0

        if dialog_active or self._inventory_open:
            return

        logic.update_enemies(self, delta_time)
        logic.update_idle_timeout(self, delta_time)
        logic.update_puddles(self, delta_time)

        if self.player:
            self.player.update(delta_time)
            logic.check_enemy_contact(self, delta_time)
            logic.check_player_death(self)

        logic.update_flow(self, delta_time)

    def render(self, screen):
        im         = self.director._input_handler
        delta_time = self.director.clock.get_time() / 1000.0

        screen.fill(lmap._BG_COLOR)
        self._draw_map_tiles(screen)

        mouse_pos     = pygame.Vector2(pygame.mouse.get_pos())
        active_weapon = self.player.inventory.get_weapon(
            self.player.inventory.active_weapon_slot)

        if self.weapon_controller:
            self.weapon_controller.setup_emitter(screen)

        if active_weapon and isinstance(active_weapon, Ranged):
            emitter = getattr(active_weapon, "emitter", None)
            if emitter is not None:
                emitter.surface = screen
                emitter.camera  = self.camera
                emitter.update()

        dialog_active = self._dialog_manager and self._dialog_manager.is_dialog_active
        movement = (pygame.Vector2(0, 0) if (self._cutscene_active or dialog_active)
                    else pygame.Vector2(im.actions["move_x"], im.actions["move_y"]))

        self.controller.speed = self.player.get_stat("speed")
        if not self._inventory_open:
            self.controller.move(movement, delta_time)
            if movement.length() > 0:
                self.player._dash_direction = pygame.Vector2(movement)

        if (not self._cutscene_active
                and not dialog_active
                and not self._inventory_open
                and self.weapon_controller):
            shot_fired = self.weapon_controller.update(im, delta_time, mouse_pos)
            if shot_fired:
                self._idle_shot_timer = self._IDLE_SHOT_TIMEOUT

        lmap.camera_follow(self.camera, self.player.position, delta_time)

        all_enemies = logic.all_enemies_list(self)

        from character_scripts.enemy.enemy_types import ShooterEnemy
        for enemy in all_enemies:
            if isinstance(enemy, ShooterEnemy):
                enemy.draw_zone(screen, self.camera)

        for puddle in self._toxic_puddles:
            puddle.draw(screen, self.camera)
        if self._helicopter:
            self._helicopter.draw(screen, self.camera)

        entity_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for enemy in all_enemies:
            enemy.draw(entity_surf, self.camera)
            if getattr(enemy, "_hit_flash_timer", 0) > 0:
                sp = enemy.position - self.camera.position
                fr = enemy._render_asset.get_rect(center=sp)
                fs = pygame.Surface(fr.size, pygame.SRCALPHA)
                fs.fill((255, 30, 30, 180))
                entity_surf.blit(fs, fr)
        screen.blit(entity_surf, (0, 0))

        for enemy in all_enemies:
            if isinstance(enemy, ShooterEnemy):
                enemy.draw_bullets(screen, self.camera)

        if self.player and self.player.inventory.drop_manager:
            self.player.inventory.drop_manager.draw(screen, self.camera)
        if self.audres:
            self.audres.draw(screen, self.camera)
        self.player.draw(screen, self.camera)

        if isinstance(active_weapon, Ranged) and active_weapon.is_reloading():
            lmap.draw_reload_bar(screen, self.player, self.camera, active_weapon)
        if isinstance(active_weapon, Melee):
            active_weapon.draw_attack_cone(screen, self.camera)

        if self.weapon_controller and not self._cutscene_active:
            player_screen_pos = self.player.position - self.camera.position
            self.weapon_controller.draw_trail(screen, player_screen_pos, active_weapon)

        screen.blit(pygame.transform.scale(self.crosshair, (40, 40)), (mouse_pos - (20, 20)))

        hud_wm = self._wave_manager_north or self._wave_manager
        ui_manager.draw_overlay(screen, self.player, wave_manager=hud_wm, delta_time=delta_time)

        if self._dialog_manager:
            draw_dialog_ui(screen, self._dialog_manager)

        if self._inventory_open:
            from ui.inventory_menu import draw_inventory_screen
            draw_inventory_screen(screen, self.player, mouse_pos,
                                  pending_weapon_item=self._pending_weapon_item)
        else:
            if self.director._input_handler:
                self.director._input_handler.actions["click_drop"] = False

        self._last_frame = screen.copy()

    def get_last_frame(self):
        return self._last_frame