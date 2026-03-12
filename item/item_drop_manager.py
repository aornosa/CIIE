import pygame
from core.monolite_behaviour import MonoliteBehaviour
from item.item_instance import DroppedItem
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class DropManager(MonoliteBehaviour):
    def __init__(self):
        MonoliteBehaviour.__init__(self)
        self.dropped_items: list[DroppedItem] = []

    def drop_item(self, item, position, velocity=None):
        dropped = DroppedItem(item, position, velocity)
        self.dropped_items.append(dropped)
        print(f"[DROP] {item.name} en {position}")
        return dropped

    def draw(self, screen, camera):
        for item in self.dropped_items:
            item.draw(screen, camera)


class DroppedWeapon:
    """Arma colocada en el escenario que el jugador puede recoger con [E]."""

    INTERACT_RADIUS = 100
    ICON_SIZE       = 48
    TOOLTIP_COLOR   = (255, 255, 180)

    def __init__(self, weapon, position, slot: str = "primary"):
        self.weapon   = weapon
        self.position = pygame.Vector2(position)
        self.slot     = slot
        self._registered = False
        self._register()

    def get_tooltip(self) -> str:
        return f"[E] Recoger {self.weapon.name}"

    def is_player_in_range(self, player_position) -> bool:
        if not self._registered:
            return False
        return self.position.distance_to(player_position) <= self.INTERACT_RADIUS

    def interact(self, player):
        """Guarda el arma en el slot secundario (sin tocar el primario).
        Si el secundario ya estaba ocupado, el arma antigua queda tirada."""
        target_slot = self.slot   # "secondary" por defecto desde la escena
        if target_slot == "primary":
            player.inventory.primary_weapon = self.weapon
        else:
            player.inventory.secondary_weapon = self.weapon
        self.weapon.parent         = player
        self.weapon.audio_emitter  = player.audio_emitter
        print(f"[PICKUP] Arma recogida: {self.weapon.name}")
        self._unregister()

    def _register(self):
        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().register(self)
        self._registered = True

    def _unregister(self):
        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().unregister(self)
        self._registered = False

    def draw(self, screen: pygame.Surface, camera):
        if not self._registered:
            return
        screen_pos = self.position - camera.position

        shadow = pygame.Surface((self.ICON_SIZE + 8, self.ICON_SIZE + 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        screen.blit(shadow, (screen_pos.x - self.ICON_SIZE // 2 - 4,
                              screen_pos.y - self.ICON_SIZE // 2 + 4))

        icon = pygame.transform.scale(self.weapon.asset, (self.ICON_SIZE, self.ICON_SIZE))
        screen.blit(icon, (screen_pos.x - self.ICON_SIZE // 2,
                            screen_pos.y - self.ICON_SIZE // 2))

        font  = pygame.font.SysFont("consolas", 14)
        label = font.render(self.weapon.name, True, self.TOOLTIP_COLOR)
        screen.blit(label, (screen_pos.x - label.get_width() // 2,
                             screen_pos.y - self.ICON_SIZE // 2 - 18))