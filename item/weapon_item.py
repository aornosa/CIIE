"""
item/weapon_item.py
--------------------
Envuelve un objeto Weapon para que pueda guardarse en el inventario
como si fuera un item normal (type="weapon_item").

Flujo:
  1. Jugador compra arma en la tienda → se crea WeaponItem y va al inventario
  2. Jugador abre inventario y hace clic izquierdo sobre el WeaponItem
  3. Aparece overlay de selección de slot (primario / secundario)
  4. Al elegir slot, el arma se equipa y el WeaponItem desaparece del inventario
"""
from __future__ import annotations
import pygame


class WeaponItem:
    """Duck-type compatible con ItemInstance para mostrarse en el inventario."""

    type = "weapon_item"

    def __init__(self, weapon):
        self.weapon      = weapon
        self.name        = weapon.name
        self.description = "Arma — clic para asignar a un slot"
        self.effect      = None
        self.ammo        = None
        self.cooldown    = 0.0
        self.reusable    = True

        try:
            self.asset = pygame.transform.scale(weapon.asset, (50, 50))
        except Exception:
            surf = pygame.Surface((50, 50))
            surf.fill((100, 100, 200))
            self.asset = surf

    @property
    def id(self):
        return f"weapon_item_{self.weapon.name}"