"""
weapons/weapon_controller.py
-----------------------------
Gestiona toda la lógica de entrada relacionada con armas:
  - Apuntado continuo hacia el ratón (siempre activo)
  - Disparo  (ranged: shoot / melee: attack)
  - Recarga
  - Cambio de arma
  - Efecto ADS (velocidad reducida al apuntar/disparar)

Uso desde la escena:
    # En __init__ / _build_level:
    self.weapon_controller = WeaponController(self.player, self.camera, ads_effect)

    # En render (necesita delta_time y el input_handler):
    self.weapon_controller.update(input_handler, delta_time, player_screen_pos, mouse_pos)

    # Para el trail visual del ranged (llamar después de update si se necesita):
    self.weapon_controller.draw_trail(screen, player_screen_pos)
"""

from __future__ import annotations

import pygame
from game_math.utils import lerp_angle
from weapons.ranged.ranged import Ranged
from weapons.melee.melee import Melee


class WeaponController:
    """
    Controlador de armas desacoplado de la escena.

    Parámetros
    ----------
    player      — referencia al jugador
    camera      — referencia a la cámara (para calcular posición en pantalla)
    ads_effect  — StatusEffect a aplicar mientras se apunta/dispara (puede ser None)
    """

    def __init__(self, player, camera, ads_effect=None):
        self.player     = player
        self.camera     = camera
        self.ads_effect = ads_effect

        # Dirección actual hacia el ratón (normalizada), para uso externo
        self.aim_direction: pygame.Vector2 = pygame.Vector2(0, -1)

    # ── API pública ────────────────────────────────────────────────────────────

    def update(
        self,
        input_handler,
        delta_time: float,
        mouse_pos: pygame.Vector2,
    ) -> None:
        """
        Llama una vez por frame desde la escena.

        Parámetros
        ----------
        input_handler  — InputHandler con las acciones del frame
        delta_time     — segundos desde el frame anterior
        mouse_pos      — posición del ratón en coordenadas de pantalla
        """
        player = self.player
        weapon = self._active_weapon()

        # ── 1. Apuntado continuo al ratón ──────────────────────────────────
        player_screen = player.position - self.camera.position
        to_mouse = mouse_pos - player_screen

        if to_mouse.length() > 1:
            self.aim_direction = to_mouse.normalize()
            target_angle = to_mouse.angle_to(pygame.Vector2(0, -1))
            # Lerp más rápido cuando se está apuntando/disparando, suave en movimiento
            lerp_speed = 14.0 if (input_handler.actions["attack"] or input_handler.actions["aim"]) else 8.0
            player.rotation = lerp_angle(player.rotation, target_angle, lerp_speed * delta_time)

        # ── 2. ADS ─────────────────────────────────────────────────────────
        if self.ads_effect is not None:
            if input_handler.actions["attack"] or input_handler.actions["aim"]:
                player.add_effect(self.ads_effect)
            else:
                player.remove_effect(self.ads_effect.name)

        if not weapon:
            return

        # ── 3. Cambio de arma ──────────────────────────────────────────────
        if input_handler.actions["swap_weapon"]:
            input_handler.actions["swap_weapon"] = False
            player.inventory.swap_weapons()
            weapon = self._active_weapon()

        # ── 4. Recarga ─────────────────────────────────────────────────────
        if input_handler.actions["reload"]:
            input_handler.actions["reload"] = False
            if isinstance(weapon, Ranged):
                weapon.reload()

        # ── 5. Disparo / ataque ────────────────────────────────────────────
        if input_handler.actions["attack"]:
            if isinstance(weapon, Ranged):
                self._fire_ranged(weapon, player_screen)
            elif isinstance(weapon, Melee):
                weapon.attack()

    def draw_trail(
        self,
        screen: pygame.Surface,
        player_screen: pygame.Vector2,
        weapon: Ranged | None = None,
    ) -> None:
        """
        Dibuja el efecto de partículas de disparo del arma ranged activa.
        Llamar después de update(), antes del flip.
        """
        if weapon is None:
            weapon = self._active_weapon()
        if not isinstance(weapon, Ranged):
            return

        direction = pygame.Vector2(0, -1).rotate(-self.player.rotation)
        muzzle_pos = (
            player_screen
            + direction * weapon.muzzle_offset[0]
            + direction.rotate(90) * weapon.muzzle_offset[1]
        )
        weapon.play_trail_effect(screen, muzzle_pos, direction)

    def setup_emitter(self, screen: pygame.Surface) -> None:
        """Asigna screen y camera al emitter del arma ranged activa."""
        weapon = self._active_weapon()
        if isinstance(weapon, Ranged):
            weapon.emitter.surface = screen
            weapon.emitter.camera  = self.camera

    # ── Internos ───────────────────────────────────────────────────────────────

    def _active_weapon(self):
        inv = self.player.inventory
        return inv.get_weapon(inv.active_weapon_slot)

    def _fire_ranged(self, weapon: Ranged, player_screen: pygame.Vector2) -> None:
        direction = pygame.Vector2(0, -1).rotate(-self.player.rotation)
        muzzle_pos = (
            player_screen
            + direction * weapon.muzzle_offset[0]
            + direction.rotate(90) * weapon.muzzle_offset[1]
        )
        weapon.play_trail_effect(None, muzzle_pos, direction)
        weapon.shoot()


class WeaponUIHelper:
    """Utilidades estáticas para la UI de armas."""

    @staticmethod
    def format_ammo_display(weapon: Ranged) -> str:
        in_clip, in_reserve = weapon.get_ammo_count()
        return f"{in_clip}/{weapon.clip_size} ({in_reserve})"

    @staticmethod
    def get_reload_progress(weapon: Ranged) -> float:
        if not weapon.is_reloading():
            return 0.0
        elapsed = (pygame.time.get_ticks() - weapon._reload_start_time) / 1000.0
        return min(1.0, elapsed / weapon.reload_time)

    @staticmethod
    def get_attack_color(weapon) -> tuple:
        if isinstance(weapon, Ranged):
            if weapon.is_reloading():
                return (255, 165, 0)
            return (0, 255, 0) if weapon.can_shoot() else (255, 0, 0)
        if isinstance(weapon, Melee):
            return (0, 255, 0) if weapon.can_attack() else (255, 0, 0)
        return (255, 255, 255)