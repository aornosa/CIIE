import pygame
from weapons.ranged.ranged import Ranged
from weapons.melee.melee import Melee
from core.status_effects import StatusEffect

_MELEE_SPEED_EFFECT_NAME = "Melee Agility"
_MELEE_SPEED_BONUS       = 80    


class WeaponController:

    def __init__(self, player, camera=None, ads_effect=None):
        self.player     = player
        self.camera     = camera
        self.ads_effect = ads_effect
        self._last_attack_time  = 0
        self._attack_hold_time  = 0
        self._melee_bonus_active = False

    def update(self, input_handler, delta_time, mouse_pos=None):
        if not self.player or not self.player.inventory:
            return

        active_weapon = self.player.inventory.get_weapon(
            self.player.inventory.active_weapon_slot
        )
        if not active_weapon:
            self._remove_melee_bonus()
            return

        if hasattr(active_weapon, 'update'):
            active_weapon.update()

        # Rotar jugador hacia el ratón
        if mouse_pos is not None and self.camera is not None:
            from game_math import utils as math
            direction = mouse_pos - (self.player.position - self.camera.position)
            if direction.length() > 5:
                target_angle = direction.angle_to(pygame.Vector2(0, -1))
                aiming = input_handler.actions.get("attack") or input_handler.actions.get("aim")
                lerp_speed = 20 * delta_time if aiming else 12 * delta_time
                self.player.set_rotation(
                    math.lerp_angle(self.player.rotation, target_angle, lerp_speed) + 0.164
                )

        # ADS effect
        if self.ads_effect:
            if input_handler.actions.get("attack") or input_handler.actions.get("aim"):
                self.player.add_effect(self.ads_effect)
            else:
                self.player.remove_effect(self.ads_effect.name)

        # Bonus de velocidad con melee
        if isinstance(active_weapon, Melee):
            self._apply_melee_bonus()
        else:
            self._remove_melee_bonus()

        self._handle_attack(input_handler, active_weapon, delta_time)
        self._handle_reload(input_handler, active_weapon)
        self._handle_weapon_swap(input_handler)

    def _apply_melee_bonus(self):
        if not self._melee_bonus_active:
            effect = StatusEffect(
                icon=None,
                name=_MELEE_SPEED_EFFECT_NAME,
                modifiers={"speed": _MELEE_SPEED_BONUS},
                duration=-1,
                is_buff=True,
            )
            self.player.add_effect(effect)
            self._melee_bonus_active = True

    def _remove_melee_bonus(self):
        if self._melee_bonus_active:
            self.player.remove_effect(_MELEE_SPEED_EFFECT_NAME)
            self._melee_bonus_active = False

    def setup_emitter(self, screen):
        """Configura el emitter de partículas del arma ranged activa."""
        weapon = self.player.inventory.get_weapon(self.player.inventory.active_weapon_slot)
        if isinstance(weapon, Ranged) and hasattr(weapon, 'emitter'):
            weapon.emitter.surface = screen
            weapon.emitter.camera  = self.camera

    def draw_trail(self, screen, player_screen_pos, active_weapon):
        if isinstance(active_weapon, Ranged) and hasattr(active_weapon, 'emitter'):
            active_weapon.emitter.surface = screen
            active_weapon.emitter.camera  = self.camera

    def _handle_attack(self, input_handler, weapon, delta_time):
        if not input_handler.actions.get("attack", False):
            self._attack_hold_time = 0
            return
        self._attack_hold_time += delta_time
        if isinstance(weapon, Ranged):
            weapon.shoot()
        elif isinstance(weapon, Melee):
            weapon.attack()

    def _handle_reload(self, input_handler, weapon):
        if not input_handler.actions.get("reload", False):
            return
        if isinstance(weapon, Ranged):
            weapon.reload()
            input_handler.actions["reload"] = False

    def _handle_weapon_swap(self, input_handler):
        if not input_handler.actions.get("swap_weapon", False):
            return
        self.player.inventory.swap_weapons()
        input_handler.actions["swap_weapon"] = False

    def get_active_weapon_info(self) -> dict:
        weapon = self.player.inventory.get_weapon(self.player.inventory.active_weapon_slot)
        if not weapon:
            return None
        info = {"name": weapon.name, "damage": weapon.damage,
                "type": "ranged" if isinstance(weapon, Ranged) else "melee"}
        if isinstance(weapon, Ranged):
            info.update({"ammo_in_clip": weapon.current_clip, "clip_size": weapon.clip_size,
                         "is_reloading": weapon.is_reloading(), "can_shoot": weapon.can_shoot()})
        elif isinstance(weapon, Melee):
            info.update({"attack_progress": weapon.get_attack_progress(),
                         "can_attack": weapon.can_attack(), "reach": weapon.reach})
        return info