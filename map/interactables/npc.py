from map.interactables.interactable import Interactable
import pygame

class NPC(Interactable):
    def __init__(self, name, dialog_tree, position, sprite_path=None):
        super().__init__(name, f"Talk to {name}", f"Press E to talk to {name}")
        self.dialog_tree = dialog_tree
        self.position = pygame.Vector2(position)
        self.sprite = None
        self.sprite_rect = None
        
        if sprite_path:
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
                self.sprite_rect = self.sprite.get_rect(center=position)
            except:
                print(f"Warning: Could not load sprite for NPC {name}")
                self._create_placeholder_sprite()
        else:
            self._create_placeholder_sprite()
    
    def _create_placeholder_sprite(self):
        self.sprite = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite, (255, 200, 150), (20, 15), 12)  # Head
        pygame.draw.rect(self.sprite, (100, 100, 200), (12, 25, 16, 25))  # Body
        pygame.draw.rect(self.sprite, (100, 100, 200), (10, 50, 8, 10))  # Left leg
        pygame.draw.rect(self.sprite, (100, 100, 200), (22, 50, 8, 10))  # Right leg
        self.sprite_rect = self.sprite.get_rect(center=self.position)
    
    def interact(self, player):
        from dialogs.dialog_manager import DialogManager
        dialog_manager = DialogManager()
        dialog_manager.start_dialog(self.dialog_tree)
    
    def draw(self, screen, camera):
        if self.sprite and self.sprite_rect:
            draw_pos = self.position - camera.position
            temp_rect = self.sprite_rect.copy()
            temp_rect.center = draw_pos
            screen.blit(self.sprite, temp_rect)
    
    def is_player_in_range(self, player_position):
        distance = self.position.distance_to(player_position)
        return distance <= self.interact_radius
