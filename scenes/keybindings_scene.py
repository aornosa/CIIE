import pygame
from core.scene import Scene
from ui.keybindings_menu import draw_keybindings_menu

# ---------------------------------------------------------------------------
# KEYBINDINGS CONFIG
# ---------------------------------------------------------------------------
KEYBINDINGS = {
    "Movimiento": [
        ("W / A / S / D",      "Mover al jugador"),
        ("LCtrl  (mantener)",  "Mover la cámara libremente"),
    ],
    "Combate": [
        ("Clic izquierdo",     "Disparar / Atacar"),
        ("Clic derecho",       "Apuntar (ADS)"),
        ("R",                  "Recargar arma"),
        ("Q",                  "Cambiar arma activa"),
    ],
    "Inventario": [
        ("1 – 6",              "Seleccionar hueco del inventario"),
        ("F",                  "Usar el item seleccionado"),
        ("Tab",                "Abrir / cerrar inventario"),
    ],
    "Interacción": [
        ("E",                  "Interactuar / hablar con NPC"),
        ("P",                  "Abrir tienda"),
    ],
    "Menú": [
        ("Escape",             "Pausar / volver atrás"),
        ("↑ / ↓  o  W / S",   "Navegar opciones"),
        ("Enter",              "Confirmar selección"),
    ],
}


class KeybindingsScene(Scene):
    """Pantalla de controles — navegable por categorías con ← →."""

    def __init__(self):
        super().__init__()
        self.categories  = list(KEYBINDINGS.keys())
        self.page        = 0   # Índice de categoría activa

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            self.director.pop()
            return

        if (input_handler.keys_just_pressed.get(pygame.K_LEFT) or
                input_handler.keys_just_pressed.get(pygame.K_a)):
            self.page = (self.page - 1) % len(self.categories)

        if (input_handler.keys_just_pressed.get(pygame.K_RIGHT) or
                input_handler.keys_just_pressed.get(pygame.K_d)):
            self.page = (self.page + 1) % len(self.categories)

        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self.director.pop()

    def update(self, delta_time):
        pass

    def render(self, screen):
        category = self.categories[self.page]
        entries  = KEYBINDINGS[category]
        draw_keybindings_menu(
            screen,
            categories=self.categories,
            active_page=self.page,
            entries=entries,
        )

    def on_enter(self):
        pygame.mouse.set_visible(True)
