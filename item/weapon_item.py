from __future__ import annotations
import pygame

class WeaponItem:
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