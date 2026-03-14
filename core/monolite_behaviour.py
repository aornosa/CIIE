from __future__ import annotations
import inspect

class MonoliteBehaviour:
    _instances: list["MonoliteBehaviour"] = []
    time_scale: float = 1.0
    delta_time: float = 0.0

    def __init__(self):
        MonoliteBehaviour._instances.append(self)
        try:
            from settings import ENABLE_MONOLITE_DEBUG
            if ENABLE_MONOLITE_DEBUG:
                print(f"[Monolite] + {self.__class__.__name__}")
        except ImportError:
            pass

    def update(self, delta_time: float = 0.0): pass

    def destroy(self):
        if self in MonoliteBehaviour._instances:
            MonoliteBehaviour._instances.remove(self)

    @classmethod
    def update_all(cls, delta_time: float):
        scaled     = delta_time * cls.time_scale
        cls.delta_time = scaled
        # list() evita errores si algún update() llama a destroy() y modifica _instances
        for instance in list(cls._instances):
            try:
                # Inspecciona la firma para pasar delta_time solo si el método lo requiere
                params   = inspect.signature(instance.update).parameters
                required = [p for p in params.values()
                            if p.name != "self"
                            and p.default is inspect.Parameter.empty]
                if required:
                    instance.update(scaled)
                else:
                    instance.update()
            except Exception as e:
                print(f"[Monolite] Error en {instance.__class__.__name__}.update(): {e}")