from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character_scripts.character import Character

from core.status_effects import StatusEffect

_addiction_counters: dict[int, int] = {} 

def _get_addiction(player: "Character") -> int:
    return _addiction_counters.get(id(player), 0)

def _increment_addiction(player: "Character") -> int:
    count = _addiction_counters.get(id(player), 0) + 1
    _addiction_counters[id(player)] = count
    return count

def reset_addiction(player: "Character"):
    _addiction_counters[id(player)] = 0

def _make_speed_buff(duration: float, amount: int) -> StatusEffect:
    return StatusEffect(
        icon=None,
        name="Fénix Rush",
        modifiers={"speed": amount},
        duration=duration,
        is_buff=True,
    )

def _make_addiction_debuff(stack: int) -> StatusEffect:
    return StatusEffect(
        icon=None,
        name="Adicción Fénix",
        modifiers={"max_health": -5 * stack},
        duration=-1,          
        is_buff=False,
    )


def _make_speed_burst(duration: float, amount: int) -> StatusEffect:
    return StatusEffect(
        icon=None,
        name="Adrenalina",
        modifiers={"speed": amount},
        duration=duration,
        is_buff=True,
    )

def use_consumable(item_def, player: "Character") -> bool:
    effect_id = item_def.effect
    if effect_id is None:
        print(f"[Consumable] '{item_def.name}' no tiene efecto definido.")
        return False

    handler = _EFFECT_HANDLERS.get(effect_id)
    if handler is None:
        print(f"[Consumable] Efecto desconocido: '{effect_id}'")
        return False

    return handler(player, item_def)

def _effect_regen_health(player: "Character", item_def) -> bool:
    heal_amount = 30
    if player.health >= player.get_stat("max_health"):
        print(f"[Consumable] Vida ya al máximo.")
        return False
    player.heal(heal_amount)
    print(f"[Consumable] {item_def.name}: +{heal_amount} HP → {player.health}")
    return True


def _effect_phoenix_injector(player: "Character", item_def) -> bool:
    heal_amount = 60
    player.heal(heal_amount)

    speed_buff = _make_speed_buff(duration=8.0, amount=80)
    player.add_effect(speed_buff)

    stack = _increment_addiction(player)
    debuff = _make_addiction_debuff(stack)
    player.add_effect(debuff)           

    print(
        f"[Consumable] Autoinyector Fénix: +{heal_amount} HP, +80 spd 8s | "
        f"Adicción stack {stack} → max_health -{5 * stack}"
    )
    return True


def _effect_adrenaline_shot(player: "Character", item_def) -> bool:
    burst = _make_speed_burst(duration=5.0, amount=150)
    player.add_effect(burst)
    print(f"[Consumable] Adrenalina: +150 spd 5s")
    return True


def _effect_rad_suppressor(player: "Character", item_def) -> bool:
    if _get_addiction(player) == 0:
        print(f"[Consumable] Sin adicción que suprimir.")
        return False
    player.remove_effect("Adicción Fénix")
    reset_addiction(player)
    print(f"[Consumable] Supresor RAD: adicción eliminada, max_health restaurado.")
    return True

_EFFECT_HANDLERS = {
    "regen_health":       _effect_regen_health,
    "phoenix_injector":   _effect_phoenix_injector,
    "adrenaline_shot":    _effect_adrenaline_shot,
    "rad_suppressor":     _effect_rad_suppressor,
}