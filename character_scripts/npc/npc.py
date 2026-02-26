import pygame
from character_scripts.character import Character


class NPC(Character):
    """
    Non-Player Character class that inherits from Character.
    Represents NPCs that can be interacted with for dialog.
    """
    
    def __init__(self, name, position, dialog_tree=None, sprite_path=None, health=100):
        """
        Initialize an NPC.
        
        Args:
            name: NPC name
            position: Initial position (x, y)
            dialog_tree: Optional dialog tree for conversations (if None, NPC won't have dialog)
            sprite_path: Optional path to sprite image (if None, creates placeholder)
            health: NPC health (default 100)
        """
        # Si no hay sprite_path, crear un placeholder temporal
        if sprite_path is None:
            sprite_path = self._create_placeholder_sprite_file()
        
        super().__init__(
            asset=sprite_path,
            position=pygame.Vector2(position),
            rotation=0,
            scale=1.0,
            name=name,
            health=health
        )
        
        self.dialog_tree = dialog_tree
        self.interact_radius = 50
        
        # Set interact text based on whether NPC has dialog
        if dialog_tree:
            self.interact_text = f"Press E to talk to {name}"
        else:
            self.interact_text = f"Press E to interact with {name}"
        
    def _create_placeholder_sprite_file(self):
        """
        Create a temporary placeholder sprite and save it.
        Returns the path to the placeholder image.
        
        Object expects a file path, so we create a temporary sprite file
        instead of returning a Surface directly.
        """
        import os
        
        # Create placeholder sprite - simple blue square
        sprite = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(sprite, (0, 100, 255), (0, 0, 40, 40))  # Blue square
        
        # Save to temp file
        temp_dir = "assets/player"  # Reutilizamos un directorio existente
        temp_path = os.path.join(temp_dir, "npc_placeholder.png")
        
        # Solo crear el archivo si no existe
        if not os.path.exists(temp_path):
            pygame.image.save(sprite, temp_path)
        
        return temp_path
    
    def interact(self, player):
        """
        Initiate dialog with the NPC (if available).
        
        Args:
            player: The player character interacting with this NPC
        """
        if self.dialog_tree:
            from dialogs.dialog_manager import DialogManager
            dialog_manager = DialogManager()
            dialog_manager.start_dialog(self.dialog_tree)
        else:
            # NPC sin diálogo - puedes agregar lógica personalizada aquí
            print(f"{self.name} doesn't have anything to say.")
    
    def is_player_in_range(self, player_position):
        """
        Check if player is within interaction range.
        
        Args:
            player_position: Position of the player (pygame.Vector2)
            
        Returns:
            bool: True if player is in range
        """
        distance = self.position.distance_to(player_position)
        return distance <= self.interact_radius
    
    def get_tooltip(self):
        """Get the interaction tooltip text."""
        return self.interact_text
    
    def update(self, delta_time):
        """
        Update NPC state.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        # Update effects and status
        for effect_name in list(self.effects.keys()):
            effect = self.effects[effect_name]
            if hasattr(effect, 'update'):
                effect.update(delta_time)
            if hasattr(effect, 'is_expired') and effect.is_expired():
                self.remove_effect(effect_name)
