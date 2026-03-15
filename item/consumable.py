from __future__ import annotations
from typing import TYPE_CHECKING
from core.status_effects import StatusEffect
if TYPE_CHECKING:
    from character_scripts.character import Character

# Contador de usos del inyector por jugador
_addiction_counters: dict[int, int] = {}

def _get_addiction(player: "Character") -> int:
    return _addiction_counters.get(id(player), 0)

def _increment_addiction(player: "Character") -> int:
    count = _addiction_counters.get(id(player), 0) + 1
    _addiction_counters[id(player)] = count
    return count

def reset_addiction(player: "Character"):
    _addiction_counters[id(player)] = 0


def _make_speed_buff(duration: float, amount: int) -> "StatusEffect":
    return StatusEffect(icon=None, name="Fénix Rush",
                        modifiers={"speed": amount}, duration=duration, is_buff=True)

def _make_addiction_debuff(stack: int) -> "StatusEffect":
    # Penaliza max_health de forma acumulativa con cada uso del inyector
    return StatusEffect(icon=None, name="Adicción Fénix",
                        modifiers={"max_health": -5 * stack}, duration=-1, is_buff=False)

def _make_speed_burst(duration: float, amount: int) -> "StatusEffect":
    return StatusEffect(icon=None, name="Adrenalina",
                        modifiers={"speed": amount}, duration=duration, is_buff=True)

def use_consumable(item_def, player: "Character") -> bool:
    handler = _EFFECT_HANDLERS.get(item_def.effect)
    if handler is None:
        return False
    return handler(player, item_def)

def _effect_regen_health(player: "Character", item_def) -> bool:
    if player.health >= player.get_stat("max_health"):
        return False
    player.heal(30)
    return True

def _effect_phoenix_injector(player: "Character", item_def) -> bool:
    player.heal(60)
    player.add_effect(_make_speed_buff(duration=8.0, amount=80))
    stack = _increment_addiction(player)
    player.add_effect(_make_addiction_debuff(stack))
    return True

def _effect_adrenaline_shot(player: "Character", item_def) -> bool:
    player.add_effect(_make_speed_burst(duration=5.0, amount=150))
    return True

def _effect_rad_suppressor(player: "Character", item_def) -> bool:
    if _get_addiction(player) == 0:
        return False
    player.remove_effect("Adicción Fénix")
    reset_addiction(player)
    return True

def _effect_dash(player: "Character", item_def) -> bool:
    import pygame
    direction = getattr(player, "_dash_direction", None)
    if direction is None or direction.length() < 0.01:
        direction = pygame.Vector2(0, -1).rotate(-player.rotation)
    else:
        direction = direction.normalize()
    player.position += direction * 150.0
    return True

_EFFECT_HANDLERS = {
    "regen_health":     _effect_regen_health,
    "phoenix_injector": _effect_phoenix_injector,
    "adrenaline_shot":  _effect_adrenaline_shot,
    "rad_suppressor":   _effect_rad_suppressor,
    "dash":             _effect_dash,
}