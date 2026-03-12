"""
Nivel 1 — primer nivel de prueba.
5 enemigos, sin mapa, fondo sólido.
Todo se crea desde cero cada vez que se entra al nivel.
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
from game_math import utils as math
from item.item_instance import ItemInstance
from item.item_loader import ItemRegistry
from runtime.round_manager import cleanup_dead_enemies
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, _CAM_BORDER_RADIUS
from ui import ui_manager
from weapons.ranged.ranged import Ranged


# ── Background / arena colours ────────────────────────────
_BG_COLOR    = (20, 20, 28)   # outside the arena
_FLOOR_COLOR = (45, 45, 55)   # arena floor
_WALL_COLOR  = (110, 90, 70)  # arena wall border

# ── Arena dimensions ───────────────────────────────────────
_ARENA_HALF = 1000   # half-side of the square arena  (total 2000 × 2000)
_WALL_THICK = 80     # collision & visual wall thickness

# ── Arena centre  ==  player spawn ─────────────────────────
_ACX = SCREEN_WIDTH  // 2   # 640
_ACY = SCREEN_HEIGHT // 2   # 360

# ── Enemy AI ─────────────────────────────────────────────────
_ENEMY_SPEED       = 110    # px/s (slower than the player's 250)
_SEPARATION_RADIUS = 90     # px  — enemies push each other away within this
_SEPARATION_WEIGHT = 2.0    # how strong the push is relative to chase direction

# ── Enemy spawn positions (spread across the arena) ────────
_ENEMY_SPAWNS = [
    (_ACX - 500, _ACY - 350),
    (_ACX + 550, _ACY - 400),
    (_ACX - 450, _ACY + 500),
    (_ACX + 600, _ACY + 450),
    (_ACX + 50,  _ACY - 750),
]


class Level1Scene(Scene):
    """First game level — accessible from the main menu."""

    def __init__(self):
        super().__init__()
        self._last_frame = None
        self.player = None
        self.controller = None
        self.camera = None
        self.enemies = []
        self._contact_damage_cooldown = 0.0
        self.audres = None
        self._dialog_manager = None
        self._audres_intro_tree  = None
        self._cutscene_active    = False
        self._cutscene_phase     = "idle"
        self._audres_walk_target = None
        # Wave-clear shop hint
        self._enemies_spawned     = False
        self._shop_hint_triggered = False
        self._wave_clear_timer    = -1.0
        # Oleadas
        self._wave_manager           = None
        # Charcos tóxicos — lista compartida con el wave manager
        self._toxic_puddles: list    = []
        # Fin de oleadas
        self._wave2_clear_triggered  = False
        self._wave2_clear_timer      = -1.0
        self._going_level_complete   = False
        self._total_kills            = 0
        self._idle_shot_timer        = -1.0
        self._IDLE_SHOT_TIMEOUT      = 40.0
        self.crosshair = pygame.image.load("assets/crosshair.png").convert_alpha()
        self.ads_effect = StatusEffect(
            "assets/effects/ads", "Aiming Down Sights", {"speed": -70}, -1
        )

    # ── Scene lifecycle ───────────────────────────────────────

        # ── Room dimensions ──
        self._door = None
        self._north_room_rect = None
        self._corridor_rect = None
        self._door_rect = None
        self._door_collider = None
        # ── Pasillo ──
        self._corridor_weapon = None
        # ── North room state ──
        self._north_room_entered  = False
        self._north_room_sealed   = False
        self._north_seal_collider = None
        self._wave_manager_north  = None

    def on_enter(self):
        MonoliteBehaviour.time_scale = 1.0
        pygame.mouse.set_visible(False)

        # Avoid inheriting held movement state from previous scene (e.g., menu navigation).
        if self.director and self.director._input_handler:
            ih = self.director._input_handler
            ih.actions["move_x"] = 0
            ih.actions["move_y"] = 0

        self._build_level()

    def on_exit(self):
        MonoliteBehaviour.time_scale = 0.0
        self._teardown_level()

    def on_pause(self):
        """Pause menu pushed on top — freeze time, don't teardown."""
        MonoliteBehaviour.time_scale = 0.0

    def on_resume(self):
        """Returned from pause menu — resume time, don't rebuild."""
        MonoliteBehaviour.time_scale = 1.0
        pygame.mouse.set_visible(False)

    # ── Build / teardown — everything fresh each time ─────────

    def _build_level(self):
        """Create all game objects from scratch — no stale state possible."""

        # Wipe ALL collision state so nothing survives from previous runs
        CollisionManager.dynamic_colliders.clear()
        CollisionManager.static_colliders.clear()
        if CollisionManager._active is not None:
            CollisionManager._active.dynamic_qtree.clear()
            CollisionManager._active.static_qtree.clear()
            CollisionManager.static_dirty = True
        else:
            CollisionManager(Rectangle(-4000, -4000, 8000, 8000))

        # Ensure other singletons exist
        if AudioManager._instance is None:
            AudioManager._instance = AudioManager()
        if not ItemRegistry._items:
            ItemRegistry()
            ItemRegistry.load("assets/items/item_data.json")

        # Player
        self.player = Player(
            "assets/player/survivor-idle_rifle_0.png",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        )
        self.controller = CharacterController(250, self.player)
        AudioManager.instance().set_listener(self.player.audio_listener)

        # Weapon + ammo
        weapon = Ranged(
            "assets/weapons/AK47.png", "AK-47", 60, 1500,
            "7.62", 15, 0.15, 0.6, muzzle_offset=(35, 15),
        )
        weapon.infinite_reserve = True  # Reserva infinita: hay que recargar pero nunca faltan balas
        self.player.inventory.add_weapon(self.player, weapon, "primary")

        # Camera
        self.camera = Camera()

        # Enemies spawn after the intro cutscene ends
        self.enemies = []

        # Boundary walls
        self._build_walls()

        # Add interactive doors explicitly after walls
        self._build_doors()

        # Arma en el pasillo norte (SPAS-12) — va al slot secundario
        from item.item_drop_manager import DroppedWeapon
        from weapons.ranged.ranged_types import SPAS12
        _pickup = SPAS12()
        _pickup.infinite_reserve = True
        self._corridor_weapon = DroppedWeapon(
            _pickup,
            (_ACX, _ACY - _ARENA_HALF - 400),   # centro del pasillo
            slot="secondary",
        )

        from dialogs.audres_dialogs import create_audres_intro
        self._audres_intro_tree = create_audres_intro()
        self.audres = NPC(
            name="AUDReS-01",
            position=(_ACX, _ACY - _ARENA_HALF + 100),   # top of arena
            dialog_tree=None,
            sprite_path="assets/characters/audres/sprite_topdown.jpg",
            scale=0.16,
        )

        # DialogManager — reset the singleton to a clean state
        self._dialog_manager = DialogManager()
        self._dialog_manager.active_dialog = None
        self._dialog_manager.is_dialog_active = False
        self._dialog_manager.selected_option = 0
        self._dialog_manager._cached_dialog_surface = None
        self._dialog_manager._cached_node_id = None
        self._dialog_manager._needs_redraw = True

        # Kick off the cutscene
        self._cutscene_active    = True
        self._cutscene_phase     = "walking"
        self._audres_walk_target = pygame.Vector2(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200
        )

    def _build_walls(self):
        """Builds arena walls with a gap at the top for the north room door."""
        cx, cy = _ACX, _ACY
        h, t   = _ARENA_HALF, _WALL_THICK
        door_w = 240

        # Define extra room (north)
        # Corridor properties
        corridor_w = 240
        corridor_h = 800 # Pasillo aún más largo
        # North square properties
        north_sq_half = int(_ARENA_HALF * 1.2) # A bit larger than the main square
        
        self._north_room_rect = pygame.Rect(
            cx - north_sq_half, cy - h - corridor_h - north_sq_half * 2,
            north_sq_half * 2, north_sq_half * 2
        )
        self._corridor_rect = pygame.Rect(
            cx - corridor_w // 2, cy - h - corridor_h,
            corridor_w, corridor_h
        )

        wall_defs = [
            # Main arena: Top wall (left of door)
            (cx - (h + door_w // 2) / 2, cy - h - t // 2, t // 2, (h - door_w // 2) / 2),
            # Main arena: Top wall (right of door)
            (cx + (h + door_w // 2) / 2, cy - h - t // 2, t // 2, (h - door_w // 2) / 2),
            
            # Corridor walls (Left & Right)
            (cx - corridor_w // 2 - t // 2, cy - h - corridor_h // 2, corridor_h // 2, t // 2),
            (cx + corridor_w // 2 + t // 2, cy - h - corridor_h // 2, corridor_h // 2, t // 2),

            # North Square walls:
            # Bottom parts connecting to corridor
            (cx - (north_sq_half + corridor_w // 2) / 2, cy - h - corridor_h - t // 2, t // 2, (north_sq_half - corridor_w // 2) / 2),
            (cx + (north_sq_half + corridor_w // 2) / 2, cy - h - corridor_h - t // 2, t // 2, (north_sq_half - corridor_w // 2) / 2),
            # Left & Right of North Square
            (cx - north_sq_half - t // 2, cy - h - corridor_h - north_sq_half, north_sq_half, t // 2),
            (cx + north_sq_half + t // 2, cy - h - corridor_h - north_sq_half, north_sq_half, t // 2),
            # Top of North Square
            (cx, cy - h - corridor_h - north_sq_half * 2 - t // 2, t // 2, north_sq_half + t),

            # Standard walls: bottom, left, right of Main Arena
            (cx, cy + h + t // 2, t // 2, h + t),
            (cx - h - t // 2, cy, h, t // 2),
            (cx + h + t // 2, cy, h, t // 2),
        ]

        for wx, wy, wh, ww in wall_defs:
            Collider(
                object(), 
                Rectangle(wx, wy, wh, ww),
                layer=LAYERS["terrain"],
                static=True,
            )

    def _on_north_door_open(self):
        # Remove collider from static set so opening is immediate and reliable.
        if self._door_collider:
            from core.collision.collision_manager import CollisionManager
            if CollisionManager._active is not None:
                CollisionManager._active.static_qtree.remove(self._door_collider)
            CollisionManager.static_colliders.discard(self._door_collider)
            CollisionManager.static_dirty = True
            self._door_collider = None

        # ── Terminar primera fase de oleadas ─────────────────────────────────
        # Matar todos los enemigos vivos (dispara die() -> drop loot, quita collider)
        if self._wave_manager is not None:
            for e in list(self._wave_manager.enemies):
                e.take_damage(e.health)
            self._wave_manager.enemies.clear()
        for e in list(self.enemies):
            e.take_damage(e.health)
        self.enemies.clear()
        # Descartar el wave manager: el HUD desaparece y no spawnea más enemigos
        self._wave_manager = None
        self._toxic_puddles.clear()

    def _build_doors(self):
        from map.interactables.door import Door
        cx, cy = _ACX, _ACY
        h, t   = _ARENA_HALF, _WALL_THICK
        door_width = 240
        
        # --- North Door ---
        door_px = cx
        door_py = cy - h - t // 2
        self._door = Door("Puerta Norte", (door_px, door_py), 500, self._on_north_door_open)
        self._door_rect = pygame.Rect(door_px - door_width//2, door_py - t//2, door_width, t)
        self._door_collider = Collider(
            object(),
            Rectangle(door_px, door_py, t // 2, door_width // 2),
            layer=LAYERS["terrain"],
            static=True
        )

    def _teardown_level(self):
        """Wipe all collision and MonoliteBehaviour state — total cleanup."""
        # Nuke all colliders and quadtrees
        CollisionManager.dynamic_colliders.clear()
        CollisionManager.static_colliders.clear()
        if CollisionManager._active is not None:
            CollisionManager._active.dynamic_qtree.clear()
            CollisionManager._active.static_qtree.clear()

            # Remove player-related MonoliteBehaviour instances won't be needed
            # since a new player is created each time

        self.player = None
        self.controller = None
        self.audres = None
        self._audres_intro_tree   = None
        self._cutscene_active     = False
        self._cutscene_phase      = "idle"
        self._audres_walk_target  = None
        self._enemies_spawned     = False
        self._shop_hint_triggered = False
        self._wave_clear_timer    = -1.0
        self._wave_manager           = None
        self._toxic_puddles          = []
        self._wave2_clear_triggered  = False
        self._wave2_clear_timer      = -1.0
        self._going_level_complete   = False
        self._total_kills            = 0
        self._idle_shot_timer        = -1.0
        if self._door:
            from map.interactables.interaction_manager import InteractionManager
            InteractionManager().unregister(self._door)
        self._door = None
        self._door_collider = None
        if self._corridor_weapon is not None:
            self._corridor_weapon._unregister()
            self._corridor_weapon = None
        self._north_room_entered  = False
        self._north_room_sealed   = False
        self._north_seal_collider = None
        self._wave_manager_north  = None
        if self._dialog_manager:
            self._dialog_manager.end_dialog()
        self._dialog_manager = None
    # ── Input ─────────────────────────────────────────────────

    def handle_events(self, input_handler):
        # ── Pause always works, even during cutscene ───────────
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

        # ── Cutscene: swallow every input, only forward dialog advancement ──
        if self._cutscene_active:
            if self._dialog_manager and self._dialog_manager.is_dialog_active:
                self._dialog_manager.handle_input(
                    pygame.key.get_pressed(),
                    input_handler.keys_just_pressed,
                )
            for key in input_handler.actions:
                val = input_handler.actions[key]
                input_handler.actions[key] = 0 if isinstance(val, (int, float)) else False
            return

        # ── Forward dialog input when shop hint (or any dialog) is active ──
        if self._dialog_manager and self._dialog_manager.is_dialog_active:
            # La tienda tiene prioridad: se puede abrir incluso con diálogo activo
            if input_handler.actions.get("shop"):
                input_handler.actions["shop"] = False
                from scenes.shop_scene import ShopScene
                self.director.push(ShopScene(self, self.player))
                return
            self._dialog_manager.handle_input(
                pygame.key.get_pressed(),
                input_handler.keys_just_pressed,
            )
            return

        # ── Open shop with P ──────────────────────────────────
        if input_handler.actions.get("shop"):
            input_handler.actions["shop"] = False
            from scenes.shop_scene import ShopScene
            self.director.push(ShopScene(self, self.player))
            return
            
        # ── Toggle interaction (door) with E ──────────────────
        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().check_interaction(self.player, input_handler)

        # ── Hotbar: select slot with 1-6 ─────────────────────
        if input_handler.actions["hotkey_slot"] >= 0:
            self.player.inventory.select_item(input_handler.actions["hotkey_slot"])

        # ── Use selected consumable with F ────────────────────
        if input_handler.actions["use_item"]:
            self.player.inventory.use_selected_item(self.player)

    # ── Update ────────────────────────────────────────────────

    def update(self, delta_time):
        # ── Música ────────────────────────────────────────────
        from core.audio.music_manager import MusicManager
        MusicManager.instance().set_category("idle")

        if self._cutscene_active:
            self._update_cutscene(delta_time)
            return
        if self._wave_manager is not None:
            # Contar kills antes de que el wave_manager limpie su lista interna
            alive_before = len(self._wave_manager.enemies)
            self._wave_manager.update(delta_time)
            killed = alive_before - len(self._wave_manager.enemies)
        else:
            alive_before = len(self.enemies)
            cleanup_dead_enemies(self.enemies)
            killed = alive_before - len(self.enemies)
        if self._wave_manager_north is not None:
            north_before = len(self._wave_manager_north.enemies)
            self._wave_manager_north.update(delta_time)
            killed += north_before - len(self._wave_manager_north.enemies)
        if killed > 0 and self.player:
            self.player.add_coins(killed * 10)
            self.player.add_score(killed * 20)
            self._total_kills += killed
        if self.player:
            self.player.update(delta_time)
            self._update_enemies(delta_time)
            self._check_enemy_contact(delta_time)
            self._check_player_death()

        # ── Timeout de inactividad (sin disparar) ─────────────────────────────
        # Se activa en render() al disparar. Aquí solo lo decrementamos y, si
        # llega a 0 con enemigos activos, matamos a los restantes.
        all_enemies = (
            list(self._wave_manager.enemies if self._wave_manager is not None else self.enemies)
            + (list(self._wave_manager_north.enemies) if self._wave_manager_north is not None else [])
        )
        if self._idle_shot_timer >= 0:
            if all_enemies:
                self._idle_shot_timer -= delta_time
                if self._idle_shot_timer <= 0:
                    print(f"[TIMEOUT] {len(all_enemies)} enemigo(s) eliminado(s) por inactividad")
                    for e in all_enemies:
                        e.take_damage(e.health)
                    self._idle_shot_timer = -1.0
            else:
                self._idle_shot_timer = -1.0  # sin enemigos, desactivar

        # ── Detección de entrada a la sala norte ───────────────────────────────
        if (not self._north_room_entered
                and self._north_room_rect
                and self.player
                and self._north_room_rect.collidepoint(self.player.position)
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)):
            self._north_room_entered = True
            self._seal_north_door()
            from dialogs.audres_dialogs import create_audres_north_room_entry
            self._dialog_manager.start_dialog(create_audres_north_room_entry())

        # ── Iniciar oleadas de sala norte tras el diálogo ──────────────────────
        if (self._north_room_entered
                and self._wave_manager_north is None
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)):
            self._create_north_wave_manager()

        # ── Wave-clear shop hint (fires once, 1.5 s after all enemies die) ──
        if (self._enemies_spawned
                and not self._shop_hint_triggered
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)):
            if len(self.enemies) == 0:
                if self._wave_clear_timer < 0:
                    self._wave_clear_timer = 1.5          # start countdown
                else:
                    self._wave_clear_timer -= delta_time
                    if self._wave_clear_timer <= 0:
                        self._shop_hint_triggered = True
                        self._wave_clear_timer = -1.0
                        from dialogs.audres_dialogs import create_audres_shop_hint
                        self._dialog_manager.start_dialog(create_audres_shop_hint())
            else:
                self._wave_clear_timer = -1.0             # reset if enemies respawn

        # ── Iniciar wave manager una vez que el diálogo del shop hint termine ────
        # Solo si la puerta norte todavía no se abrió (fase 1 no terminada)
        if (self._shop_hint_triggered
                and self._wave_manager is None
                and self._door is not None and not self._door.is_open
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)):
            self._create_wave_manager()

        # ── Fin de oleadas: Audrey felicita tras 1.5 s ────────────────────────
        if self._wave2_clear_timer >= 0 and not self._wave2_clear_triggered:
            if not (self._dialog_manager and self._dialog_manager.is_dialog_active):
                self._wave2_clear_timer -= delta_time
                if self._wave2_clear_timer <= 0:
                    self._wave2_clear_timer = -1.0
                    self._wave2_clear_triggered = True
                    from dialogs.audres_dialogs import create_audres_wave2_clear
                    self._dialog_manager.start_dialog(create_audres_wave2_clear())
            else:
                self._wave2_clear_timer = -1.0  # reset si ya hay otro diálogo activo

        # ── Navegar al nivel completo cuando termina el diálogo de felicitación ─
        if (self._wave2_clear_triggered
                and not self._going_level_complete
                and not (self._dialog_manager and self._dialog_manager.is_dialog_active)):
            self._going_level_complete = True
            from scenes.level_complete_scene import LevelCompleteScene
            self.director.replace(LevelCompleteScene(
                self._last_frame,
                "Nivel 1",
                {"kills": self._total_kills,
                 "coins": self.player.coins if self.player else 0},
                next_scene_class=None
            ))

    def _update_enemies(self, delta_time):
        """Chase the player + separation steering so enemies don't stack."""
        enemies = list(self._wave_manager.enemies if self._wave_manager is not None else self.enemies)
        if self._wave_manager_north is not None:
            enemies = enemies + list(self._wave_manager_north.enemies)
        for enemy in enemies:
            # ── Chase direction ─────────────────────────────────────────────
            to_player = self.player.position - enemy.position
            if to_player.length() > 0:
                move_dir = to_player.normalize()
            else:
                move_dir = pygame.Vector2(0, 0)

            # ── Separation from other enemies ───────────────────────────────
            sep = pygame.Vector2(0, 0)
            for other in enemies:
                if other is enemy:
                    continue
                diff = enemy.position - other.position
                dist = diff.length()
                if 0 < dist < _SEPARATION_RADIUS:
                    # Stronger push the closer they are
                    sep += diff.normalize() * (1.0 - dist / _SEPARATION_RADIUS)

            move_dir = move_dir + sep * _SEPARATION_WEIGHT
            if move_dir.length() > 0:
                move_dir = move_dir.normalize()

            # ── ShooterEnemy: handle its own AI and skip movement while aiming ─
            from character_scripts.enemy.shooter_enemy import ShooterEnemy as _ShooterEnemy
            if isinstance(enemy, _ShooterEnemy):
                enemy.update(delta_time, self.player)
                if enemy.is_shooting:
                    # Rotate toward aim direction but don't move
                    if to_player.length() > 0:
                        enemy.rotation = to_player.angle_to(pygame.Vector2(0, -1))
                    enemy._hit_flash_timer = max(0.0, enemy._hit_flash_timer - delta_time)
                    continue  # skip movement + rest of loop for this enemy

            enemy._controller.move(move_dir, delta_time)

            # ── Rotate enemy toward player ──────────────────────
            if to_player.length() > 0:
                enemy.rotation = to_player.angle_to(pygame.Vector2(0, -1))

            # ── Tick hit-flash timer ────────────────────────────
            enemy._hit_flash_timer = max(0.0, enemy._hit_flash_timer - delta_time)

            # ── ToxicEnemy: generate puddles each frame ─────────
            from character_scripts.enemy.toxic_enemy import ToxicEnemy as _ToxicEnemy
            if isinstance(enemy, _ToxicEnemy):
                enemy.update(delta_time)

        # ── Update and prune toxic puddles ──────────────────────
        for puddle in self._toxic_puddles:
            puddle.update(delta_time, self.player)
        self._toxic_puddles[:] = [p for p in self._toxic_puddles if p.is_alive]

    _AUDRES_WALK_SPEED = 300   # px/s during the intro walk

    def _seal_north_door(self):
        """Coloca un collider de pared permanente donde estaba la puerta norte."""
        self._north_room_sealed = True
        cx, cy = _ACX, _ACY
        h, t = _ARENA_HALF, _WALL_THICK
        door_width = 240
        door_px = cx
        door_py = cy - h - t // 2
        self._north_seal_collider = Collider(
            object(),
            Rectangle(door_px, door_py, t // 2, door_width // 2),
            layer=LAYERS["terrain"],
            static=True,
        )

    def _create_north_wave_manager(self):
        """Instancia Level1WaveManager en la sala norte.

        Empieza en la oleada 7 (dificultad media-alta) con escalado de vida
        del 10 % acumulativo por ronda.
        """
        from runtime.level1_wave_manager import Level1WaveManager
        corridor_h = 800
        north_sq_half = int(_ARENA_HALF * 1.2)
        north_cx = _ACX
        north_cy = _ACY - _ARENA_HALF - corridor_h - north_sq_half
        self._wave_manager_north = Level1WaveManager(
            arena_center=(north_cx, north_cy),
            arena_half=north_sq_half,
            rest_time=3.0,
            enemy_speed=_ENEMY_SPEED,
            puddle_list=self._toxic_puddles,
            start_wave=7,           # primera oleada sera la 7 (55 enemigos)
            hp_scale_per_wave=0.10, # +10 % de vida acumulativo por ronda
        )

    def _create_wave_manager(self):
        """Instancia Level1WaveManager con oleadas mixtas de enemigos.

        Configura aquí los tipos de enemigos por oleada:
          wave_config  — lista de ints o dicts {"normal":N, "tank":N, "toxic":N}
          rest_time    — segundos de descanso entre oleadas
          spawn_duration — segundos para distribuir el spawn
        """
        from runtime.level1_wave_manager import Level1WaveManager
        self._wave_manager = Level1WaveManager(
            arena_center=(_ACX, _ACY),
            arena_half=_ARENA_HALF,
            rest_time=3.0,
            enemy_speed=_ENEMY_SPEED,
            puddle_list=self._toxic_puddles,
        )
        self._wave_manager.set_on_complete(self._on_waves_complete)

    def _on_waves_complete(self):
        """Callback del Level1WaveManager: arranca el timer de felicitación."""
        if not self._wave2_clear_triggered and not self._going_level_complete:
            self._wave2_clear_timer = 1.5

    def _update_cutscene(self, delta_time):
        """State machine: walking → dialog → enemies spawn."""
        if self._cutscene_phase == "walking":
            if self.audres and self._audres_walk_target:
                to_target = self._audres_walk_target - self.audres.position
                dist = to_target.length()
                if dist > 8:
                    self.audres.position += (
                        to_target.normalize() * self._AUDRES_WALK_SPEED * delta_time
                    )
                    self.audres.rotation = to_target.angle_to(pygame.Vector2(0, -1)) + 180
                else:
                    # Reached the player — start the scripted dialog
                    self._cutscene_phase = "dialog"
                    self._dialog_manager.start_dialog(self._audres_intro_tree)

        elif self._cutscene_phase == "dialog":
            # Wait for the player to advance through all dialog nodes
            if not self._dialog_manager.is_dialog_active:
                self._finish_cutscene()

    def _finish_cutscene(self):
        """End the intro cutscene: hide Audrey and spawn the enemies."""
        if self.audres is not None:
            self.audres.destroy()
        self.audres = None
        self._cutscene_active = False
        self._cutscene_phase  = "idle"
        for pos in _ENEMY_SPAWNS:
            enemy = Enemy("assets/icon.png", pos, 0, 0.05)
            enemy._controller = CharacterController(_ENEMY_SPEED, enemy)
            self.enemies.append(enemy)
        self._enemies_spawned = True

    # ── Render ─────────────────────────────────────────────────────────────

    def render(self, screen):
        im = self.director._input_handler
        delta_time = self.director.clock.get_time() / 1000.0

        # Background (outside-arena void)
        screen.fill(_BG_COLOR)

        # ── Arena floor + wall border ─────────────────────────
        ax = _ACX - _ARENA_HALF - int(self.camera.position.x)
        ay = _ACY - _ARENA_HALF - int(self.camera.position.y)
        arena_rect = pygame.Rect(ax, ay, _ARENA_HALF * 2, _ARENA_HALF * 2)
        pygame.draw.rect(screen, _FLOOR_COLOR, arena_rect)           # floor
        pygame.draw.rect(screen, _WALL_COLOR,  arena_rect, _WALL_THICK)  # walls

        # Mouse position (for crosshair & aiming)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # ── Active Rects mapped to screen positions ──
        # ax y ay representan la esquina superior izquierda (top-left) de la arena original 
        ax = _ACX - _ARENA_HALF - int(self.camera.position.x)
        ay = _ACY - _ARENA_HALF - int(self.camera.position.y)
        
        # Rectángulo que representa el suelo de la arena jugable inicial de tamaño _ARENA_HALF
        arena_rect = pygame.Rect(ax, ay, _ARENA_HALF * 2, _ARENA_HALF * 2)

        # Draw main arena and room floors
        # Pintamos la base de nuestro campo usando el color de suelo
        pygame.draw.rect(screen, _FLOOR_COLOR, arena_rect)
        if self._north_room_rect and self._corridor_rect:
            # === DIBUJANDO LA HABITACIÓN SECRETA (Cuadrado norte) ===
            n_rect = self._north_room_rect.copy()
            # Desplazamos la posición por la que lleva la cámara para que encaje
            n_rect.x -= int(self.camera.position.x)
            n_rect.y -= int(self.camera.position.y)
            # Dibujamos su suelo colorizado un poco más oscuro
            pygame.draw.rect(screen, (35, 35, 45), n_rect)  
            # Dibujamos su borde físico (pared) externa
            pygame.draw.rect(screen, _WALL_COLOR, n_rect, _WALL_THICK)
            
            # === DIBUJANDO EL PASILLO ===
            c_rect = self._corridor_rect.copy()
            c_rect.x -= int(self.camera.position.x)
            c_rect.y -= int(self.camera.position.y)
            # Dibujamos su suelo
            pygame.draw.rect(screen, (35, 35, 45), c_rect)
            
            # === CONSTRUYENDO Y PINTANDO LAS PAREDES DEL PASILLO ===
            # Pared Izquierda del pasillo 
            pygame.draw.rect(screen, _WALL_COLOR, (c_rect.x - _WALL_THICK, c_rect.y, _WALL_THICK, c_rect.height)) 
            # Pared Derecha del pasillo
            pygame.draw.rect(screen, _WALL_COLOR, (c_rect.right, c_rect.y, _WALL_THICK, c_rect.height)) 
            
            # == MÁSCARAS DE CONEXIÓN (BORRANDO PAREDES PARA FORMAR EL FLUJO DEL CUARTO) ==
            # Ocultamos la pared de arriba que lo conecta con el cuadro superior norte pintándolo del color de ambas habitaciones (35, 35, 45)
            # Esto siempre está abierto y visible si pasaste el marco final. Para asegurar que borra la línea marrón, 
            # lo hacemos un poco más alto.
            conn_rect2 = pygame.Rect(
                c_rect.x - 2,
                c_rect.top - _WALL_THICK - 2,
                c_rect.width + 4,
                _WALL_THICK + 4,
            )
            pygame.draw.rect(screen, (35, 35, 45), conn_rect2)

            # Ocultamos / enmascaramos la pared de abajo del pasillo pintándola del color del suelo de la arena principal 
            # (Así la puerta no parece una división estática), pero SOLO lo hacemos si la puerta YA se abrió o no existe
            if not self._door or self._door.is_open:
                conn_rect1 = pygame.Rect(
                    c_rect.x - 2,
                    c_rect.bottom - _WALL_THICK - 2,
                    c_rect.width + 4,
                    _WALL_THICK + 4,
                )
                pygame.draw.rect(screen, _FLOOR_COLOR, conn_rect1)
                # Enmascara la franja interior de la pared superior de la arena
                # (pintada por el border-rect genérico) que queda visible en el hueco
                inner_top_mask = pygame.Rect(c_rect.x - 2, c_rect.bottom, c_rect.width + 4, _WALL_THICK + 2)
                pygame.draw.rect(screen, _FLOOR_COLOR, inner_top_mask)

        # === DIBUJANDO LAS PAREDES DE LA ARENA PRINCIPAL (Base square) === 
        # (Draw manually line by line to support the gap, instead of a border)
        
        # Pared de abajo
        pygame.draw.rect(screen, _WALL_COLOR, (ax, ay + _ARENA_HALF*2, _ARENA_HALF*2, _WALL_THICK)) # bottom
        # Pared izquierda
        pygame.draw.rect(screen, _WALL_COLOR, (ax - _WALL_THICK, ay, _WALL_THICK, _ARENA_HALF*2)) # left
        # Pared derecha
        pygame.draw.rect(screen, _WALL_COLOR, (ax + _ARENA_HALF*2, ay, _WALL_THICK, _ARENA_HALF*2)) # right

        # HUECO DE LA PUERTA:
        # La pared superior en dos partes, una a la izquierda y otra a la derecha, dejando el hueco de en medio (door_w) 
        door_w = 240
        top_left_w = (_ARENA_HALF * 2 - door_w) // 2
        # Pedazo izquierdo superior
        pygame.draw.rect(screen, _WALL_COLOR, (ax, ay - _WALL_THICK, top_left_w, _WALL_THICK))
        # Pedazo derecho superior (dejando top_left_w + door_w de salto)
        pygame.draw.rect(screen, _WALL_COLOR, (ax + top_left_w + door_w, ay - _WALL_THICK, top_left_w, _WALL_THICK))

        # Dynamic Doors Drawing (overrides connections if closed)
        if self._door:
            # If door is closed, we should draw a solid line/wall representing the gate
            if not self._door.is_open:
                dr = self._door_rect.copy()
                dr.x -= int(self.camera.position.x)
                dr.y -= int(self.camera.position.y)
                # Dibujamos detrás la parte estructural de la pared normal
                pygame.draw.rect(screen, _WALL_COLOR, dr)

                # Encima un marco / puerta reforzada visible
                pygame.draw.rect(screen, (80, 50, 20), dr)
                pygame.draw.rect(screen, (20, 15, 10), dr, 4)

            # Dibujamos las interfaces visuales propias de la puerta (Precio, Letras)
            self._door.draw(screen, self.camera)

        # Sello permanente — pared sólida cuando la puerta norte se cerró definitivamente
        if self._north_room_sealed and self._door_rect:
            dr = self._door_rect.copy()
            dr.x -= int(self.camera.position.x)
            dr.y -= int(self.camera.position.y)
            pygame.draw.rect(screen, _WALL_COLOR, dr)

        dialog_active = self._dialog_manager and self._dialog_manager.is_dialog_active

        # Movement (frozen during cutscene)
        movement = (
            pygame.Vector2(0, 0) if self._cutscene_active
            else pygame.Vector2(im.actions["move_x"], im.actions["move_y"])
        )

        # Apply speed from stats
        self.controller.speed = self.player.get_stat("speed")

        # ── Active weapon ─────────────────────────────────────
        active_weapon = self.player.inventory.get_weapon(
            self.player.inventory.active_weapon_slot
        )

        # Update weapon emitter surfaces every frame
        if active_weapon and isinstance(active_weapon, Ranged):
            active_weapon.emitter.surface = screen
            active_weapon.emitter.camera = self.camera

        if not self._cutscene_active:
            # Swap weapon
            if im.actions["swap_weapon"]:
                im.actions["swap_weapon"] = False
                self.player.inventory.swap_weapons()

            # Reload
            if im.actions["reload"]:
                im.actions["reload"] = False
                if active_weapon is not None:
                    active_weapon.reload()

            # ── Aiming & Shooting ───────────────────────────────────
            if im.actions["attack"] or im.actions["aim"]:
                # Slow player while aiming
                self.player.add_effect(self.ads_effect)

                # Rotate player towards mouse
                direction_to_mouse = mouse_pos - (self.player.position - self.camera.position)
                target_angle = direction_to_mouse.angle_to(pygame.Vector2(0, -1))
                self.player.set_rotation(
                    math.lerp_angle(self.player.rotation, target_angle, 10 * delta_time) + 0.164
                )

                # Shoot
                if im.actions["attack"]:
                    if active_weapon is not None:
                        direction = pygame.Vector2(0, -1).rotate(-self.player.rotation)
                        if isinstance(active_weapon, Ranged):
                            active_weapon.play_trail_effect(
                                screen,
                                (self.player.position - self.camera.position)
                                + direction * active_weapon.muzzle_offset[0]
                                + direction.rotate(90) * active_weapon.muzzle_offset[1],
                                direction,
                            )
                        if active_weapon.shoot():
                            self._idle_shot_timer = self._IDLE_SHOT_TIMEOUT  # reset al disparar

            elif movement.length() > 0:
                # Rotate player towards movement when not aiming
                target_angle = movement.angle_to(pygame.Vector2(0, -1))
                self.player.rotation = math.lerp_angle(
                    self.player.rotation, target_angle, 7.5 * delta_time
                )

            if not im.actions["attack"] and not im.actions["aim"]:
                self.player.remove_effect("Aiming Down Sights")

        # Move player
        self.controller.move(movement, delta_time)
        # Record last non-zero movement for dash direction
        if movement.length() > 0:
            self.player._dash_direction = pygame.Vector2(movement)

        # Camera follow
        self._camera_follow(self.player.position, delta_time)

        # Draw shooter danger zones (below puddles and enemies)
        active_enemies = list(self._wave_manager.enemies if self._wave_manager is not None else self.enemies)
        if self._wave_manager_north is not None:
            active_enemies += list(self._wave_manager_north.enemies)
        from character_scripts.enemy.shooter_enemy import ShooterEnemy as _ShooterEnemy
        for enemy in active_enemies:
            if isinstance(enemy, _ShooterEnemy) and enemy.zone_active:
                enemy.draw_zone(screen, self.camera)

        # Draw toxic puddles (below enemies)
        for puddle in self._toxic_puddles:
            puddle.draw(screen, self.camera)

        # Draw corridor weapon pickup
        if self._corridor_weapon is not None:
            self._corridor_weapon.draw(screen, self.camera)

        # Draw enemies
        entity_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for enemy in active_enemies:
            enemy.draw(entity_surface, self.camera)
            # Hit-flash: red overlay for _HIT_FLASH_DURATION seconds after damage
            if enemy._hit_flash_timer > 0:
                screen_pos = enemy.position - self.camera.position
                flash_rect = enemy._render_asset.get_rect(center=screen_pos)
                flash_surf = pygame.Surface(flash_rect.size, pygame.SRCALPHA)
                flash_surf.fill((255, 30, 30, 180))
                entity_surface.blit(flash_surf, flash_rect)
        screen.blit(entity_surface, (0, 0))

        # Draw Audrey NPC
        if self.audres:
            self.audres.draw(screen, self.camera)

        # Draw player
        self.player.draw(screen, self.camera)

        # Reload progress bar
        if active_weapon is not None and active_weapon.is_reloading():
            elapsed  = (pygame.time.get_ticks() - active_weapon._reload_start_time) / 1000.0
            progress = min(elapsed / active_weapon.reload_time, 1.0)
            sp = self.player.position - self.camera.position
            bar_w, bar_h = 80, 8
            bx = int(sp.x) - bar_w // 2
            by = int(sp.y) + 32
            pygame.draw.rect(screen, (20, 20, 20),   (bx - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=4)
            pygame.draw.rect(screen, (60, 60, 60),   (bx, by, bar_w, bar_h),                  border_radius=3)
            pygame.draw.rect(screen, (255, 160, 20), (bx, by, int(bar_w * progress), bar_h),  border_radius=3)

        # Draw crosshair at mouse position
        screen.blit(
            pygame.transform.scale(self.crosshair, (40, 40)),
            (mouse_pos - (20, 20)),
        )

        # HUD
        _hud_wm = self._wave_manager_north if self._wave_manager_north is not None else self._wave_manager
        ui_manager.draw_overlay(screen, self.player, wave_manager=_hud_wm, delta_time=delta_time)

        # Dialog UI (drawn last so it's always on top)
        if self._dialog_manager:
            draw_dialog_ui(screen, self._dialog_manager)

        # Cache frame for PauseScene overlay
        self._last_frame = screen.copy()

    # ── Helpers ────────────────────────────────────────────────

    def get_last_frame(self):
        """Return the last rendered frame (used by PauseScene)."""
        return self._last_frame

    def _check_enemy_contact(self, delta_time):
        """Deal damage to the player when touching a living enemy. 0.75s cooldown."""
        self._contact_damage_cooldown -= delta_time
        if self._contact_damage_cooldown > 0:
            return

        hits = self.player.collider.check_collision(layers=[LAYERS["enemy"]])
        # Ignore corpses that haven't been cleaned up yet
        alive_hits = [h for h in hits if h.owner.is_alive()]
        if alive_hits:
            self.player.take_damage(10)
            self._contact_damage_cooldown = 0.75

            # ── Player death (also caught by _check_player_death, but keep for safety) ──
            if not self.player.is_alive():
                return  # _check_player_death will handle the scene transition

    def _check_player_death(self):
        """Transitions to DeathScene if the player has no HP. Called every frame."""
        if self.player and not self.player.is_alive():
            from scenes.death_scene import DeathScene
            self.director.replace(DeathScene(
                self._last_frame,
                {"kills": self._total_kills, "coins": self.player.coins},
            ))

    def _camera_follow(self, target, delta_time, speed=10):
        """Smooth camera follow with dead-zone (same logic as game.py)."""
        target_relative = target - self.camera.position
        center = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        offset = target_relative - center

        distance = offset.length()
        if distance > _CAM_BORDER_RADIUS:
            excess = distance - _CAM_BORDER_RADIUS
            direction = offset.normalize()
            self.camera.move(direction * excess * speed * delta_time)

    _tooltip_font = None

    def _draw_interact_tooltip(self, screen, npc):
        """Draw a small 'Press E' hint above the NPC sprite."""
        if Level1Scene._tooltip_font is None:
            Level1Scene._tooltip_font = pygame.font.SysFont("consolas", 20)
        font = Level1Scene._tooltip_font
        text = font.render("[E] Hablar", True, (255, 255, 180))
        screen_pos = npc.position - self.camera.position
        x = int(screen_pos.x) - text.get_width() // 2
        y = int(screen_pos.y) - npc._render_asset.get_height() // 2 - 24
        # subtle dark shadow
        shadow = font.render("[E] Hablar", True, (0, 0, 0))
        screen.blit(shadow, (x + 1, y + 1))
        screen.blit(text, (x, y))

