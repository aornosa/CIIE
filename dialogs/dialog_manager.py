from core.monolite_behaviour import MonoliteBehaviour
import pygame

class DialogManager(MonoliteBehaviour):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DialogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self.active_dialog = None
            self.is_dialog_active = False
            self.selected_option = 0
            self.input_handler = None
            # Cache optimization
            self._cached_dialog_surface = None
            self._cached_node_id = None
            self._cached_selected_option = None
            self._needs_redraw = True
            self._initialized = True
    
    def start_dialog(self, dialog_tree):
        self.active_dialog = dialog_tree
        self.active_dialog.reset()
        self.is_dialog_active = True
        self.selected_option = 0
        self._invalidate_cache()
        print(f"Dialog started: {dialog_tree.get_current_node().speaker}")
    
    def end_dialog(self):
        self.active_dialog = None
        self.is_dialog_active = False
        self.selected_option = 0
        self._invalidate_cache()
        
        # Consume interact action to prevent immediate re-trigger
        if self.input_handler:
            self.input_handler.actions["interact"] = False
        
        print("Dialog ended")
    
    def advance_dialog(self):
        if not self.is_dialog_active or not self.active_dialog:
            return
        
        current_node = self.active_dialog.get_current_node()
        
        if current_node.on_complete:
            current_node.on_complete()
        
        if current_node.options:
            return
        
        if current_node.next_node:
            self.active_dialog.advance_to_node(current_node.next_node)
            self.selected_option = 0
            self._invalidate_cache()
        else:
            self.end_dialog()
    
    def choose_option(self, option_index):
        if not self.is_dialog_active or not self.active_dialog:
            return
        
        current_node = self.active_dialog.get_current_node()
        
        if not current_node.options or option_index >= len(current_node.options):
            return
        
        if current_node.on_complete:
            current_node.on_complete()
        
        _, next_node_id = current_node.options[option_index]
        
        if next_node_id:
            self.active_dialog.advance_to_node(next_node_id)
            self.selected_option = 0
            self._invalidate_cache()
        else:
            self.end_dialog()
    
    def handle_input(self, keys_pressed, keys_just_pressed):
        if not self.is_dialog_active:
            return
        
        current_node = self.active_dialog.get_current_node()
        
        if current_node.options:
            if keys_just_pressed.get(pygame.K_DOWN, False) or keys_just_pressed.get(pygame.K_s, False):
                self.selected_option = (self.selected_option + 1) % len(current_node.options)
                self._invalidate_cache()
            elif keys_just_pressed.get(pygame.K_UP, False) or keys_just_pressed.get(pygame.K_w, False):
                self.selected_option = (self.selected_option - 1) % len(current_node.options)
                self._invalidate_cache()
            elif keys_just_pressed.get(pygame.K_RETURN, False) or keys_just_pressed.get(pygame.K_e, False):
                self.choose_option(self.selected_option)
        else:
            if keys_just_pressed.get(pygame.K_RETURN, False) or keys_just_pressed.get(pygame.K_e, False):
                self.advance_dialog()
    
    def get_current_node(self):
        if self.is_dialog_active and self.active_dialog:
            return self.active_dialog.get_current_node()
        return None
    
    def _invalidate_cache(self):
        """Mark the dialog UI cache as dirty, forcing a redraw."""
        self._needs_redraw = True
    
    def get_cached_surface(self):
        """Get the cached dialog surface if valid, None otherwise."""
        if not self._needs_redraw and self._cached_dialog_surface:
            return self._cached_dialog_surface
        return None
    
    def set_cached_surface(self, surface):
        """Cache the rendered dialog surface."""
        self._cached_dialog_surface = surface
        self._needs_redraw = False
