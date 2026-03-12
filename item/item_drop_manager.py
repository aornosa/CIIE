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
        """Añade el arma al inventario como WeaponItem para que el jugador
        elija el slot desde el overlay (igual que al comprar en la tienda)."""
        from item.weapon_item import WeaponItem
        weapon_item = WeaponItem(self.weapon)
        self.weapon.parent        = player
        self.weapon.audio_emitter = player.audio_emitter
        added = player.inventory.add_item(weapon_item)
        if added:
            print(f"[PICKUP] {self.weapon.name} añadida al inventario")
        else:
            # Inventario lleno — equipar directamente en secundario como fallback
            player.inventory.secondary_weapon = self.weapon
            print(f"[PICKUP] Inventario lleno, equipada en secundario: {self.weapon.name}")
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


class HelicopterInteractable:
    """Helicóptero de extracción — interactuar aquí completa el juego."""

    INTERACT_RADIUS = 400
    TOOLTIP_COLOR   = (180, 255, 200)
    SIZE            = 500
    _IMAGE_PATH     = "assets/interactables/helicopter.png"

    def __init__(self, position, scene_ref):
        self.position     = pygame.Vector2(position)
        self._scene       = scene_ref
        self._registered  = False
        self._image       = None  # lazy-loaded on first draw
        self._register()

    def get_tooltip(self) -> str:
        return "[E] Evacuar"

    def is_player_in_range(self, player_position) -> bool:
        if not self._registered:
            return False
        return self.position.distance_to(player_position) <= self.INTERACT_RADIUS

    def interact(self, player):
        from scenes.victory_scene import VictoryScene
        scene = self._scene
        scene.director.replace(VictoryScene(
            kills=scene._total_kills,
            coins=player.coins if player else 0,
        ))

    def _register(self):
        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().register(self)
        self._registered = True

    def _unregister(self):
        from map.interactables.interaction_manager import InteractionManager
        InteractionManager().unregister(self)
        self._registered = False

    def _load_image(self):
        try:
            img = pygame.image.load(self._IMAGE_PATH).convert_alpha()
            self._image = pygame.transform.scale(img, (self.SIZE, self.SIZE))
        except Exception:
            self._image = False  # no asset — use placeholder rect

    def draw(self, screen: pygame.Surface, camera):
        if not self._registered:
            return
        sp = self.position - camera.position
        s  = self.SIZE

        if self._image is None:
            self._load_image()

        if self._image:
            screen.blit(self._image, (int(sp.x) - s // 2, int(sp.y) - s // 2))
        else:
            rect = pygame.Rect(int(sp.x) - s // 2, int(sp.y) - s // 2, s, s)
            pygame.draw.rect(screen, (30, 140, 60),  rect, border_radius=8)
            pygame.draw.rect(screen, (100, 220, 120), rect, 3, border_radius=8)