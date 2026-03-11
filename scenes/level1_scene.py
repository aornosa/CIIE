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
        self._contact_damage_cooldown = 0.0  # seconds until next contact hit
        self.audres = None
        self._dialog_manager = None
        self._audres_intro_tree  = None
        self._cutscene_active    = False
        self._cutscene_phase     = "idle"   # "walking" → "dialog" → done
        self._audres_walk_target = None
        # Wave-clear shop hint
        self._enemies_spawned     = False   # True once _finish_cutscene() runs
        self._shop_hint_triggered = False   # fires only once per run
        self._wave_clear_timer    = -1.0    # counts down from 1.5 s
        # Sistema de oleadas estructurado (arranca tras el diálogo de la tienda)
        self._wave_manager           = None   # Level1WaveManager, creado tras el shop hint
        # Fin de oleadas → nivel completo
        self._wave2_clear_triggered  = False  # True once congratulation dialog starts
        self._wave2_clear_timer      = -1.0   # 1.5 s delay before Audrey congratulates
        self._going_level_complete   = False  # True once we navigate to LevelCompleteScene
        self._total_kills            = 0      # running kill count for the stats screen
        self.crosshair = pygame.image.load("assets/crosshair.png").convert_alpha()
        self.ads_effect = StatusEffect(
            "assets/effects/ads", "Aiming Down Sights", {"speed": -70}, -1
        )

    # ── Scene lifecycle ───────────────────────────────────────

    def on_enter(self):
        MonoliteBehaviour.time_scale = 1.0
        pygame.mouse.set_visible(False)
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

        # ── AUDReS-01 (Audrey) — spawns at the top of the arena, walks in ──
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
        """Create four static terrain colliders that form the square arena.

        Rectangle(cx, cy, half_h, half_w)  — all values are center + half-extents.
        CharacterController.move() already resolves terrain collisions on both
        axes, so no extra logic is needed here.
        """
        cx, cy = _ACX, _ACY
        h, t   = _ARENA_HALF, _WALL_THICK

        wall_defs = [
            # (center_x,          center_y,          half_h, half_w )
            (cx,                  cy - h - t // 2,   t // 2, h + t  ),  # top
            (cx,                  cy + h + t // 2,   t // 2, h + t  ),  # bottom
            (cx - h - t // 2,    cy,                 h,      t // 2 ),  # left
            (cx + h + t // 2,    cy,                 h,      t // 2 ),  # right
        ]
        for wx, wy, wh, ww in wall_defs:
            Collider(
                object(),                        # static walls need no logic owner
                Rectangle(wx, wy, wh, ww),
                layer=LAYERS["terrain"],
                static=True,
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
        self._wave2_clear_triggered  = False
        self._wave2_clear_timer      = -1.0
        self._going_level_complete   = False
        self._total_kills            = 0
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
        if killed > 0 and self.player:
            self.player.add_coins(killed * 10)
            self._total_kills += killed
        if self.player:
            self._update_enemies(delta_time)
            self._check_enemy_contact(delta_time)

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
        if (self._shop_hint_triggered
                and self._wave_manager is None
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
            ))

    def _update_enemies(self, delta_time):
        """Chase the player + separation steering so enemies don't stack."""
        enemies = self._wave_manager.enemies if self._wave_manager is not None else self.enemies
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

            enemy._controller.move(move_dir, delta_time)

            # ── Rotate enemy toward player ──────────────────────
            if to_player.length() > 0:
                enemy.rotation = to_player.angle_to(pygame.Vector2(0, -1))

            # ── Tick hit-flash timer ────────────────────────────
            enemy._hit_flash_timer = max(0.0, enemy._hit_flash_timer - delta_time)

    _AUDRES_WALK_SPEED = 400   # px/s during the intro walk

    def _create_wave_manager(self):
        """Instancia Level1WaveManager tras el diálogo del shop hint.

        Modifica wave_config, rest_time o spawn_duration aquí para ajustar
        la dificultad del nivel:
          wave_config     — lista con el nº de enemigos por oleada
          rest_time       — segundos de descanso entre oleadas
          spawn_duration  — segundos para distribuir el spawn de una oleada completa
        """
        from runtime.level1_wave_manager import Level1WaveManager
        self._wave_manager = Level1WaveManager(
            arena_center=(_ACX, _ACY),
            arena_half=_ARENA_HALF,
            wave_config=[20, 25, 30, 40, 50],   # enemigos por oleada
            rest_time=3.0,                       # segundos de descanso entre oleadas
            spawn_duration=8.0,                  # segundos para spawnear toda una oleada
            enemy_speed=_ENEMY_SPEED,
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
                        active_weapon.shoot()

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

        # Camera follow
        self._camera_follow(self.player.position, delta_time)

        # Draw enemies
        active_enemies = self._wave_manager.enemies if self._wave_manager is not None else self.enemies
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
        ui_manager.draw_overlay(screen, self.player, wave_manager=self._wave_manager, delta_time=delta_time)

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

            # ── Player death ───────────────────────────────────
            if not self.player.is_alive():
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

