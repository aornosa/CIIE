from __future__ import annotations
import pygame
from item.item_type_data import ItemDefinition


class ItemInstance:
    def __init__(self, definition: ItemDefinition):
        self.definition = definition
        # Cooldown state — stored directly on the instance (NOT proxied to definition)
        self._cooldown_timer = 0.0

        if definition.ammo:
            self.current_ammo = definition.ammo.capacity
        else:
            self.current_ammo = None

    @property
    def cooldown_timer(self) -> float:
        return self._cooldown_timer

    @cooldown_timer.setter
    def cooldown_timer(self, value: float):
        self._cooldown_timer = value

    def update(self, delta_time: float):
        if self._cooldown_timer > 0:
            self._cooldown_timer -= delta_time
            if self._cooldown_timer < 0:
                self._cooldown_timer = 0.0

    def __getattr__(self, attr):
        # Only called when attr is NOT found on the instance itself
        return getattr(self.definition, attr)


class DroppedItem:
    INTERACT_RADIUS = 80
    TOOLTIP_COLOR   = (255, 255, 180)
    ICON_SIZE       = 40

    def __init__(self, item_instance: ItemInstance, position, velocity=None):
        self.item_instance  = item_instance
        self.position       = pygame.Vector2(position)
        self.velocity       = velocity
        self.last_drop_time = pygame.time.get_ticks()
        self._registered    = False

        self._register()

    @property
    def interact_radius(self):
        return self.INTERACT_RADIUS

    def get_tooltip(self) -> str:
        return f"[E] Recoger {self.item_instance.name}"

    def is_player_in_range(self, player_position: pygame.Vector2) -> bool:
        if not self._registered:
            return False
        if pygame.time.get_ticks() - self.last_drop_time < 1000:
            return False
        return self.position.distance_to(player_position) <= self.INTERACT_RADIUS

    def interact(self, player):
        if player.inventory.check_full():
            print(f"[PICKUP] Inventario lleno, no se puede recoger {self.item_instance.name}")
            return

        player.inventory.add_item(self.item_instance)
        print(f"[PICKUP] Recogido: {self.item_instance.name}")
        self._unregister()

        dm = player.inventory.drop_manager
        if self in dm.dropped_items:
            dm.dropped_items.remove(self)

    def _register(self):
        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().register(self)
        self._registered = True

    def _unregister(self):
        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().unregister(self)
        self._registered = False

    def draw(self, screen: pygame.Surface, camera):
        screen_pos = self.position - camera.position

        shadow_surf = pygame.Surface((self.ICON_SIZE + 8, self.ICON_SIZE + 8), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 80))
        screen.blit(shadow_surf, (screen_pos.x - self.ICON_SIZE // 2 - 4,
                                   screen_pos.y - self.ICON_SIZE // 2 + 4))

        icon = pygame.transform.scale(self.item_instance.asset,
                                      (self.ICON_SIZE, self.ICON_SIZE))
        screen.blit(icon, (screen_pos.x - self.ICON_SIZE // 2,
                            screen_pos.y - self.ICON_SIZE // 2))

        font = pygame.font.SysFont("consolas", 14)
        label = font.render(self.item_instance.name, True, self.TOOLTIP_COLOR)
        screen.blit(label, (screen_pos.x - label.get_width() // 2,
                             screen_pos.y - self.ICON_SIZE // 2 - 18))