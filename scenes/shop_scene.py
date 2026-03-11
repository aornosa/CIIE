import pygame

from core.scene import Scene
from ui.shop_menu import draw_shop_menu
from item.item_instance import ItemInstance
from item.item_loader import ItemRegistry


# ── Shop catalog ──────────────────────────────────────────────
# Each entry defines: name, desc, cost, type, and type-specific data.
#   type="stat"   → modifies player.base_stats[stat] by +value
#   type="weapon" → modifies active weapon's attr by +value
#   type="item"   → adds an ItemInstance to inventory by item_id

SHOP_CATALOG = [
    {
        "name": "Vida Reforzada",
        "desc": "+25 Vida máxima",
        "cost": 200,
        "type": "stat",
        "stat": "max_health",
        "value": 25,
    },
    {
        "name": "Botas de Acero",
        "desc": "+30 Velocidad",
        "cost": 100,
        "type": "stat",
        "stat": "speed",
        "value": 30,
    },
    {
        "name": "Cargador Ampliado",
        "desc": "+5 balas al cargador (arma activa)",
        "cost": 150,
        "type": "weapon",
        "attr": "clip_size",
        "value": 5,
    },
    {
        "name": "Botiquín de Campo",
        "desc": "Cura 50 HP al instante",
        "cost": 75,
        "type": "heal",
        "value": 50,
    },
    {
        "name": "Gatillo Mejorado",
        "desc": "-0.03s entre disparos (arma activa)",
        "cost": 175,
        "type": "weapon",
        "attr": "fire_rate",
        "value": -0.03,
    },
    {
        "name": "Munición Perforante",
        "desc": "+15 daño por bala (arma activa)",
        "cost": 200,
        "type": "weapon",
        "attr": "damage",
        "value": 15,
    },
]


class ShopScene(Scene):
    """Shop menu – stacked on top of GameScene via director.push()."""

    def __init__(self, game_scene, player):
        super().__init__()
        self.game_scene = game_scene
        self.player = player
        self.catalog = SHOP_CATALOG
        self.selected = 0
        self.total_options = len(self.catalog) + 1  # catalog items + "Cerrar"
        self.message = ""
        self.message_timer = 0.0

    # ── Scene lifecycle ───────────────────────────────────────

    def on_enter(self):
        pygame.mouse.set_visible(True)
        from core.audio.music_manager import MusicManager
        MusicManager.instance().set_category("idle")

    def on_exit(self):
        pygame.mouse.set_visible(False)

    # ── Input ─────────────────────────────────────────────────

    def handle_events(self, input_handler):
        # Close shop with P or ESC
        if input_handler.actions.get("shop"):
            input_handler.actions["shop"] = False
            self.director.pop()
            return

        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            self.director.pop()
            return

        # Navigate up/down
        if input_handler.keys_just_pressed.get(pygame.K_UP) or \
           input_handler.keys_just_pressed.get(pygame.K_w):
            self.selected = (self.selected - 1) % self.total_options

        if input_handler.keys_just_pressed.get(pygame.K_DOWN) or \
           input_handler.keys_just_pressed.get(pygame.K_s):
            self.selected = (self.selected + 1) % self.total_options

        # Confirm purchase / close
        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select_option()

    # ── Update ────────────────────────────────────────────────

    def update(self, delta_time):
        # Tick down the feedback message
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.message = ""

    # ── Render ────────────────────────────────────────────────

    def render(self, screen):
        # Frozen game frame as background
        last_frame = self.game_scene.get_last_frame()
        if last_frame is not None:
            screen.blit(last_frame, (0, 0))

        draw_shop_menu(screen, self.catalog, self.selected,
                       self.player.coins, self.message, self.player)

    # ── Selection logic ───────────────────────────────────────

    def _select_option(self):
        # Last option is always "Cerrar"
        if self.selected >= len(self.catalog):
            self.director.pop()
            return

        entry = self.catalog[self.selected]
        self.message = ""  # clear before purchase so _purchase can set its own
        success = self._purchase(entry)

        if success:
            self.message = f"¡{entry['name']} comprado!"
            self.message_timer = 2.0
        elif not self.message:  # _purchase may have already set a specific message
            self.message = "¡No tienes suficientes monedas!"
            self.message_timer = 2.0

    # ── Purchase logic ────────────────────────────────────────

    def _purchase(self, entry):
        cost = entry["cost"]

        if not self.player.spend_coins(cost):
            return False

        if entry["type"] == "stat":
            self.player.base_stats[entry["stat"]] += entry["value"]
            self.player._recalculate_stats()

            # If max_health increased, also raise the healing cap and heal
            if entry["stat"] == "max_health":
                self.player.base_health += entry["value"]
                self.player.heal(entry["value"])

        elif entry["type"] == "weapon":
            weapon = self.player.inventory.get_weapon(
                self.player.inventory.active_weapon_slot
            )
            if weapon is not None:
                current = getattr(weapon, entry["attr"], 0)
                setattr(weapon, entry["attr"], current + entry["value"])
            else:
                # No weapon equipped — refund
                self.player.coins += cost
                self.message = "¡No tienes arma equipada!"
                self.message_timer = 2.0
                return False

        elif entry["type"] == "item":
            if self.player.inventory.check_full():
                # Inventory full — refund
                self.player.coins += cost
                self.message = "¡Inventario lleno!"
                self.message_timer = 2.0
                return False

            self.player.inventory.add_item(
                ItemInstance(ItemRegistry.get(entry["item_id"]))
            )

        elif entry["type"] == "heal":
            if self.player.health >= self.player.get_stat("max_health"):
                # Already full HP — refund
                self.player.coins += cost
                self.message = "¡Ya tienes la vida al máximo!"
                self.message_timer = 2.0
                return False
            self.player.heal(entry["value"])

        return True
