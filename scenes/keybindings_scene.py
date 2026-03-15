import pygame
from core.scene import Scene
from ui.keybindings_menu import draw_keybindings_menu

KEYBINDINGS = {
    "Movimiento": [
        ("W / A / S / D",      "Mover al jugador"),
        ("LShift",             "Dash (si está desbloqueado)"),
    ],
    "Combate": [
        ("Clic izquierdo",     "Disparar / Atacar"),
        ("R",                  "Recargar arma"),
        ("Q",                  "Cambiar arma activa"),
    ],
    "Inventario": [
        ("1 - 6",              "Usar consumible en hotbar"),
        ("F",                  "Usar el item seleccionado"),
        ("Tab",                "Abrir / cerrar inventario"),
        ("LMB (inventario)",   "Usar consumible / elegir arma"),
        ("RMB (inventario)",   "Soltar item al suelo"),
        ("1 / 2 (overlay)",    "Asignar arma a primario / secundario"),
        ("Esc (inventario)",   "Cerrar inventario (no pausa)"),
    ],
    "Interacción": [
        ("E",                  "Interactuar"),
        ("P",                  "Abrir tienda (si está desbloqueada)"),
    ],
    "Menú": [
        ("Escape",             "Pausar"),
        ("↑ / ↓  o  W / S",   "Navegar opciones"),
        ("Enter",              "Confirmar selección"),
    ],
}


class KeybindingsScene(Scene):

    def __init__(self):
        super().__init__()
        self.categories  = list(KEYBINDINGS.keys())
        self.page        = 0   # Índice de categoría activa

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
