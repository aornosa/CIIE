import ui.inventory_menu as menu
from item.consumable import use_consumable
from item.item_drop_manager import DropManager


class Inventory:
    def __init__(self):
        self.active_weapon_slot  = "primary"
        self.primary_weapon      = None
        self.secondary_weapon    = None
        self.max_size            = 19
        self.items: list         = []
        self.selected_item_index = -1
        self.owner               = None
        self.drop_manager        = DropManager()

    def add_weapon(self, player, weapon, slot: str):
        weapon.parent        = player
        weapon.audio_emitter = player.audio_emitter
        if slot == "primary":
            if self.primary_weapon is None:
                self.primary_weapon = weapon
        elif slot == "secondary":
            if self.secondary_weapon is not None:
                self.drop_weapon("secondary")
            self.secondary_weapon = weapon

    def get_weapon(self, slot: str):
        if slot == "primary":   return self.primary_weapon
        if slot == "secondary": return self.secondary_weapon
        return None

    def drop_weapon(self, slot: str):
        weapon = self.get_weapon(slot)
        if weapon is None:
            return
        self.drop_manager.drop_item(weapon, weapon.parent.position)
        if slot == "primary":
            self.primary_weapon = None
        else:
            self.secondary_weapon = None

    def swap_weapons(self):
        self.active_weapon_slot = "secondary" if self.active_weapon_slot == "primary" else "primary"

    def add_item(self, item) -> bool:
        if not self.check_full():
            self.items.append(item)
            return True
        return False

    def drop_item(self, item):
        self.drop_manager.drop_item(item, self.owner.position)
        if item in self.items:
            self.items.remove(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            if self.selected_item_index >= len(self.items):
                self.selected_item_index = len(self.items) - 1

    def check_full(self) -> bool:
        return len(self.items) >= self.max_size

    def select_item(self, index: int):
        self.selected_item_index = index if 0 <= index < len(self.items) else -1

    def get_selected_item(self):
        if 0 <= self.selected_item_index < len(self.items):
            return self.items[self.selected_item_index]
        return None

    def _try_use_consumable(self, item, player) -> bool:
        if item.type != "consumable":
            return False
        return use_consumable(item, player)

    def use_selected_item(self, player) -> bool:
        item = self.get_selected_item()
        if item is None:
            return False
        success = self._try_use_consumable(item, player)
        if success:
            self.remove_item(item)
        return success

    def use_consumable_hotkey(self, slot_index: int, player) -> bool:
        if slot_index < 0 or slot_index >= len(self.items):
            return False
        item    = self.items[slot_index]
        success = self._try_use_consumable(item, player)
        if success:
            self.items.pop(slot_index)
            if self.selected_item_index >= len(self.items):
                self.selected_item_index = len(self.items) - 1
        return success

    def click_drop_item(self, mouse_pos) -> bool:
        for i, item in enumerate(self.items):
            if menu.get_item_slot_rect(i).collidepoint(mouse_pos):
                self.drop_item(item)
                return True
        return False

    def equip_weapon_from_item(self, player, weapon_item, item_index: int, slot: str):
        # Equipa un WeaponItem del inventario en el slot indicado, devolviendo el arma anterior al inventario
        weapon               = weapon_item.weapon
        weapon.parent        = player
        weapon.audio_emitter = player.audio_emitter

        old = self.get_weapon(slot)
        if old is not None:
            from item.weapon_item import WeaponItem as WI
            if not self.add_item(WI(old)):
                self.drop_weapon(slot)
            else:
                if slot == "primary":
                    self.primary_weapon = None
                else:
                    self.secondary_weapon = None

        if slot == "primary":
            self.primary_weapon = weapon
        else:
            self.secondary_weapon = weapon

        if 0 <= item_index < len(self.items):
            self.items.pop(item_index)

    def update(self, delta_time: float):
        pass