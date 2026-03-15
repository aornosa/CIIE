import os
import pygame
from character_scripts.character import Character
from map.interactables.interactable import Interactable

class NPC(Character, Interactable):
    def __init__(self, name, position, dialog_tree=None, sprite_path=None, health=100,
                 interact_radius=80, scale=1.0):
        if sprite_path is None:
            sprite_path = self._create_placeholder_sprite_file()

        Character.__init__(
            self,
            asset=sprite_path,
            position=pygame.Vector2(position),
            rotation=0,
            scale=scale,
            name=name,
            health=health,
        )

        interact_text = f"Press E to talk to {name}" if dialog_tree else f"Press E to interact with {name}"
        Interactable.__init__(
            self,
            name=name,
            description="",
            interact_text=interact_text,
            interact_radius=interact_radius,
        )

        self.dialog_tree = dialog_tree

        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().register(self)

    @staticmethod
    def _create_placeholder_sprite_file():
        # Genera un placeholder azul solo si no existe ya en disco
        temp_path = os.path.join("assets/player", "npc_placeholder.png")
        if not os.path.exists(temp_path):
            sprite = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.rect(sprite, (0, 100, 255), (0, 0, 40, 40))
            pygame.image.save(sprite, temp_path)
        return temp_path

    def interact(self, player):
        if self.dialog_tree:
            from dialogs.dialog_manager import DialogManager
            DialogManager().start_dialog(self.dialog_tree)

    def destroy(self):
        from map.interactables.interaction_manager import InteractionManager
        from core.collision.collision_manager import CollisionManager
        InteractionManager().unregister(self)
        if hasattr(self, 'collider') and self.collider is not None:
            CollisionManager.dynamic_colliders.discard(self.collider)
            self.collider = None

    def update(self, delta_time):
        # Actualiza y limpia efectos de estado expirados
        for effect_name in list(self.effects.keys()):
            effect = self.effects[effect_name]
            if hasattr(effect, 'update'):
                effect.update(delta_time)
            if hasattr(effect, 'is_expired') and effect.is_expired():
                self.remove_effect(effect_name)