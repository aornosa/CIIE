# Developer Manual: Scene Director
The Scene Director system manages game flow through a **stack of scenes**. Only the scene at the top of the stack is active — it receives input, updates, and renders. All other scenes are dormant.

## Core Components

### Scene (`core/scene.py`)
Abstract base class for all scenes. Every scene must implement three methods:

| Method | Purpose |
|--------|---------|
| `handle_events(input_handler)` | Process input for this scene |
| `update(delta_time)` | Update scene logic |
| `render(screen)` | Draw the scene |

**Optional lifecycle hooks:**
- `on_enter()` — called when this scene becomes the active scene (pushed or uncovered by a pop)
- `on_exit()` — called when this scene is no longer active (popped or covered by a push)

### SceneDirector (`core/scene_director.py`)
Manages the scene stack and delegates the frame cycle to the active scene.

**Stack operations:**

| Method | Effect |
|--------|--------|
| `push(scene)` | Pauses the current scene (`on_exit`) and activates the new one (`on_enter`) |
| `pop()` | Removes the current scene and resumes the previous one. If the stack is empty, sets `running = False` |
| `replace(scene)` | Pops the current scene and pushes a new one (no going back) |
| `get_current()` | Returns the scene at the top of the stack |

**Shared references (set from `main.py`):**
- `director.clock` — the pygame Clock, accessible by scenes via `self.director.clock`
- `director._input_handler` — the InputHandler, available via `self.director._input_handler`


## Main Loop (`main.py`)
The main loop is minimal — it only handles pygame events and delegates everything to the director:

```python
director = SceneDirector()
director.clock = clock
director.push(MainMenuScene())

while director.running:
    im.reset_frame()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            director.running = False
        im.handle_event(event)

    screen.fill(SCREEN_BACKGROUND_COLOR)

    director.handle_events(im)          # → active scene handles input
    director.update(clock.get_time() / 1000.0)  # → active scene updates
    director.render(screen)             # → active scene renders

    MonoliteBehaviour.update_all(clock.get_time() / 1000)
    pygame.display.flip()
    clock.tick(FPS if FPS > 0 else 0)
```

## Pause System

The pause works via two mechanisms working together:

### 1. Scene Stack Isolation
When `PauseScene` is pushed, only `PauseScene` receives `handle_events`, `update`, and `render`. `GameScene` is dormant — `game_loop()` is never called.

### 2. MonoliteBehaviour.time_scale
`MonoliteBehaviour.update_all()` runs every frame in `main.py` (outside the scene stack), so game entities (bullets, particles, enemies) would still tick during pause.

To fix this, `MonoliteBehaviour` has a `time_scale` class variable:
- `GameScene.on_enter()` → `time_scale = 1.0` (normal speed)
- `GameScene.on_exit()` → `time_scale = 0.0` (frozen)

`update_all()` multiplies `dt * time_scale`, so all entities receive `delta_time = 0` during pause.