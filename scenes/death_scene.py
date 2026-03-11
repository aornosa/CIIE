import pygame
from core.scene import Scene
from ui.death_screen import draw_death_screen


class DeathScene(Scene):
    """Death screen — stacked on top of Level1Scene via director.replace()."""

    _FADE_DURATION = 1.2   # seconds for the fade-in

    def __init__(self, frozen_frame, stats):
        """
        frozen_frame  – last rendered Surface from Level1Scene (may be None)
        stats         – dict: {"kills": int, "coins": int}
        """
        super().__init__()
        self.frozen_frame = frozen_frame
        self.stats = stats
        self.options = ["Reintentar", "Menú Principal"]
        self.selected = 0
        self._fade_timer = 0.0          # counts up to _FADE_DURATION
        self._ready = False             # input blocked until fade completes

    # ── Lifecycle ────────────────────────────────────────────

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def on_exit(self):
        pygame.mouse.set_visible(False)

    # ── Input ────────────────────────────────────────────────

    def handle_events(self, input_handler):
        if not self._ready:
            return

        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            self.selected = (self.selected - 1) % len(self.options)

        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
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
        draw_death_screen(
            screen,
            self.frozen_frame,
            self.stats,
            self.options,
            self.selected,
            alpha,
        )

    # ── Selection ────────────────────────────────────────────

    def _confirm(self):
        option = self.options[self.selected]
        if option == "Reintentar":
            from scenes.level1_scene import Level1Scene
            self.director.replace(Level1Scene())
        elif option == "Menú Principal":
            from scenes.main_menu_scene import MainMenuScene
            self.director.replace(MainMenuScene())
