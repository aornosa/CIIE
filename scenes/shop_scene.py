import pygame
from core.scene import Scene
from ui.shop_menu import draw_shop_menu
from item.item_instance import ItemInstance
from item.item_loader import ItemRegistry

SHOP_CATALOG = [
    # Mejoras de personaje
    {"name": "Vida Reforzada",    "desc": "+25 Vida máxima",               "cost": 300, "type": "stat",       "stat": "max_health", "value": 25},
    {"name": "Botas de Acero",    "desc": "+30 Velocidad",                  "cost": 600, "type": "stat",       "stat": "speed",      "value": 30},
    # Mejoras ranged (todas las armas de fuego equipadas)
    {"name": "Cargador Ampliado", "desc": "+10 balas (todas las ranged)",   "cost": 600, "type": "weapon_all_ranged", "attr": "clip_size",  "value": 10},
    {"name": "Gatillo Mejorado",  "desc": "-0.03s disparo (todas ranged)",  "cost": 600, "type": "weapon_all_ranged", "attr": "fire_rate",  "value": -0.03},
    {"name": "Munición Perforante","desc": "+30 daño (todas las ranged)",   "cost": 600, "type": "weapon_all_ranged", "attr": "damage",      "value": 30},
    {"name": "Recarga Rápida",    "desc": "-0.2s recarga (todas ranged)",   "cost": 300, "type": "weapon_all_ranged", "attr": "reload_time", "value": -0.2},
    # Mejoras melee (todas las armas cuerpo a cuerpo equipadas)
    {"name": "Filo Afilado",      "desc": "+25 daño (todas las melee)",     "cost": 600, "type": "weapon_all_melee",  "attr": "damage",       "value": 25},
    {"name": "Ataque Rápido",     "desc": "-0.05s ataque (todas melee)",    "cost": 600, "type": "weapon_all_melee",  "attr": "fire_rate",    "value": -0.05},
    # Armas
    {"name": "Bastón",            "desc": "Porra antidisturbios · melee",   "cost": 350, "type": "buy_weapon", "weapon_class": "Baton",  "unique": True},
    {"name": "MP5",               "desc": "Subfusil 9mm · 60 balas",        "cost": 350, "type": "buy_weapon", "weapon_class": "MP5",    "unique": True},
    {"name": "SPAS-12",           "desc": "Escopeta 12ga · 15 balas",       "cost": 350, "type": "buy_weapon", "weapon_class": "SPAS12", "unique": True},
    # Habilidad
    {"name": "Habilidad: Dash",   "desc": "Impulso rápido · Shift · CD: 3s",  "cost": 400, "type": "dash",        "unique": True},
]

def _build_weapon(weapon_class: str):
    if weapon_class == "MP5":
        from weapons.ranged.ranged_types import MP5;         return MP5()
    if weapon_class == "SPAS12":
        from weapons.ranged.ranged_types import SPAS12;      return SPAS12()
    if weapon_class == "AK47":
        from weapons.ranged.ranged_types import AK47;        return AK47()
    if weapon_class == "TacticalKnife":
        from weapons.melee.melee_types import TacticalKnife; return TacticalKnife()
    if weapon_class == "Baton":
        from weapons.melee.melee_types import Baton;         return Baton()
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
        catalog_len = len(self.catalog)
        close_index = catalog_len

        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            if self.selected == close_index:
                self.selected = max(0, catalog_len - 1)
            elif self.selected >= 2:
                self.selected -= 2
            else:
                self.selected = close_index

        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
            if self.selected == close_index:
                self.selected = 0
            else:
                next_idx = self.selected + 2
                self.selected = next_idx if next_idx < catalog_len else close_index

        if input_handler.keys_just_pressed.get(pygame.K_LEFT) or \
           input_handler.keys_just_pressed.get(pygame.K_a):
            if self.selected == close_index:
                self.selected = max(0, catalog_len - 1)
            elif self.selected % 2 == 1:
                self.selected -= 1

        if input_handler.keys_just_pressed.get(pygame.K_RIGHT) or \
           input_handler.keys_just_pressed.get(pygame.K_d):
            if self.selected == close_index:
                self.selected = 0
            elif self.selected % 2 == 0 and self.selected + 1 < catalog_len:
                self.selected += 1
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
                       self.player.coins, self.message, self.player,
                       owned_items=self._get_owned_weapon_names())

    def _get_owned_weapon_names(self) -> set:
        owned = set()
        for slot in ("primary", "secondary"):
            w = self.player.inventory.get_weapon(slot)
            if w is not None:
                owned.add(w.name.split(" (")[0])
        for item in self.player.inventory.items:
            if getattr(item, "type", None) == "weapon_item":
                owned.add(getattr(item, "name", "").split(" (")[0])
        if self.player.has_dash:
            owned.add("Habilidad: Dash")
        return owned

    def _fail(self, entry, msg: str) -> bool:
        self.player.coins += entry["cost"]
        self.message       = msg
        self.message_timer = 2.0
        return False

    def _select_option(self):
        if self.selected >= len(self.catalog):
            self.director.pop()
            return
        entry        = self.catalog[self.selected]
        self.message = ""
        success      = self._purchase(entry)
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
                self.player.health = min(self.player.health + entry["value"],
                                         self.player.get_stat("max_health"))

        elif t == "weapon_all_ranged":
            # Acumula la mejora en el jugador — todas las ranged la reciben automáticamente
            from weapons.ranged.ranged import Ranged
            weapons = [self.player.inventory.get_weapon(s) for s in ("primary", "secondary")]
            if not any(isinstance(w, Ranged) for w in weapons):
                return self._fail(entry, "¡Necesitas un arma de fuego equipada!")
            key_map = {"clip_size": "ranged_clip", "fire_rate": "ranged_fire_rate", "damage": "ranged_damage", "reload_time": "ranged_reload_time"}
            self.player.weapon_upgrades[key_map[entry["attr"]]] += entry["value"]

        elif t == "weapon_all_melee":
            # Acumula la mejora en el jugador — todas las melee la reciben automáticamente
            from weapons.melee.melee import Melee
            weapons = [self.player.inventory.get_weapon(s) for s in ("primary", "secondary")]
            if not any(isinstance(w, Melee) for w in weapons):
                return self._fail(entry, "¡Necesitas un arma melee equipada!")
            key_map = {"damage": "melee_damage", "fire_rate": "melee_fire_rate"}
            self.player.weapon_upgrades[key_map[entry["attr"]]] += entry["value"]

        elif t == "buy_weapon":
            if entry.get("unique"):
                weapon_name   = entry["name"].split(" (")[0]
                already_inv   = any(getattr(i, "name", None) == weapon_name
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

        elif t == "dash":
            if self.player.has_dash:
                return self._fail(entry, "¡Ya tienes el Dash!")
            self.player.has_dash = True

        elif t == "item":
            if entry.get("unique"):
                if any(getattr(i, "id", None) == entry.get("item_id")
                       for i in self.player.inventory.items):
                    return self._fail(entry, f"¡Ya tienes {entry['name']}!")
            if self.player.inventory.check_full():
                return self._fail(entry, "¡Inventario lleno!")
            self.player.inventory.add_item(
                ItemInstance(ItemRegistry.get(entry["item_id"])))

        return True