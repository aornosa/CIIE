"""
Escena de nivel completado — reutilizable para todos los niveles.

Uso:
    LevelCompleteScene(
        frozen_frame   = self._last_frame,   # Surface o None
        level_name     = "Nivel 1",
        stats          = {"kills": 35, "coins": 350},
        next_scene_class = Level2Scene,      # None → Menú Principal
    )
"""
import pygame
from core.scene import Scene
from ui.level_complete_screen import draw_level_complete_screen


class LevelCompleteScene(Scene):
    """
    Pantalla de victoria mostrada al completar un nivel.

    Parámetros
    ----------
    frozen_frame      – último fotograma renderizado del nivel (puede ser None)
    level_name        – nombre del nivel, p.ej. "Nivel 1"
    stats             – dict con claves: kills, coins
    next_scene_class  – clase Scene a instanciar al pulsar "Continuar"
                        (None → vuelve al Menú Principal)
    """

    _FADE_DURATION = 1.2   # segundos del fade-in

    def __init__(self, frozen_frame, level_name, stats, next_scene_class=None):
        super().__init__()
        self.frozen_frame     = frozen_frame
        self.level_name       = level_name
        self.stats            = stats
        self.next_scene_class = next_scene_class
        self.options          = ["Continuar", "Menú Principal"]
        self.selected         = 0
        self._fade_timer      = 0.0
        self._ready           = False   # input bloqueado hasta que acaba el fade

    # ── Lifecycle ────────────────────────────────────────────

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def on_exit(self):
        pygame.mouse.set_visible(False)

    # ── Input ────────────────────────────────────────────────

    def handle_events(self, input_handler):
        if not self._ready:
            return

        if (input_handler.keys_just_pressed.get(pygame.K_UP) or
                input_handler.keys_just_pressed.get(pygame.K_w)):
            self.selected = (self.selected - 1) % len(self.options)

        if (input_handler.keys_just_pressed.get(pygame.K_DOWN) or
                input_handler.keys_just_pressed.get(pygame.K_s)):
            self.selected = (self.selected + 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._confirm()

    # ── Update ───────────────────────────────────────────────

    def update(self, delta_time):
        if not self._ready:
            self._fade_timer += delta_time
            if self._fade_timer >= self._FADE_DURATION:
                self._fade_timer = self._FADE_DURATION
                self._ready = True

    # ── Render ───────────────────────────────────────────────

    def render(self, screen):
        alpha = int(255 * (self._fade_timer / self._FADE_DURATION))
        draw_level_complete_screen(
            screen,
            self.frozen_frame,
            self.level_name,
            self.stats,
            self.options,
            self.selected,
            alpha,
        )

    # ── Selección ────────────────────────────────────────────

    def _confirm(self):
        option = self.options[self.selected]
        if option == "Continuar":
            if self.next_scene_class is not None:
                self.director.replace(self.next_scene_class())
            else:
                from scenes.main_menu_scene import MainMenuScene
                self.director.replace(MainMenuScene())
        elif option == "Menú Principal":
            from scenes.main_menu_scene import MainMenuScene
            self.director.replace(MainMenuScene())
