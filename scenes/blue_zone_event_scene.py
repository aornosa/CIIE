import pygame

import game
from core.scene import Scene
from core.collision.collision_manager import CollisionManager
from character_scripts.enemy.enemy_base import Enemy
from character_scripts.character_controller import CharacterController
from dialogs.dialog_manager import DialogManager
from dialogs.test_dialogs import create_blue_zone_intro_dialog, create_blue_zone_final_dialog
from ui.dialog import draw_dialog_ui


class BlueZoneEventScene(Scene):
    """Scripted event scene triggered by the blue zone.

    Steps:
        STEP_INTRO      – Frozen game + intro dialog (player speaks)
        STEP_ENEMY_MOVE – Frozen game + scripted enemy walks toward player
        STEP_FINAL      – Frozen game + final dialog (player speaks)
        → director.pop() → back to GameScene
    """

    STEP_INTRO = 0
    STEP_ENEMY_MOVE = 1
    STEP_FINAL = 2

    ENEMY_SPEED = 180          # px / s
    ENEMY_MOVE_DURATION = 2.5  # seconds the enemy walks before final dialog
    ENEMY_START_POS = (750, 150)  # world-space spawn point

    # ------------------------------------------------------------------

    def __init__(self, game_scene):
        super().__init__()
        self.game_scene = game_scene
        self.step = self.STEP_INTRO

        # Scripted enemy – created only for this event
        self.scripted_enemy = Enemy(
            "assets/icon.png",
            position=self.ENEMY_START_POS,
            rotation=0,
            scale=0.05,
        )
        self.enemy_controller = CharacterController(self.ENEMY_SPEED, self.scripted_enemy)
        self.enemy_move_timer = 0.0
        self.enemy_target = pygame.Vector2(0, 0)  # Set when movement starts

        # DialogManager (singleton) – start with the intro dialog
        self.dialog_manager = DialogManager()
        self.dialog_manager.start_dialog(create_blue_zone_intro_dialog())

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def handle_events(self, input_handler):
        if self.step in (self.STEP_INTRO, self.STEP_FINAL):
            self.dialog_manager.input_handler = input_handler
            self.dialog_manager.handle_input(
                input_handler.get_keys_pressed(),
                input_handler.get_keys_just_pressed(),
            )

    def update(self, delta_time):
        if self.step == self.STEP_INTRO:
            if not self.dialog_manager.is_dialog_active:
                self._start_enemy_move()

        elif self.step == self.STEP_ENEMY_MOVE:
            self._update_enemy(delta_time)

        elif self.step == self.STEP_FINAL:
            if not self.dialog_manager.is_dialog_active:
                self.director.pop()

    def render(self, screen):
        # 1 – Frozen game world
        self.game_scene.render(screen)
                                                                                                                     
        # 2 – Scripted enemy (visible in all steps)
        self.scripted_enemy.draw(screen, game.camera)

        # 3 – Dim overlay + dialog during dialog steps
        if self.step in (self.STEP_INTRO, self.STEP_FINAL):
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            draw_dialog_ui(screen, self.dialog_manager)

    def on_enter(self):
        pygame.mouse.set_visible(False)

    def on_exit(self):
        pygame.mouse.set_visible(False)
        # Remove the scripted enemy's collider so it doesn't linger in the world
        CollisionManager.dynamic_colliders.discard(self.scripted_enemy.collider)

    # ------------------------------------------------------------------
    # Internal step transitions
    # ------------------------------------------------------------------

    def _start_enemy_move(self):
        """Transition to STEP_ENEMY_MOVE: capture player position as target."""
        self.step = self.STEP_ENEMY_MOVE
        self.enemy_move_timer = 0.0
        # Target = player's current (frozen) world position
        self.enemy_target = pygame.Vector2(game.player.position)

    def _update_enemy(self, delta_time):
        self.enemy_move_timer += delta_time

        direction = self.enemy_target - self.scripted_enemy.position
        if direction.length() > 8:
            # Rotate enemy to face movement direction
            self.scripted_enemy.set_rotation(
                direction.angle_to(pygame.Vector2(0, -1))
            )
            self.enemy_controller.move(direction, delta_time)

        if self.enemy_move_timer >= self.ENEMY_MOVE_DURATION:
            self._start_final_dialog()

    def _start_final_dialog(self):
        """Transition to STEP_FINAL: show closing dialog."""
        self.step = self.STEP_FINAL
        self.dialog_manager.start_dialog(create_blue_zone_final_dialog())
