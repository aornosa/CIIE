"""
Nivel 1 — primer nivel de prueba.
5 enemigos, sin mapa, fondo sólido.
Todo se crea desde cero cada vez que se entra al nivel.
"""
import pygame

from core.audio.audio_manager import AudioManager
from core.camera import Camera
from core.collision.collision_manager import CollisionManager
from core.collision.quadtree import Rectangle
from core.monolite_behaviour import MonoliteBehaviour
from core.scene import Scene
from core.status_effects import StatusEffect
from character_scripts.character_controller import CharacterController
from character_scripts.enemy.enemy_base import Enemy
from character_scripts.player.player import Player
from game_math import utils as math
from item.item_instance import ItemInstance
from item.item_loader import ItemRegistry
from runtime.round_manager import cleanup_dead_enemies
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, _CAM_BORDER_RADIUS
from ui import ui_manager
from weapons.ranged.ranged import Ranged


# ── Background colour (no map yet) ─────────────────────────
_BG_COLOR = (30, 30, 40)

# ── Enemy spawn positions ──────────────────────────────────
_ENEMY_SPAWNS = [
    (400, 250),
    (700, 450),
    (200, 550),
    (800, 200),
    (550, 700),
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

        # Enemies
        self.enemies = []
        for pos in _ENEMY_SPAWNS:
            self.enemies.append(Enemy("assets/icon.png", pos, 0, 0.05))

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

    # ── Input ─────────────────────────────────────────────────

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            from scenes.pause_scene import PauseScene
            self.director.push(PauseScene(self))
            return

    # ── Update ────────────────────────────────────────────────

    def update(self, delta_time):
        cleanup_dead_enemies(self.enemies)

    # ── Render ────────────────────────────────────────────────

    def render(self, screen):
        im = self.director._input_handler
        delta_time = self.director.clock.get_time() / 1000.0

        # Background
        screen.fill(_BG_COLOR)

        # Mouse position (for crosshair & aiming)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # Movement
        movement = pygame.Vector2(im.actions["move_x"], im.actions["move_y"])

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

        # Swap weapon
        if im.actions["swap_weapon"]:
            im.actions["swap_weapon"] = False
            self.player.inventory.swap_weapons()

        # Reload
        if im.actions["reload"]:
            im.actions["reload"] = False
            if active_weapon is not None:
                active_weapon.reload()

        # ── Aiming & Shooting ─────────────────────────────────
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
        screen.blit(entity_surface, (0, 0))

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

        # Cache frame for PauseScene overlay
        self._last_frame = screen.copy()

    # ── Helpers ────────────────────────────────────────────────

    def get_last_frame(self):
        """Return the last rendered frame (used by PauseScene)."""
        return self._last_frame

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
