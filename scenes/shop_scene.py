import pygame
from core.scene import Scene
from ui.shop_menu import draw_shop_menu
from item.item_instance import ItemInstance
from item.item_loader import ItemRegistry

SHOP_CATALOG = [
    {"name": "Vida Reforzada",    "desc": "+25 Vida máxima",                        "cost": 200, "type": "stat",       "stat": "max_health", "value": 25},
    {"name": "Botas de Acero",    "desc": "+30 Velocidad",                           "cost": 100, "type": "stat",       "stat": "speed",      "value": 30},
    {"name": "Botiquín de Campo", "desc": "Cura 50 HP al instante",                  "cost": 75,  "type": "heal",       "value": 50},
    {"name": "Cargador Ampliado", "desc": "+5 balas al cargador (arma activa)",      "cost": 150, "type": "weapon",     "attr": "clip_size",  "value": 5},
    {"name": "Gatillo Mejorado",  "desc": "-0.03s entre disparos (arma activa)",     "cost": 175, "type": "weapon",     "attr": "fire_rate",  "value": -0.03},
    {"name": "Munición Perforante","desc": "+15 daño por bala (arma activa)",        "cost": 200, "type": "weapon",     "attr": "damage",     "value": 15},
    {"name": "MP5",               "desc": "Subfusil 9mm · 30 balas · Va al inventario",  "cost": 350, "type": "buy_weapon", "weapon_class": "MP5",   "unique": True},
    {"name": "SPAS-12",           "desc": "Escopeta 12ga · 8 balas · Va al inventario",  "cost": 500, "type": "buy_weapon", "weapon_class": "SPAS12","unique": True},
    {"name": "AK-47 (extra)",     "desc": "Rifle 7.62mm · 60 balas · Va al inventario",  "cost": 600, "type": "buy_weapon", "weapon_class": "AK47",  "unique": True},
    {"name": "Habilidad: Dash",   "desc": "Impulso rápido (CD: 3s)",                "cost": 150, "type": "item",       "item_id": "dash_ability", "unique": True},
]


def _build_weapon(weapon_class: str):
    """Instancia un arma por nombre de clase."""
    if weapon_class == "MP5":
        from weapons.ranged.ranged_types import MP5;       return MP5()
    if weapon_class == "SPAS12":
        from weapons.ranged.ranged_types import SPAS12;    return SPAS12()
    if weapon_class == "AK47":
        from weapons.ranged.ranged_types import AK47;      return AK47()
    if weapon_class == "TacticalKnife":
        from weapons.melee.melee_types import TacticalKnife; return TacticalKnife()
    if weapon_class == "Baton":
        from weapons.melee.melee_types import Baton;       return Baton()
    return None


class ShopScene(Scene):
    def __init__(self, game_scene, player):
        super().__init__()
        self.game_scene    = game_scene
        self.player        = player
        self.catalog       = SHOP_CATALOG
        self.selected      = 0
        self.total_options = len(self.catalog) + 1
        self.message       = ""
        self.message_timer = 0.0

    def on_enter(self):
        pygame.mouse.set_visible(True)
        from core.audio.music_manager import MusicManager
        MusicManager.instance().set_category("idle")

    def on_exit(self):
        pygame.mouse.set_visible(False)

    def handle_events(self, input_handler):
        if input_handler.actions.get("shop") or input_handler.actions.get("pause"):
            input_handler.actions["shop"]  = False
            input_handler.actions["pause"] = False
            self.director.pop()
            return
        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            self.selected = (self.selected - 1) % self.total_options
        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
            self.selected = (self.selected + 1) % self.total_options
        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select_option()

    def update(self, delta_time):
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = ""

    def render(self, screen):
        last_frame = self.game_scene.get_last_frame()
        if last_frame is not None:
            screen.blit(last_frame, (0, 0))
        draw_shop_menu(screen, self.catalog, self.selected,
                       self.player.coins, self.message, self.player)

    def _fail(self, entry, msg: str) -> bool:
        """Reembolsa el coste y muestra un mensaje de error."""
        self.player.coins += entry["cost"]
        self.message       = msg
        self.message_timer = 2.0
        return False

    def _select_option(self):
        if self.selected >= len(self.catalog):
            self.director.pop()
            return
        entry   = self.catalog[self.selected]
        self.message = ""
        success = self._purchase(entry)
        if success:
            self.message       = f"¡{entry['name']} comprado!"
            self.message_timer = 2.0
        elif not self.message:
            self.message       = "¡No tienes suficientes monedas!"
            self.message_timer = 2.0

    def _purchase(self, entry) -> bool:
        if not self.player.spend_coins(entry["cost"]):
            return False

        t = entry["type"]

        if t == "stat":
            self.player.base_stats[entry["stat"]] += entry["value"]
            self.player._recalculate_stats()
            if entry["stat"] == "max_health":
                self.player.base_health += entry["value"]
                self.player.heal(entry["value"])

        elif t == "weapon":
            weapon = self.player.inventory.get_weapon(
                self.player.inventory.active_weapon_slot)
            if weapon is None:
                return self._fail(entry, "¡No tienes arma equipada!")
            setattr(weapon, entry["attr"], getattr(weapon, entry["attr"], 0) + entry["value"])

        elif t == "buy_weapon":
            if entry.get("unique"):
                weapon_name  = entry["name"].split(" (")[0]
                already_inv  = any(getattr(i, "name", None) == weapon_name
                                   for i in self.player.inventory.items
                                   if getattr(i, "type", None) == "weapon_item")
                already_equip = any(w is not None and w.name == weapon_name
                                    for w in [self.player.inventory.get_weapon("primary"),
                                              self.player.inventory.get_weapon("secondary")])
                if already_inv or already_equip:
                    return self._fail(entry, f"¡Ya tienes {entry['name']}!")
            if self.player.inventory.check_full():
                return self._fail(entry, "¡Inventario lleno!")
            weapon = _build_weapon(entry["weapon_class"])
            if weapon is None:
                return self._fail(entry, "Error: clase de arma no encontrada")
            weapon.parent        = self.player
            weapon.audio_emitter = self.player.audio_emitter
            from item.weapon_item import WeaponItem
            self.player.inventory.add_item(WeaponItem(weapon))
            self.message       = f"¡{weapon.name} añadida al inventario!"
            self.message_timer = 2.5
            return True

        elif t == "item":
            if entry.get("unique"):
                if any(getattr(i, "id", None) == entry.get("item_id")
                       for i in self.player.inventory.items):
                    return self._fail(entry, f"¡Ya tienes {entry['name']}!")
            if self.player.inventory.check_full():
                return self._fail(entry, "¡Inventario lleno!")
            self.player.inventory.add_item(
                ItemInstance(ItemRegistry.get(entry["item_id"])))

        elif t == "heal":
            if self.player.health >= self.player.get_stat("max_health"):
                return self._fail(entry, "¡Ya tienes la vida al máximo!")
            self.player.heal(entry["value"])

        return True