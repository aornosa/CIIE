import ui.inventory_menu as menu
from item.consumable import use_consumable

WEAPON_SLOTS = {
    "primary": 0,
    "secondary": 1,
}


class Inventory:
    def __init__(self):
        self.active_weapon_slot = "primary"
        self.primary_weapon = None
        self.secondary_weapon = None
        self.max_size = 12
        self.items = []
        self.selected_item_index = -1

    def add_weapon(self, player, weapon, slot):
        weapon.parent = player
        weapon.audio_emitter = player.audio_emitter
        if slot == "primary":
            if self.primary_weapon is None:
                self.primary_weapon = weapon
        elif slot == "secondary":
            if self.secondary_weapon is None:
                self.secondary_weapon = weapon
            else:
                self.drop_weapon(slot)

    def get_weapon(self, slot):
        if slot == "primary":
            return self.primary_weapon
        elif slot == "secondary":
            return self.secondary_weapon
        return None

    def drop_weapon(self, slot):
        if slot == "primary":
            self.primary_weapon = None
        elif slot == "secondary":
            self.secondary_weapon = None

    def swap_weapons(self):
        self.active_weapon_slot = "secondary" if self.active_weapon_slot == "primary" else "primary"

    def add_item(self, item):
        if not self.check_full():
            self.items.append(item)
            return True
        return False

    def drop_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            if self.selected_item_index >= len(self.items):
                self.selected_item_index = len(self.items) - 1

    def check_full(self):
        return len(self.items) >= self.max_size

    def select_item(self, index: int):
        if 0 <= index < len(self.items):
            self.selected_item_index = index
        else:
            self.selected_item_index = -1

    def get_selected_item(self):
        if 0 <= self.selected_item_index < len(self.items):
            return self.items[self.selected_item_index]
        return None

    def use_selected_item(self, player) -> bool:
        if self.selected_item_index < 0 or self.selected_item_index >= len(self.items):
            return False
        item = self.items[self.selected_item_index]
        if item.type != "consumable":
            return False
        success = use_consumable(item, player)
        if success:
            self.remove_item(item)
        return success

    def use_consumable_hotkey(self, slot_index: int, player) -> bool:
        if slot_index < 0 or slot_index >= len(self.items):
            return False
        item = self.items[slot_index]
        if item.type != "consumable":
            return False
        success = use_consumable(item, player)
        if success:
            self.items.pop(slot_index)
            if self.selected_item_index >= len(self.items):
                self.selected_item_index = len(self.items) - 1
        return success


def show_inventory(screen, player):
    menu.draw_weapon_box(screen, player.inventory.primary_weapon, (100, 100))
    menu.draw_weapon_box(screen, player.inventory.secondary_weapon, (700, 100))
    menu.draw_player_status(screen, player, (1300, 100))

    for i in range(player.inventory.max_size):
        x = 100 + (i % 6) * 110
        y = 550 + (i // 6) * 110
        if i < len(player.inventory.items):
            item = player.inventory.items[i]
            is_selected = (i == player.inventory.selected_item_index)
            menu.draw_item_box(screen, item, (x, y), selected=is_selected)
        else:
            menu.draw_item_box(screen, None, (x, y))