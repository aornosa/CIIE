import pygame
from core.monolite_behaviour import MonoliteBehaviour

class DialogManager(MonoliteBehaviour):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self.active_dialog    = None
            self.is_dialog_active = False
            self.selected_option  = 0
            self.input_handler    = None
            self._cached_dialog_surface  = None
            self._cached_node_id         = None
            self._cached_selected_option = None
            self._needs_redraw           = True
            self._initialized = True

    def start_dialog(self, dialog_tree):
        self.active_dialog    = dialog_tree
        self.active_dialog.reset()
        self.is_dialog_active = True
        self.selected_option  = 0
        self._invalidate_cache()

    def end_dialog(self):
        self.active_dialog    = None
        self.is_dialog_active = False
        self.selected_option  = 0
        self._invalidate_cache()
        # Consume interact para evitar re-trigger inmediato al cerrar el diálogo
        if self.input_handler:
            self.input_handler.actions["interact"] = False

    def advance_dialog(self):
        if not self.is_dialog_active or not self.active_dialog:
            return
        current = self.active_dialog.get_current_node()
        if current.on_complete:
            current.on_complete()
        if current.options:
            return
        if current.next_node:
            self.active_dialog.advance_to_node(current.next_node)
            self.selected_option = 0
            self._invalidate_cache()
        else:
            self.end_dialog()

    def choose_option(self, option_index):
        if not self.is_dialog_active or not self.active_dialog:
            return
        current = self.active_dialog.get_current_node()
        if not current.options or option_index >= len(current.options):
            return
        if current.on_complete:
            current.on_complete()
        _, next_node_id = current.options[option_index]
        if next_node_id:
            self.active_dialog.advance_to_node(next_node_id)
            self.selected_option = 0
            self._invalidate_cache()
        else:
            self.end_dialog()

    def handle_input(self, keys_pressed, keys_just_pressed):
        if not self.is_dialog_active:
            return
        current = self.active_dialog.get_current_node()
        if current.options:
            if keys_just_pressed.get(pygame.K_DOWN) or keys_just_pressed.get(pygame.K_s):
                self.selected_option = (self.selected_option + 1) % len(current.options)
                self._invalidate_cache()
            elif keys_just_pressed.get(pygame.K_UP) or keys_just_pressed.get(pygame.K_w):
                self.selected_option = (self.selected_option - 1) % len(current.options)
                self._invalidate_cache()
            elif keys_just_pressed.get(pygame.K_RETURN) or keys_just_pressed.get(pygame.K_e):
                self.choose_option(self.selected_option)
        else:
            if keys_just_pressed.get(pygame.K_RETURN) or keys_just_pressed.get(pygame.K_e):
                self.advance_dialog()

    def get_current_node(self):
        if self.is_dialog_active and self.active_dialog:
            return self.active_dialog.get_current_node()
        return None

    def _invalidate_cache(self):
        self._needs_redraw = True

    def get_cached_surface(self):
        # Devuelve la superficie cacheada si sigue siendo válida
        if not self._needs_redraw and self._cached_dialog_surface:
            return self._cached_dialog_surface
        return None

    def set_cached_surface(self, surface):
        self._cached_dialog_surface = surface
        self._needs_redraw = False