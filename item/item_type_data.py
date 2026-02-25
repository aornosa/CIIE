from dataclasses import dataclass

import pygame


@dataclass
class AmmoData:
    ammo_type: str
    capacity: int

@dataclass
class ItemDefinition:
    id: str
    asset: pygame.Surface
    name: str
    description: str
    type: str
    effect: str | None = None
    ammo: AmmoData | None = None
