"""
core/monolite_behaviour.py
---------------------------
Base class for all game objects that need per-frame updates.

delta_time  — atributo de clase, actualizado cada frame en update_all().
              Accesible globalmente como MonoliteBehaviour.delta_time.
time_scale  — escala de tiempo global (0 = pausa, 1 = normal).

Para ver los prints de creación en consola, activar en settings.py:
    ENABLE_MONOLITE_DEBUG = True
"""
from __future__ import annotations
import inspect


class MonoliteBehaviour:
    _instances: list["MonoliteBehaviour"] = []
    time_scale: float = 1.0
    delta_time: float = 0.0   # último delta escalado; usado por partículas etc.

    def __init__(self):
        MonoliteBehaviour._instances.append(self)

        try:
            from settings import ENABLE_MONOLITE_DEBUG
            if ENABLE_MONOLITE_DEBUG:
                print(f"[Monolite] + {self.__class__.__name__}")
        except ImportError:
            pass

    def update(self, delta_time: float = 0.0):
        pass

    def destroy(self):
        if self in MonoliteBehaviour._instances:
            MonoliteBehaviour._instances.remove(self)

    @classmethod
    def update_all(cls, delta_time: float):
        scaled = delta_time * cls.time_scale
        cls.delta_time = scaled   # disponible globalmente este frame

        for instance in list(cls._instances):
            # Llamar con o sin argumento según la firma del método
            try:
                params = inspect.signature(instance.update).parameters
                required = [p for p in params.values()
                            if p.name != "self"
                            and p.default is inspect.Parameter.empty]
                if required:
                    instance.update(scaled)
                else:
                    instance.update()
            except Exception as e:
                print(f"[Monolite] Error en {instance.__class__.__name__}.update(): {e}")