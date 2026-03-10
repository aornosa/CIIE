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
        self._audres_intro_done = False    # True after intro plays once
        self._audres_intro_tree = None
        self._audres_idle_tree  = None
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
            "7.62", 30, 0.1, 2, muzzle_offset=(35, 15),
        )
        self.player.inventory.add_weapon(self.player, weapon, "primary")
        self.player.inventory.add_item(
            ItemInstance(ItemRegistry.get("ammo_clip_762"))
        )
        for _ in range(5):
            self.player.inventory.add_item(
                ItemInstance(ItemRegistry.get("ammo_clip_762"))
            )

        # Camera
        self.camera = Camera()

        # Enemies — each gets its own CharacterController for movement
        self.enemies = []
        for pos in _ENEMY_SPAWNS:
            enemy = Enemy("assets/icon.png", pos, 0, 0.05)
            enemy._controller = CharacterController(_ENEMY_SPEED, enemy)
            self.enemies.append(enemy)

        # Boundary walls
        self._build_walls()

        # ── AUDReS-01 (Audrey) NPC ──────────────────────────────────
        from dialogs.audres_dialogs import create_audres_intro, create_audres_idle
        self._audres_intro_tree = create_audres_intro()
        self._audres_idle_tree  = create_audres_idle()
        self._audres_intro_done = False
        self.audres = NPC(
            name="AUDReS-01",
            position=(_ACX + 110, _ACY + 110),
            dialog_tree=self._audres_idle_tree,
            sprite_path="assets/characters/audres/sprite_topdown.jpg",
            scale=0.16,
        )
        self.audres.interact_radius = 150

        # DialogManager — reset the singleton to a clean state
        self._dialog_manager = DialogManager()
        self._dialog_manager.active_dialog = None
        self._dialog_manager.is_dialog_active = False
        self._dialog_manager.selected_option = 0
        self._dialog_manager._cached_dialog_surface = None
        self._dialog_manager._cached_node_id = None
        self._dialog_manager._needs_redraw = True
        # Dialog starts only when the player presses E near Audrey

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
        self._audres_intro_done = False
        self._audres_intro_tree = None
        self._audres_idle_tree  = None
        if self._dialog_manager:
            self._dialog_manager.end_dialog()
        self._dialog_manager = None
    # ── Input ─────────────────────────────────────────────────

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

        # ── Forward input to active dialog ─────────────────────────
        if self._dialog_manager and self._dialog_manager.is_dialog_active:
            self._dialog_manager.handle_input(
                pygame.key.get_pressed(),
                input_handler.keys_just_pressed,
            )
            input_handler.actions["interact"] = False   # consume so it doesn't stack
            return

        # ── Interact with Audrey ───────────────────────────────
        if (input_handler.actions.get("interact")
                and self.audres and self.player
                and self.audres.is_player_in_range(self.player.position)):
            input_handler.actions["interact"] = False
            if not self._audres_intro_done:
                # First interaction: play the scripted intro
                self._audres_intro_done = True
                self._dialog_manager.start_dialog(self._audres_intro_tree)
            else:
                # Subsequent interactions: play idle conversation
                self._audres_idle_tree.reset()
                self._dialog_manager.start_dialog(self._audres_idle_tree)

    # ── Update ────────────────────────────────────────────────

    def update(self, delta_time):
        cleanup_dead_enemies(self.enemies)
        if self.player:
            self._update_enemies(delta_time)
            self._check_enemy_contact(delta_time)

    def _update_enemies(self, delta_time):
        """Chase the player + separation steering so enemies don't stack."""
        for enemy in self.enemies:
            # ── Chase direction ─────────────────────────────────
            to_player = self.player.position - enemy.position
            if to_player.length() > 0:
                move_dir = to_player.normalize()
            else:
                move_dir = pygame.Vector2(0, 0)

            # ── Separation from other enemies ───────────────────
            sep = pygame.Vector2(0, 0)
            for other in self.enemies:
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

    # ── Render ────────────────────────────────────────────────

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

        # Movement (frozen while dialog is open)
        movement = (
            pygame.Vector2(0, 0) if dialog_active
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

        if not dialog_active:
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
        entity_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for enemy in self.enemies:
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
            # Tooltip when in range and no dialog running
            if (not dialog_active
                    and self.player
                    and self.audres.is_player_in_range(self.player.position)):
                self._draw_interact_tooltip(screen, self.audres)

        # Draw player
        self.player.draw(screen, self.camera)

        # Draw crosshair at mouse position
        screen.blit(
            pygame.transform.scale(self.crosshair, (40, 40)),
            (mouse_pos - (20, 20)),
        )

        # HUD
        ui_manager.draw_overlay(screen, self.player)
        self._draw_hud(screen, active_weapon)

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
        """Deal damage to the player when touching an enemy. 0.75s cooldown."""
        self._contact_damage_cooldown -= delta_time
        if self._contact_damage_cooldown > 0:
            return

        hits = self.player.collider.check_collision(layers=[LAYERS["enemy"]])
        if hits:
            self.player.take_damage(10)
            self._contact_damage_cooldown = 0.75

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

    # ── HUD ────────────────────────────────────────────────────

    _hud_font = None

    def _draw_hud(self, screen, active_weapon):
        """Draw health bar and ammo counter on screen."""
        if Level1Scene._hud_font is None:
            Level1Scene._hud_font = pygame.font.SysFont("consolas", 36)
        font = Level1Scene._hud_font

        # ── Health bar (top-left, safe area) ─────────────────
        bar_x, bar_y = 20, 20
        bar_w, bar_h = 400, 40
        max_hp = self.player.get_stat("max_health")
        hp = max(0, self.player.health)
        ratio = hp / max_hp if max_hp > 0 else 0

        # Background
        pygame.draw.rect(screen, (120, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        # Fill
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h))
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 3)
        # Text
        hp_text = font.render(f"HP  {int(hp)} / {int(max_hp)}", True, (255, 255, 255))
        screen.blit(hp_text, (bar_x + 8, bar_y + bar_h // 2 - hp_text.get_height() // 2))

        # ── Ammo counter (top-right, safe area) ──────────────
        if active_weapon and hasattr(active_weapon, "current_clip"):
            ammo_text = font.render(
                f"AMMO  {active_weapon.current_clip} / {active_weapon.clip_size}",
                True, (255, 0, 0),
            )
            screen.blit(ammo_text, (SCREEN_WIDTH - ammo_text.get_width() - 20, 20))
