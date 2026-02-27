import pygame
from weapons.ranged.ranged import Ranged
from weapons.melee.melee import Melee


class WeaponController:
    
    def __init__(self, player):
        self.player = player
        self._last_attack_time = 0
        self._attack_hold_time = 0
    
    def update(self, input_handler, delta_time):
        if not self.player or not self.player.inventory:
            return
        
        # Obtener arma activa
        active_weapon = self.player.inventory.get_weapon(
            self.player.inventory.active_weapon_slot
        )
        
        if not active_weapon:
            return
        
        # Actualizar estado del arma
        if hasattr(active_weapon, 'update'):
            active_weapon.update()
        
        # Procesar acciones de entrada
        self._handle_attack(input_handler, active_weapon, delta_time)
        self._handle_reload(input_handler, active_weapon)
        self._handle_weapon_swap(input_handler)
    
    def _handle_attack(self, input_handler, weapon, delta_time):
        if not input_handler.actions.get("attack", False):
            self._attack_hold_time = 0
            return
        
        self._attack_hold_time += delta_time
        
        if isinstance(weapon, Ranged):
            self._handle_ranged_attack(weapon)
        elif isinstance(weapon, Melee):
            self._handle_melee_attack(weapon)
    
    def _handle_ranged_attack(self, weapon):
        if weapon.shoot():
            # Éxito - el sonido se reproduce en shoot()
            pass
        else:
            # Fallo - podría ser sin munición
            if weapon.current_clip == 0:
                print(f"Sin munición en {weapon.get_name()}")
                # Aquí se podría reproducir sonido de "clic seco"
    
    def _handle_melee_attack(self, weapon):
        if weapon.attack():
            # Éxito
            pass
        else:
            # Fallo - probablemente en cooldown
            pass
    
    def _handle_reload(self, input_handler, weapon):
        if not input_handler.actions.get("reload", False):
            return
        
        # Solo las armas de fuego pueden recargar
        if isinstance(weapon, Ranged):
            if weapon.reload():
                print(f"Recargando {weapon.get_name()}...")
                # Limpiar acción para evitar recargas múltiples en el mismo frame
                input_handler.actions["reload"] = False
        
        # Limpiar la acción de recarga de una sola vez
        # (se establece como True cuando se presiona R)
        if "reload" in input_handler.keys_just_pressed:
            input_handler.keys_just_pressed.pop("reload", None)
    
    def _handle_weapon_swap(self, input_handler):
        if not input_handler.actions.get("swap_weapon", False):
            return
        
        self.player.inventory.swap_weapons()
        
        new_weapon = self.player.inventory.get_weapon(
            self.player.inventory.active_weapon_slot
        )
        
        if new_weapon:
            print(f"Arma cambiada a: {new_weapon.get_name()}")
        else:
            print("Slot de arma vacío")
        
        # Limpiar acción de cambio
        input_handler.actions["swap_weapon"] = False
    
    def get_active_weapon_info(self) -> dict:
        weapon = self.player.inventory.get_weapon(
            self.player.inventory.active_weapon_slot
        )
        
        if not weapon:
            return None
        
        info = {
            "name": weapon.get_name(),
            "damage": weapon.get_damage(),
            "type": "ranged" if isinstance(weapon, Ranged) else "melee"
        }
        
        if isinstance(weapon, Ranged):
            in_clip, in_reserve = weapon.get_ammo_count()
            info.update({
                "ammo_in_clip": in_clip,
                "ammo_in_reserve": in_reserve,
                "clip_size": weapon.clip_size,
                "is_reloading": weapon.is_reloading(),
                "can_shoot": weapon.can_shoot()
            })
        
        elif isinstance(weapon, Melee):
            info.update({
                "attack_progress": weapon.get_attack_progress(),
                "can_attack": weapon.can_attack(),
                "reach": weapon.reach
            })
        
        return info


class WeaponUIHelper:
    @staticmethod
    def format_ammo_display(weapon: Ranged) -> str:
        in_clip, in_reserve = weapon.get_ammo_count()
        return f"{in_clip}/{weapon.clip_size} ({in_reserve})"
    
    @staticmethod
    def get_reload_progress(weapon: Ranged) -> float:
        if not weapon.is_reloading():
            return 0.0
        
        elapsed = (pygame.time.get_ticks() - weapon._reload_start_time) / 1000.0
        progress = min(1.0, elapsed / weapon.reload_time)
        return progress
    
    @staticmethod
    def get_attack_color(weapon) -> tuple:
        if isinstance(weapon, Ranged):
            if weapon.is_reloading():
                return (255, 165, 0)  # Naranja - recargando
            elif weapon.can_shoot():
                return (0, 255, 0)    # Verde - listo
            else:
                return (255, 0, 0)    # Rojo - esperar
        
        elif isinstance(weapon, Melee):
            if weapon.can_attack():
                return (0, 255, 0)    # Verde - listo
            else:
                return (255, 0, 0)    # Rojo - esperar
        
        return (255, 255, 255)  # Blanco - desconocido
