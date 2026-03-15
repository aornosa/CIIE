# Sistema de Armas - Guía de Implementación

## Descripción General

El sistema de armas está dividido en dos categorías principales:
- **Melee**: Armas de cuerpo a cuerpo (cuchillos, palos, etc.)
- **Ranged**: Armas de fuego (rifles, pistolas, escopetas, etc.)

Ambas heredan de la clase base `Weapon` y de `MonoliteBehaviour` para integrarse con el ciclo de vida del juego.

## Estructura de Clases

### Clase Base: `Weapon`

```
weapons/weapon_module.py
├── asset: pygame.Surface
├── name: str
├── damage: int
├── parent: Character (set cuando se equipa)
├── audio_emitter: AudioEmitter
├── update(): void
├── get_name(): str
├── get_damage(): int
├── on_equipped(parent): void
└── on_unequipped(): void
```

### Armas Cuerpo a Cuerpo: `Melee`

**Ubicación**: `weapons/melee/melee.py`

**Características**:
- Ataque rápido con cooldown
- Detección de golpe mediante raycast
- Sistema de arco de ataque para detectar múltiples objetivos
- Animación de ataque con duración configurable

**Propiedades principales**:
```python
reach: int              # Distancia máxima de ataque (píxeles)
attack_speed: float    # Ataques por segundo
attack_cooldown: float # Tiempo entre ataques (segundos)
reach_radius: int      # Radio de detección en arco
```

**Métodos principales**:
```python
attack(): bool         # Realiza un ataque
can_attack(): bool     # Verifica si puede atacar
get_attack_progress(): float  # Progreso de animación (0.0-1.0)
```

**Ejemplo de creación**:
```python
class MiArmaBlanca(Melee):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/mi_arma.png",
            name="Mi Arma",
            damage=50,
            reach=100,          # Máximo alcance
            attack_speed=1.5,   # 1.5 ataques por segundo
            reach_radius=50     # Radio de detección en arco
        )
```

### Armas de Fuego: `Ranged`

**Ubicación**: `weapons/ranged/ranged.py`

**Características**:
- Sistema de munición con cargador
- Recarga desde inventario del jugador
- Efectos de partículas al disparar
- Sistema de raycast para detección de impactos
- Control de cadencia de fuego

**Propiedades principales**:
```python
max_range: int         # Alcance máximo en píxeles
ammo_type: str         # Tipo de munición ("9x19", "7.62", "12gauge")
clip_size: int         # Capacidad del cargador
fire_rate: float       # Tiempo entre disparos (segundos)
reload_time: float     # Tiempo de recarga (segundos)
muzzle_speed: int      # Velocidad de salida del proyectil
muzzle_offset: tuple   # Offset del cañón (forward, side)
current_clip: int      # Munición en cargador actual
```

**Métodos principales**:
```python
shoot(): bool          # Dispara el arma
reload(): bool         # Inicia recarga
can_shoot(): bool      # Verifica si puede disparar
is_reloading(): bool   # Verifica si está recargando
get_ammo_count(): tuple # Retorna (en_cargador, en_reserva)
```

**Ejemplo de creación**:
```python
class MiRifle(Ranged):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/mi_rifle.png",
            name="Mi Rifle",
            damage=60,
            max_range=1500,
            ammo_type="7.62",      # Tipo de munición
            clip_size=30,
            fire_rate=0.1,         # 0.1s = 10 disparos/segundo
            reload_time=2.5,       # 2.5 segundos de recarga
            muzzle_offset=(35, 15) # (hacia adelante, hacia lado)
        )
```

## Tipos de Munición

Definidos en `weapons/weapon_module.py`:

```python
AMMO_TYPES = {
    "9x19": "assets/ammo/9x19/data.json",      # Pistola/SMG
    "7.62": "assets/ammo/7.62/data.json",      # Rifle
    "12gauge": "assets/ammo/12Gauge/data.json" # Escopeta
}
```

Cada tipo de munición tiene un archivo `data.json` que contiene:
- `asset_particle_path`: Ruta de la textura del proyectil
- Otras propiedades específicas de munición

## Integración con Personajes

### Equipar un Arma

```python
from character_scripts.player.player import Player
from weapons.ranged.ranged_types import AK47

player = Player(...)
rifle = AK47()
player.inventory.add_weapon(player, rifle, "primary")
```

### Usar un Arma

```python
# Para armas de fuego
active_weapon = player.inventory.get_weapon("primary")
if isinstance(active_weapon, Ranged):
    if active_weapon.shoot():
        print("Disparo exitoso")
    
    # Recargar si es necesario
    if active_weapon.current_clip == 0:
        active_weapon.reload()

# Para armas de cuerpo a cuerpo
elif isinstance(active_weapon, Melee):
    if active_weapon.attack():
        print("Ataque exitoso")
```

## Sistema de Daño

### Aplicación de Daño

```python
# En Melee.attack()
target.take_damage(self.damage)

# En Ranged (después del raycast)
hit[0].owner.take_damage(self.damage)
```

### Requisitos del Objetivo

El objetivo debe tener:
```python
def take_damage(self, damage: int):
    self.health -= damage
    if self.health <= 0:
        self.die()
```

## Sistema de Sonido

### Configuración de Sonidos

En `core/audio/sound_cache.py`, agregar:

```python
SOUNDS = {
    # Armas de fuego
    "9x19_shoot": pygame.mixer.Sound("assets/sounds/9x19_shoot.wav"),
    "7.62_shoot": pygame.mixer.Sound("assets/sounds/7.62_shoot.wav"),
    "12gauge_shoot": pygame.mixer.Sound("assets/sounds/12gauge_shoot.wav"),
    
    # Recarga
    "9x19_reload": pygame.mixer.Sound("assets/sounds/9x19_reload.wav"),
    "7.62_reload": pygame.mixer.Sound("assets/sounds/7.62_reload.wav"),
    
    # Armas blancas
    "knife_slash": pygame.mixer.Sound("assets/sounds/knife_slash.wav"),
    "baton_hit": pygame.mixer.Sound("assets/sounds/baton_hit.wav"),
    "machete_slash": pygame.mixer.Sound("assets/sounds/machete_slash.wav"),
}
```

## Mejoras Futuras

- [ ] **Balísticas realistas**: Caída de proyectiles con distancia
- [ ] **Dispersión**: Spread pattern basado en estabilidad
- [ ] **Efectos de retroceso**: Recoil afectando puntería
- [ ] **Modificaciones**: Sistema de attachment (miras, silenciadores, etc.)
- [ ] **Durabilidad**: Desgaste de armas con uso
- [ ] **Especializaciones**: Diferentes tipos de munición
- [ ] **Animaciones**: Estados de carga/disparo/recarga visibles
- [ ] **UI de munición**: Contador en HUD

## Checklist de Implementación

- [x] Clase base `Weapon`
- [x] Clase `Melee` con ataque básico
- [x] Clase `Ranged` con sistema de munición
- [x] Tipos de armas específicas
- [ ] Integración completa con inventario del jugador
- [ ] Sistema de sonido configurado
- [ ] Animaciones de ataque/disparo
- [ ] UI de estado del arma (munición, recarga)
- [ ] Sistema de balance y daño
- [ ] Efectos visuales mejorados
