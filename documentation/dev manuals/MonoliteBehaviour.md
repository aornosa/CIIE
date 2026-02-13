# Developer Manual: MonoliteBehaviour
The `MonoliteBehaviour` class is a base class that emulates Unity's internal MonoBehaviour. 
MonoliteBehaviour provides a structure for providing all inheriting classes with lifecycle methods
that communicate events to the former.

## Lifecycle Methods
The following lifecycle methods are provided by `MonoliteBehaviour`:

#### Initialization
- `Awake()`: Called when the script instance is being loaded.
- `Start()`: Called before the first frame update, if the script instance is enabled.
<br></br>
#### Runtime
- `Update()`: Called once per frame, if the script instance is enabled.
<br></br>
#### State Changes
- `OnEnable()`: Called when the object becomes enabled and active.
- `OnDisable()`: Called when the behaviour becomes disabled or inactive.
<br></br>
#### Last Execution
- `OnDestroy()`: Called when the MonoBehaviour will be destroyed.

## Usage
To use `MonoliteBehaviour`, simply create a new class that inherits from it and implement any
of the lifecycle methods as needed. For example:

```python
from core.monolite_behaviour import MonoliteBehaviour

class Enemy(MonoliteBehaviour):
    def awake(self):
        enemy_health = 100
        spawn_enemy()
        
    def update(self, delta_time):
        player_position = get_player_position()
        move_towards(player_position)
        
        if player_position - enemy_position < attack_range:
            attack_player()
    
    def on_destroy():
        drop_loot()
```

### How it Works
When a class inherits from `MonoliteBehaviour`, any lifecycle methods mentioned above,
when implemented, will be triggered automatically by the Monolite system, given the appropiate
circustances.

