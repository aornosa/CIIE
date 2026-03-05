import pygame
from character_scripts.character import Character
from map.interactables.interactable import Interactable


class NPC(Character, Interactable):

    def __init__(self, name, position, dialog_tree=None, sprite_path=None, health=100,
                 interact_radius=80):
        if sprite_path is None:
            sprite_path = self._create_placeholder_sprite_file()

        Character.__init__(
            self,
            asset=sprite_path,
            position=pygame.Vector2(position),
            rotation=0,
            scale=1.0,
            name=name,
            health=health
        )

        interact_text = f"Press E to talk to {name}" if dialog_tree else f"Press E to interact with {name}"
        Interactable.__init__(
            self,
            name=name,
            description="",
            interact_text=interact_text,
            interact_radius=interact_radius
        )

        self.dialog_tree = dialog_tree

        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().register(self)

    def _create_placeholder_sprite_file(self):
        import os

        sprite = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(sprite, (0, 100, 255), (0, 0, 40, 40))  

        temp_dir = "assets/player"  
        temp_path = os.path.join(temp_dir, "npc_placeholder.png")

        if not os.path.exists(temp_path):
            pygame.image.save(sprite, temp_path)

        return temp_path

    def interact(self, player):
        if self.dialog_tree:
            from dialogs.dialog_manager import DialogManager
            dialog_manager = DialogManager()
            dialog_manager.start_dialog(self.dialog_tree)
        else:
            print(f"{self.name} doesn't have anything to say.")

    def update(self, delta_time):
        for effect_name in list(self.effects.keys()):
            effect = self.effects[effect_name]
            if hasattr(effect, 'update'):
                effect.update(delta_time)
            if hasattr(effect, 'is_expired') and effect.is_expired():
                self.remove_effect(effect_name)