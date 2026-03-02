from item.item_type_data import ItemDefinition

class ItemInstance:
    def __init__(self, definition: ItemDefinition):
        self.definition = definition

        # Runtime state (unique per instance)
        if definition.ammo:
            self.current_ammo = definition.ammo.capacity
        else:
            self.current_ammo = None

    # --- Forwarded properties ---
    def __getattr__(self, attr):
        return getattr(self.definition, attr)