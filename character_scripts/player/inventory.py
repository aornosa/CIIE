import ui.inventory_menu as menu
class Inventory:
    def __init__(self):
        self.primary_weapon = None
        self.secondary_weapon = None
        self.max_size = 12
        self.items = []

    def add_weapon(self, weapon, slot):
        if slot == "primary":
            if self.primary_weapon is None:
                self.primary_weapon = weapon
        elif slot == "secondary":
            if self.secondary_weapon is None:
                self.secondary_weapon = weapon
            else:
                self.drop_weapon(slot)

    def drop_weapon(self, slot):
        if slot == "primary":
            # instance weapon to ground (implement)

            # Null slot
            self.primary_weapon = None
        elif slot == "secondary":
            # instance weapon to ground

            # Null slot
            self.secondary_weapon = None

    def add_item(self, item):
        self.items.append(item)

    def drop_item(self, item):
        # instance item to ground (implement)

        # Remove from inventory
        if item in self.items:
            self.items.remove(item)

    def check_full(self):
        return len(self.items) >= self.max_size

def open_inventory(screen, player):
    menu.draw_weapon_box(screen, player.inventory.primary_weapon, (100, 100))
    menu.draw_weapon_box(screen, player.inventory.secondary_weapon, (300, 100))
    for index, item in enumerate(player.inventory.items):
        x = 100 + (index % 4) * 70
        y = 300 + (index // 4) * 70
        menu.draw_item_box(screen, item, (x, y))
