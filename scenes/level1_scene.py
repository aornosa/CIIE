"""
scenes/level1_scene.py
-----------------------
CAMBIOS:
  • _contact_dmg_cd arranca en 1.0 (grace period) — evita daño invisible al spawnear
  • _check_enemy_contact: guard hasattr(h, "owner") para colisionadores sin owner
  • Nuevo estado _pending_weapon_item: cuando el jugador clica un WeaponItem en el
    inventario se muestra el overlay de selección de slot (Primario/Secundario/Cancelar)
  • Al confirmar slot, el WeaponItem se consume, el arma se equipa y la anterior
    se tira al suelo
  • Helicóptero de extracción en sala norte — interactuar con [E] lleva a VictoryScene
  • Puerta de salida norte con diálogo de Audrey al abrirse
  • player.score arranca en 4000
"""
import pygame

from core.audio.audio_manager import AudioManager
from core.camera import Camera
from core.collision.collider import Collider
from core.collision.collision_manager import CollisionManager
from core.collision.layers import LAYERS
from core.collision.quadtree import Rectangle
from core.monolite_behaviour import MonoliteBehaviour
from core.scene import Scene
from core.status_effects import StatusEffect
from character_scripts.character_controller import CharacterController
from character_scripts.enemy.enemy_base import Enemy
from character_scripts.npc.npc import NPC
from character_scripts.player.player import Player
from dialogs.dialog_manager import DialogManager
from ui.dialog import draw_dialog_ui
from item.item_loader import ItemRegistry
from runtime.round_manager import WaveManager, cleanup_dead_enemies
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, _CAM_BORDER_RADIUS
from ui import ui_manager
from weapons.ranged.ranged import Ranged
from weapons.melee.melee import Melee
from weapons.melee.melee_types import TacticalKnife
from weapons.weapon_controller import WeaponController


def _destroy_enemy(enemy):
    if hasattr(enemy, "audio_emitter") and enemy.audio_emitter:
        enemy.audio_emitter.destroy()
    if hasattr(enemy, "collider") and enemy.collider:
        CollisionManager.dynamic_colliders.discard(enemy.collider)
        CollisionManager.static_colliders.discard(enemy.collider)


_BG_COLOR    = (20, 20, 28)
_FLOOR_COLOR = (45, 45, 55)
_WALL_COLOR  = (110, 90, 70)

_ARENA_HALF = 1000
_WALL_THICK = 80
_ACX        = SCREEN_WIDTH  // 2
_ACY        = SCREEN_HEIGHT // 2

_CUTSCENE_ENEMY_SPAWNS = [
    (_ACX - 500, _ACY - 350), (_ACX + 550, _ACY - 400),
    (_ACX - 450, _ACY + 500), (_ACX + 600, _ACY + 450),
    (_ACX + 50,  _ACY - 750),
]
_ENEMY_SPEED = 110


class Level1Scene(Scene):

    def __init__(self):
        super().__init__()
        self._last_frame   = None
        self.player        = None
        self.controller    = None
        self.camera        = None
        self.weapon_controller: WeaponController | None = None
        self.enemies: list = []
        self._toxic_puddles: list = []

        # FIX: 1-second grace period — ningún enemigo hace daño de contacto
        #      en el primer segundo de vida (evita daño invisible al spawnear)
        self._contact_dmg_cd = 1.0

        self._dialog_manager    = None
        self.audres             = None
        self._audres_intro_tree = None
        self._cutscene_active   = False
        self._cutscene_phase    = "idle"
        self._audres_walk_target = None

        self._wave_manager: WaveManager | None       = None
        self._wave_manager_north: WaveManager | None = None

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

        # Estado del overlay de asignación de slot de arma
        self._pending_weapon_item    = None   # WeaponItem esperando asignación
        self._pending_weapon_index   = -1     # índice en inventory.items

        self._door             = None
        self._north_room_rect  = None
        self._corridor_rect    = None
        self._door_rect        = None
        self._door_collider    = None
        self._corridor_weapon  = None
        self._north_room_entered  = False
        self._north_room_sealed   = False
        self._north_seal_collider = None

        # Puerta de salida norte (acceso al helicóptero) y helicóptero
        self._exit_door             = None
        self._exit_door_rect        = None
        self._exit_door_collider    = None
        self._helicopter            = None  # HelicopterInteractable
        self._helicopter_spawned    = False

        self.crosshair = pygame.image.load("assets/crosshair.png").convert_alpha()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

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

    # ── Build / teardown ──────────────────────────────────────────────────────

    def _build_level(self):
        CollisionManager.dynamic_colliders.clear()
        CollisionManager.static_colliders.clear()
        if CollisionManager._active is not None:
            CollisionManager._active.dynamic_qtree.clear()
            CollisionManager._active.static_qtree.clear()
            CollisionManager.static_dirty = True
        else:
            CollisionManager(Rectangle(-4000, -4000, 8000, 8000))

        if AudioManager._instance is None:
            AudioManager._instance = AudioManager()
        if not ItemRegistry._items:
            ItemRegistry()
        if not ItemRegistry._items:
            ItemRegistry.load("assets/items/item_data.json")

        self.player = Player("assets/player/survivor-idle_rifle_0.png", (_ACX, _ACY))
        self.controller = CharacterController(250, self.player)
        AudioManager.instance().set_listener(self.player.audio_listener)

        weapon = Ranged("assets/weapons/AK47.png", "AK-47", 60, 1500,
                        "7.62", 45, 0.15, 0.6, muzzle_offset=(35, 15))
        self.player.inventory.add_weapon(self.player, weapon, "primary")
        self.player.inventory.add_weapon(self.player, TacticalKnife(), "secondary")

        from item.item_instance import ItemInstance
        for item_id in ["stim_patch", "stim_patch", "health_injector",
                        "adrenaline_shot", "rad_suppressor",
                        "ammo_clip_762", "ammo_clip_762", "ammo_clip_12gauge"]:
            try:
                self.player.inventory.add_item(ItemInstance(ItemRegistry.get(item_id)))
            except Exception as e:
                print(f"[INVENTORY] Item no encontrado '{item_id}': {e}")

        self.camera = Camera()
        self._toxic_puddles = []
        self.enemies = []
        # FIX: reset grace period every new level
        self._contact_dmg_cd = 1.0

        ads_effect = StatusEffect("assets/effects/ads", "Aiming Down Sights", {"speed": -30}, -1)
        self.weapon_controller = WeaponController(self.player, self.camera, ads_effect)

        self._build_walls()
        self._build_doors()

        from item.item_drop_manager import DroppedWeapon
        from weapons.ranged.ranged_types import SPAS12
        self._corridor_weapon = DroppedWeapon(
            SPAS12(), (_ACX, _ACY - _ARENA_HALF - 400), slot="secondary")

        from dialogs.audres_dialogs import create_audres_intro
        self._audres_intro_tree = create_audres_intro()
        self.audres = NPC(
            name="AUDReS-01", position=(_ACX, _ACY - _ARENA_HALF + 100),
            dialog_tree=None, sprite_path="assets/characters/audres/sprite_topdown.jpg",
            scale=0.16)
        self._dialog_manager = DialogManager()
        self._dialog_manager.active_dialog          = None
        self._dialog_manager.is_dialog_active        = False
        self._dialog_manager.selected_option         = 0
        self._dialog_manager._cached_dialog_surface  = None
        self._dialog_manager._cached_node_id         = None
        self._dialog_manager._needs_redraw           = True

        self._cutscene_active    = True
        self._cutscene_phase     = "walking"
        self._audres_walk_target = pygame.Vector2(_ACX, _ACY - 200)

    def _build_walls(self):
        cx, cy = _ACX, _ACY
        h, t   = _ARENA_HALF, _WALL_THICK
        door_w = 240
        corridor_w, corridor_h = 240, 800
        north_sq = int(_ARENA_HALF * 1.2)

        self._north_room_rect = pygame.Rect(
            cx - north_sq, cy - h - corridor_h - north_sq * 2,
            north_sq * 2, north_sq * 2)
        self._corridor_rect = pygame.Rect(
            cx - corridor_w // 2, cy - h - corridor_h, corridor_w, corridor_h)

        for wx, wy, wh, ww in [
            (cx - (h + door_w // 2) / 2, cy - h - t // 2, t // 2, (h - door_w // 2) / 2),
            (cx + (h + door_w // 2) / 2, cy - h - t // 2, t // 2, (h - door_w // 2) / 2),
            (cx - corridor_w // 2 - t // 2, cy - h - corridor_h // 2, corridor_h // 2, t // 2),
            (cx + corridor_w // 2 + t // 2, cy - h - corridor_h // 2, corridor_h // 2, t // 2),
            (cx - (north_sq + corridor_w // 2) / 2, cy - h - corridor_h - t // 2, t // 2, (north_sq - corridor_w // 2) / 2),
            (cx + (north_sq + corridor_w // 2) / 2, cy - h - corridor_h - t // 2, t // 2, (north_sq - corridor_w // 2) / 2),
            (cx - north_sq - t // 2, cy - h - corridor_h - north_sq, north_sq, t // 2),
            (cx + north_sq + t // 2, cy - h - corridor_h - north_sq, north_sq, t // 2),
            (cx, cy - h - corridor_h - north_sq * 2 - t // 2, t // 2, north_sq + t),
            (cx, cy + h + t // 2, t // 2, h + t),
            (cx - h - t // 2, cy, h, t // 2),
            (cx + h + t // 2, cy, h, t // 2),
        ]:
            Collider(object(), Rectangle(wx, wy, wh, ww), layer=LAYERS["terrain"], static=True)

    def _build_doors(self):
        from map.interactables.door import Door
        cx, cy = _ACX, _ACY
        h, t   = _ARENA_HALF, _WALL_THICK
        door_w = 240
        # Puerta norte (acceso al pasillo)
        dx, dy = cx, cy - h - t // 2
        self._door = Door("Puerta Norte", (dx, dy), 1000, self._on_north_door_open)
        self._door_rect = pygame.Rect(dx - door_w // 2, dy - t // 2, door_w, t)
        self._door_collider = Collider(
            object(), Rectangle(dx, dy, t // 2, door_w // 2),
            layer=LAYERS["terrain"], static=True)
        # Puerta de salida norte (hacia el helicóptero) — empieza cerrada
        corridor_h = 800
        north_sq   = int(_ARENA_HALF * 1.2)
        ex, ey     = cx, cy - h - corridor_h - north_sq * 2 - t // 2
        self._exit_door = Door("Salida Norte", (ex, ey), 5000, self._on_exit_door_open)
        self._exit_door_rect = pygame.Rect(ex - door_w // 2, ey - t // 2, door_w, t)
        self._exit_door_collider = Collider(
            object(), Rectangle(ex, ey, t // 2, door_w // 2),
            layer=LAYERS["terrain"], static=True)

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
        self._cutscene_active = False
        self._cutscene_phase  = "idle"
        self._audres_walk_target = None
        self._enemies_spawned = self._shop_hint_triggered = self._shop_unlocked = False
        self._wave_clear_timer = -1.0
        self._wave_manager = self._wave_manager_north = None
        self._toxic_puddles = []
        self._wave2_clear_triggered = False
        self._wave2_clear_timer = -1.0
        self._going_level_complete = False
        self._total_kills = 0
        self._contact_dmg_cd = 1.0
        self._pending_weapon_item  = None
        self._pending_weapon_index = -1
        if self._door:
            from map.interactables.interaction_manager import InteractionManager
            InteractionManager().unregister(self._door)
        self._door = self._door_collider = None
        if self._exit_door:
            from map.interactables.interaction_manager import InteractionManager
            InteractionManager().unregister(self._exit_door)
        self._exit_door = self._exit_door_collider = self._exit_door_rect = None
        if self._helicopter:
            self._helicopter._unregister()
        self._helicopter = None
        self._helicopter_spawned = False
        self._north_room_entered = self._north_room_sealed = False
        self._north_seal_collider = None
        if self._corridor_weapon:
            self._corridor_weapon._unregister()
            self._corridor_weapon = None
        if self._dialog_manager:
            self._dialog_manager.end_dialog()
        self._dialog_manager = None

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_events(self, input_handler):
        aim_now = input_handler.actions.get("aim", False)
        self._inv_right_click = aim_now and not self._aim_was_pressed
        self._aim_was_pressed = aim_now

        # ── Overlay de asignación de arma ──────────────────────────────────────
        # Selección por teclado: 1 → primario, 2 → secundario, ESC → cancelar
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
            else:
                print("[SHOP] La tienda aún no está disponible.")
            return

        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().check_interaction(self.player, input_handler)

        if input_handler.actions.get("inventory"):
            input_handler.actions["inventory"] = False
            self._inventory_open = not self._inventory_open
            return

        if self._inventory_open:
            from ui.inventory_menu import get_item_slot_rect
            mouse_pos = input_handler.mouse_position

            if input_handler.actions.get("click_drop"):
                input_handler.actions["click_drop"] = False
                input_handler.actions["attack"]     = False
                # Detectar si se hizo clic en un WeaponItem
                for i, item in enumerate(self.player.inventory.items):
                    if (getattr(item, "type", None) == "weapon_item"
                            and get_item_slot_rect(i).collidepoint(mouse_pos)):
                        # Activar overlay de asignación
                        self._pending_weapon_item  = item
                        self._pending_weapon_index = i
                        return
                # Clic normal → usar consumible
                for i in range(len(self.player.inventory.items)):
                    if get_item_slot_rect(i).collidepoint(mouse_pos):
                        self.player.inventory.use_consumable_hotkey(i, self.player)
                        break

            if self._inv_right_click:
                self._inv_right_click = False
                self.player.inventory.click_drop_item(mouse_pos)
            return

        if input_handler.actions["hotkey_slot"] >= 0:
            slot = input_handler.actions["hotkey_slot"]
            self.player.inventory.select_item(slot)
            # Usar el consumible directamente al pulsar la tecla numérica
            self.player.inventory.use_consumable_hotkey(slot, self.player)
        if input_handler.actions["use_item"]:
            self.player.inventory.use_selected_item(self.player)

    def _handle_weapon_assign(self, slot: str):
        """Equipa el weapon_item pendiente en el slot dado ('primary'/'secondary')."""
        weapon_item = self._pending_weapon_item
        idx         = self._pending_weapon_index

        weapon = weapon_item.weapon
        weapon.parent        = self.player
        weapon.audio_emitter = self.player.audio_emitter

        # Mover el arma actual al inventario (o al suelo si está lleno)
        old = self.player.inventory.get_weapon(slot)
        if old is not None:
            from item.weapon_item import WeaponItem as WI
            old_wi = WI(old)
            if not self.player.inventory.add_item(old_wi):
                self.player.inventory.drop_weapon(slot)
            else:
                if slot == "primary":
                    self.player.inventory.primary_weapon = None
                else:
                    self.player.inventory.secondary_weapon = None

        # Equipar nueva arma
        if slot == "primary":
            self.player.inventory.primary_weapon = weapon
        else:
            self.player.inventory.secondary_weapon = weapon

        # Eliminar el WeaponItem del inventario
        if 0 <= idx < len(self.player.inventory.items):
            self.player.inventory.items.pop(idx)

        self._pending_weapon_item  = None
        self._pending_weapon_index = -1

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, delta_time):
        from core.audio.music_manager import MusicManager
        MusicManager.instance().set_category("idle")

        if self._cutscene_active:
            self._update_cutscene(delta_time)
            return

        if self._dialog_manager and self._dialog_manager.is_dialog_active:
            return
        if self._inventory_open:
            return

        kills = 0
        if self._wave_manager is not None:
            prev = len(self._wave_manager.enemies)
            self._wave_manager.update(delta_time)
            kills += prev - len(self._wave_manager.enemies)
        else:
            prev = len(self.enemies)
            cleanup_dead_enemies(self.enemies)
            kills += prev - len(self.enemies)

        if self._wave_manager_north is not None:
            prev = len(self._wave_manager_north.enemies)
            self._wave_manager_north.update(delta_time)
            kills += prev - len(self._wave_manager_north.enemies)

        if kills > 0 and self.player:
            self.player.add_coins(kills * 10)
            self._total_kills += kills

        # Solo actualizar charcos manualmente si no hay WaveManager activo
        # (con WaveManager activo, él los actualiza internamente)
        if self._wave_manager is None and self._wave_manager_north is None:
            for puddle in list(self._toxic_puddles):
                puddle.update(delta_time, self.player)
            self._toxic_puddles[:] = [p for p in self._toxic_puddles if p.is_alive]

        if self.player:
            self.player.update(delta_time)
            self._check_enemy_contact(delta_time)
            self._check_player_death()

        if (not self._north_room_entered and self._north_room_rect and self.player
                and self._north_room_rect.collidepoint(self.player.position)
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)):
            self._north_room_entered = True
            self._seal_north_door()
            from dialogs.audres_dialogs import create_audres_north_room_entry
            self._dialog_manager.start_dialog(create_audres_north_room_entry())

        if (self._north_room_entered and self._wave_manager_north is None
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)):
            self._create_north_wave_manager()

        dialog_active = self._dialog_manager and self._dialog_manager.is_dialog_active

        if self._enemies_spawned and not self._shop_hint_triggered and not dialog_active:
            if not self.enemies:
                if self._wave_clear_timer < 0:
                    self._wave_clear_timer = 1.5
                else:
                    self._wave_clear_timer -= delta_time
                    if self._wave_clear_timer <= 0:
                        self._shop_hint_triggered = True
                        self._shop_unlocked = True
                        self._wave_clear_timer = -1.0
                        from dialogs.audres_dialogs import create_audres_shop_hint
                        self._dialog_manager.start_dialog(create_audres_shop_hint())
            else:
                self._wave_clear_timer = -1.0

        if (self._shop_hint_triggered and self._wave_manager is None
                and self._door is not None and not self._door.is_open and not dialog_active):
            self._create_wave_manager()

        if self._wave2_clear_timer >= 0 and not self._wave2_clear_triggered and not dialog_active:
            self._wave2_clear_timer -= delta_time
            if self._wave2_clear_timer <= 0:
                self._wave2_clear_timer = -1.0
                self._wave2_clear_triggered = True
                from dialogs.audres_dialogs import create_audres_wave2_clear
                self._dialog_manager.start_dialog(create_audres_wave2_clear())

    def _all_enemies(self) -> list:
        out = list(self._wave_manager.enemies if self._wave_manager else self.enemies)
        if self._wave_manager_north:
            out += list(self._wave_manager_north.enemies)
        return out

    def _update_cutscene(self, delta_time):
        if self._cutscene_phase == "walking":
            if self.audres and self._audres_walk_target:
                to = self._audres_walk_target - self.audres.position
                if to.length() > 8:
                    self.audres.position += to.normalize() * 300 * delta_time
                    self.audres.rotation  = to.angle_to(pygame.Vector2(0, -1)) + 180
                else:
                    self._cutscene_phase = "dialog"
                    self._dialog_manager.start_dialog(self._audres_intro_tree)
        elif self._cutscene_phase == "dialog":
            if not self._dialog_manager.is_dialog_active:
                self._finish_cutscene()

    def _finish_cutscene(self):
        if self.audres:
            self.audres.destroy()
        self.audres = None
        self._cutscene_active = False
        self._cutscene_phase  = "idle"
        for pos in _CUTSCENE_ENEMY_SPAWNS:
            enemy = Enemy("assets/icon.png", pos, 0, 0.05)
            enemy._controller = CharacterController(_ENEMY_SPEED, enemy)
            self.enemies.append(enemy)
        self._enemies_spawned = True

    def _create_wave_manager(self):
        self._wave_manager = WaveManager(
            player=self.player, total_waves=None,
            arena_center=(_ACX, _ACY), arena_half=_ARENA_HALF,
            arena_mix=True, rest_time=3.0, puddle_list=self._toxic_puddles)
        self._wave_manager.set_on_complete(self._on_waves_complete)

    def _create_north_wave_manager(self):
        corridor_h = 800
        north_sq   = int(_ARENA_HALF * 1.2)
        north_cy   = _ACY - _ARENA_HALF - corridor_h - north_sq
        self._wave_manager_north = WaveManager(
            player=self.player, total_waves=None,
            arena_center=(_ACX, north_cy), arena_half=north_sq,
            arena_mix=True, rest_time=3.0, puddle_list=self._toxic_puddles,
            start_wave=7, hp_scale_per_wave=0.10)

    def _on_waves_complete(self):
        if not self._wave2_clear_triggered and not self._going_level_complete:
            self._wave2_clear_timer = 1.5

    def _on_north_door_open(self):
        if self._door_collider:
            cm = CollisionManager._active
            if cm:
                cm.static_qtree.remove(self._door_collider)
            CollisionManager.static_colliders.discard(self._door_collider)
            CollisionManager.static_dirty = True
            self._door_collider = None
        if self._wave_manager:
            for e in list(self._wave_manager.enemies):
                e.take_damage(e.health)
            self._wave_manager.enemies.clear()
            self._wave_manager = None
        for e in list(self.enemies):
            e.take_damage(e.health)
        self.enemies.clear()
        self._toxic_puddles.clear()

    def _seal_north_door(self):
        self._north_room_sealed = True
        cx, cy = _ACX, _ACY
        h, t = _ARENA_HALF, _WALL_THICK
        dw = 240
        self._north_seal_collider = Collider(
            object(), Rectangle(cx, cy - h - t // 2, t // 2, dw // 2),
            layer=LAYERS["terrain"], static=True)

    def _on_exit_door_open(self):
        """Callback invocado por Door al alcanzar 500k score — quita el collider,
        lanza el diálogo de Audrey y spawna el helicóptero de extracción."""
        # Quitar el collider de la puerta de salida
        if self._exit_door_collider:
            cm = CollisionManager._active
            if cm:
                cm.static_qtree.remove(self._exit_door_collider)
            CollisionManager.static_colliders.discard(self._exit_door_collider)
            CollisionManager.static_dirty = True
            self._exit_door_collider = None
        if not self._helicopter_spawned:
            self._helicopter_spawned = True
            # Diálogo de Audrey indicando que está el helicóptero
            from dialogs.audres_dialogs import create_audres_exit_door
            if self._dialog_manager:
                self._dialog_manager.start_dialog(create_audres_exit_door())
            # Spawnear helicóptero en el fondo de la sala norte
            corridor_h = 800
            north_sq   = int(_ARENA_HALF * 1.2)
            heli_x     = _ACX
            heli_y     = _ACY - _ARENA_HALF - corridor_h - north_sq * 2 + north_sq // 2
            from item.item_drop_manager import HelicopterInteractable
            self._helicopter = HelicopterInteractable((heli_x, heli_y), self)

    # ── Colisiones / muerte ───────────────────────────────────────────────────

    def _check_enemy_contact(self, delta_time):
        # FIX: siempre decrementar; solo hacer daño cuando el cooldown llega a 0
        self._contact_dmg_cd -= delta_time
        if self._contact_dmg_cd > 0:
            return
        # FIX: guard hasattr(h, "owner") — algunos colliders de terreno no tienen owner
        hits = [
            h for h in self.player.collider.check_collision(layers=[LAYERS["enemy"]])
            if hasattr(h, "owner") and h.owner is not None and h.owner.is_alive()
        ]
        if hits:
            self.player.take_damage(10)
            self._contact_dmg_cd = 0.75

    def _check_player_death(self):
        if self.player and not self.player.is_alive():
            from scenes.game_over_scene import GameOverScene
            self.director.replace(GameOverScene(stats={
                "kills": self._total_kills, "coins": self.player.coins}))

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self, screen):
        im         = self.director._input_handler
        delta_time = self.director.clock.get_time() / 1000.0

        screen.fill(_BG_COLOR)
        self._draw_map(screen)

        mouse_pos     = pygame.Vector2(pygame.mouse.get_pos())
        active_weapon = self.player.inventory.get_weapon(
            self.player.inventory.active_weapon_slot)

        if self.weapon_controller:
            self.weapon_controller.setup_emitter(screen)

        movement = (pygame.Vector2(0, 0) if self._cutscene_active
                    else pygame.Vector2(im.actions["move_x"], im.actions["move_y"]))

        self.controller.speed = self.player.get_stat("speed")
        if not self._inventory_open:
            self.controller.move(movement, delta_time)
            if movement.length() > 0:
                self.player._dash_direction = pygame.Vector2(movement)

        if (not self._cutscene_active
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)
                and not self._inventory_open
                and self.weapon_controller):
            self.weapon_controller.update(im, delta_time, mouse_pos)

        self._camera_follow(self.player.position, delta_time)

        all_enemies = self._all_enemies()

        from character_scripts.enemy.enemy_types import ShooterEnemy
        for enemy in all_enemies:
            if isinstance(enemy, ShooterEnemy) and enemy.zone_active:
                enemy.draw_zone(screen, self.camera)

        for puddle in self._toxic_puddles:
            puddle.draw(screen, self.camera)

        if self._helicopter:
            self._helicopter.draw(screen, self.camera)

        if self._corridor_weapon:
            self._corridor_weapon.draw(screen, self.camera)

        entity_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for enemy in all_enemies:
            enemy.draw(entity_surf, self.camera)
            if getattr(enemy, "_hit_flash_timer", 0) > 0:
                sp = enemy.position - self.camera.position
                fr = enemy._render_asset.get_rect(center=sp)
                fs = pygame.Surface(fr.size, pygame.SRCALPHA)
                fs.fill((255, 30, 30, 180))
                entity_surf.blit(fs, fr)
            if isinstance(enemy, ShooterEnemy):
                enemy.draw_bullets(screen, self.camera)
        screen.blit(entity_surf, (0, 0))

        if self.player and self.player.inventory.drop_manager:
            self.player.inventory.drop_manager.draw(screen, self.camera)

        if self.audres:
            self.audres.draw(screen, self.camera)
        self.player.draw(screen, self.camera)

        if isinstance(active_weapon, Ranged) and active_weapon.is_reloading():
            self._draw_reload_bar(screen, active_weapon)
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

    def _draw_map(self, screen):
        cx = int(self.camera.position.x) if self.camera else 0
        cy = int(self.camera.position.y) if self.camera else 0
        ax = _ACX - _ARENA_HALF - cx
        ay = _ACY - _ARENA_HALF - cy
        arena_rect = pygame.Rect(ax, ay, _ARENA_HALF * 2, _ARENA_HALF * 2)
        pygame.draw.rect(screen, _FLOOR_COLOR, arena_rect)
        pygame.draw.rect(screen, _WALL_COLOR,  arena_rect, _WALL_THICK)

        if self._north_room_rect and self._corridor_rect:
            nr = self._north_room_rect.move(-cx, -cy)
            cr = self._corridor_rect.move(-cx, -cy)
            pygame.draw.rect(screen, (35, 35, 45), nr)
            pygame.draw.rect(screen, _WALL_COLOR,  nr, _WALL_THICK)
            pygame.draw.rect(screen, (35, 35, 45), cr)
            pygame.draw.rect(screen, _WALL_COLOR,
                             (cr.x - _WALL_THICK, cr.y, _WALL_THICK, cr.height))
            pygame.draw.rect(screen, _WALL_COLOR,
                             (cr.right, cr.y, _WALL_THICK, cr.height))
            pygame.draw.rect(screen, (35, 35, 45),
                             (cr.x - 2, cr.top - _WALL_THICK - 2, cr.width + 4, _WALL_THICK + 4))
            if not self._door or self._door.is_open:
                pygame.draw.rect(screen, _FLOOR_COLOR,
                                 (cr.x - 2, cr.bottom - _WALL_THICK - 2, cr.width + 4, _WALL_THICK + 4))

        door_w = 240
        side   = (_ARENA_HALF * 2 - door_w) // 2
        pygame.draw.rect(screen, _WALL_COLOR, (ax, ay - _WALL_THICK, side, _WALL_THICK))
        pygame.draw.rect(screen, _WALL_COLOR, (ax + side + door_w, ay - _WALL_THICK, side, _WALL_THICK))
        pygame.draw.rect(screen, _WALL_COLOR, (ax, ay + _ARENA_HALF * 2, _ARENA_HALF * 2, _WALL_THICK))
        pygame.draw.rect(screen, _WALL_COLOR, (ax - _WALL_THICK, ay, _WALL_THICK, _ARENA_HALF * 2))
        pygame.draw.rect(screen, _WALL_COLOR, (ax + _ARENA_HALF * 2, ay, _WALL_THICK, _ARENA_HALF * 2))

        if self._door:
            if not self._door.is_open:
                dr = self._door_rect.move(-cx, -cy)
                pygame.draw.rect(screen, (80, 50, 20), dr)
                pygame.draw.rect(screen, (20, 15, 10), dr, 4)
            self._door.draw(screen, self.camera)

        if self._exit_door and self._exit_door_rect:
            if not getattr(self._exit_door, 'is_open', True):
                er = self._exit_door_rect.move(-cx, -cy)
                pygame.draw.rect(screen, (80, 50, 20), er)
                pygame.draw.rect(screen, (20, 15, 10), er, 4)
            self._exit_door.draw(screen, self.camera)

        if self._north_room_sealed and self._door_rect:
            pygame.draw.rect(screen, _WALL_COLOR, self._door_rect.move(-cx, -cy))

    def _draw_reload_bar(self, screen, weapon):
        elapsed  = (pygame.time.get_ticks() - weapon._reload_start_time) / 1000.0
        progress = min(elapsed / weapon.reload_time, 1.0)
        sp = self.player.position - self.camera.position
        bw, bh = 80, 8
        bx, by = int(sp.x) - bw // 2, int(sp.y) + 32
        pygame.draw.rect(screen, (20, 20, 20),   (bx - 1, by - 1, bw + 2, bh + 2), border_radius=4)
        pygame.draw.rect(screen, (60, 60, 60),   (bx, by, bw, bh), border_radius=3)
        pygame.draw.rect(screen, (255, 160, 20), (bx, by, int(bw * progress), bh), border_radius=3)

    def _camera_follow(self, target, delta_time, speed=10):
        target_relative = target - self.camera.position
        center   = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        offset   = target_relative - center
        distance = offset.length()
        if distance > _CAM_BORDER_RADIUS:
            self.camera.move(offset.normalize() * (distance - _CAM_BORDER_RADIUS) * speed * delta_time)

    def get_last_frame(self):
        return self._last_frame