from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from map.interactables.interactable import Interactable
    from character_scripts.player.player import Player


class InteractionManager:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._interactables = []
        return cls._instance

    def register(self, interactable: "Interactable"):
        if interactable not in self._interactables:
            self._interactables.append(interactable)

    def unregister(self, interactable: "Interactable"):
        if interactable in self._interactables:
            self._interactables.remove(interactable)

    def get_closest_in_range(self, player: "Player"):
        closest = None
        closest_dist = float("inf")

        for obj in self._interactables:
            if obj.is_player_in_range(player.position):
                dist = obj.position.distance_to(player.position)
                if dist < closest_dist:
                    closest_dist = dist
                    closest = obj

        return closest

    def check_interaction(self, player: "Player", input_handler):
        if not input_handler.actions.get("interact", False):
            return

        target = self.get_closest_in_range(player)
        if target:
            input_handler.actions["interact"] = False
            target.interact(player)

    def get_tooltip_in_range(self, player: "Player") -> str | None:
        target = self.get_closest_in_range(player)
        return target.get_tooltip() if target else None

    def clear(self):
        self._interactables.clear()