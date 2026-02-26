# Developer Manual: Scene Director

The **Scene Director** system provides a stack-based mechanism for managing game screens
(menus, gameplay, pause, scripted events, etc.). It is inspired by the classic
**Director / Scene Stack** pattern used in mobile and indie game engines.

The system is composed of two components: `Scene` (abstract base) and `SceneDirector` (the manager).

---

## Scene

`Scene` is the abstract base class that all game screens must inherit from.
It defines the interface that the director uses to drive each screen every frame.

### Lifecycle Methods

| Method | When it is called |
|---|---|
| `on_enter()` | When the scene becomes the **active** one (pushed or restored after a pop) |
| `handle_events(input_handler)` | Each frame — before `update`. Receives the shared `InputHandler` |
| `update(delta_time)` | Each frame — game logic, state transitions |
| `render(screen)` | Each frame — all drawing goes here |
| `on_exit()` | When the scene is **removed** from the top of the stack (popped or replaced) |

`on_enter` and `on_exit` are optional — they have empty default implementations.
`handle_events`, `update`, and `render` are **abstract** and must be implemented.

### Attributes

- `self.director` — Reference to the `SceneDirector` that owns this scene.
  Set automatically when the scene is pushed. Use it to trigger stack operations
  (`push`, `pop`, `replace`) from inside the scene.

---

## SceneDirector

`SceneDirector` owns the scene stack and delegates each frame's work to the scene at the top.

### Methods

- `push(scene)` — Pushes `scene` on top of the stack.
  Calls `on_exit` on the previous top, then `on_enter` on the new one.
  The previous scene is **paused but kept in memory**.

- `pop()` — Removes the top scene.
  Calls `on_exit` on it, then `on_enter` on the scene below (now active again).
  If the stack becomes empty, `running` is set to `False` and the main loop exits.

- `replace(scene)` — Discards the current top and replaces it with `scene`.
  Unlike `pop` + `push`, the previous scene is **not restored** afterwards.

- `get_current()` — Returns the active scene, or `None` if the stack is empty.

- `handle_events(input_handler)` — Delegates to the active scene. Also stores
  `input_handler` in `self._input_handler` so nested scenes can retrieve it.

- `update(delta_time)` — Delegates to the active scene.

- `render(screen)` — Delegates to the active scene.

### Attributes

- `scene_stack` — The internal list. Index `-1` is always the active scene.
- `running` — `True` while the game loop should continue. Set to `False` automatically
  when the last scene is popped.
- `_input_handler` — Shared reference to the current frame's `InputHandler`.
  Scenes can read it via `self.director._input_handler`.

---

## Setting Up in `main.py`

```python
from core.scene_director import SceneDirector
from scenes.main_menu_scene import MainMenuScene

director = SceneDirector()
director.push(MainMenuScene())        # First scene on the stack

while director.running:
    im.reset_frame()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            director.running = False
        im.handle_event(event)

    delta_time = clock.get_time() / 1000.0
    screen.fill(BACKGROUND_COLOR)

    director.handle_events(im)
    director.update(delta_time)
    director.render(screen)

    pygame.display.flip()
    clock.tick(FPS)
```

---

## Creating a Scene

Inherit from `Scene` and implement the three abstract methods.

```python
from core.scene import Scene

class MyScene(Scene):

    def __init__(self):
        super().__init__()
        self.selected = 0
        self.options = ["Option A", "Option B", "Exit"]

    def on_enter(self):
        print("MyScene is now active")

    def handle_events(self, input_handler):
        if input_handler.keys_just_pressed.get(pygame.K_DOWN):
            self.selected = (self.selected + 1) % len(self.options)
        if input_handler.keys_just_pressed.get(pygame.K_RETURN):
            self._select(self.selected)

    def update(self, delta_time):
        pass  # No continuous logic in this example

    def render(self, screen):
        for i, text in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            surf = font.render(text, True, color)
            screen.blit(surf, (100, 100 + i * 40))

    def _select(self, index):
        if index == 2:
            self.director.pop()       # Return to the previous scene
```

---

## Stack Operations

### `push` — Add a new scene on top (previous one is paused)

Use it when you want to place a new screen over the current one without losing it.
Examples: opening the pause menu over the game, showing a dialog over the gameplay.

```python
# From any scene:
self.director.push(PauseScene(self))
```

```
Stack before:  [GameScene]
Stack after:   [GameScene, PauseScene]   ← active
```

### `pop` — Remove the current scene (return to the one below)

Use it when the current scene finishes and you want to go back to the previous one.

```python
self.director.pop()
```

```
Stack before:  [GameScene, PauseScene]
Stack after:   [GameScene]               ← active again
```

**⚠️ Warning:** After calling `pop()`, `self.director` is set to `None`.
If you need to chain operations, save the reference first:

```python
director = self.director   # Save BEFORE calling pop
director.pop()
director.push(AnotherScene())
```

### `replace` — Swap the current scene (no going back)

Use it to switch to a new scene without keeping the current one.
Examples: transitioning from the main menu to gameplay, or from Game Over to the main menu.

```python
self.director.replace(GameScene())
```

```
Stack before:  [MainMenuScene]
Stack after:   [GameScene]               ← MainMenuScene discarded
```

---

## Stacked Scenes

One of the main advantages of the stack is that a scene can **render the scene below it**
before drawing itself, creating overlay effects (pause, dialogs, inventory).

```python
class PauseScene(Scene):

    def __init__(self, game_scene):
        super().__init__()
        self.game_scene = game_scene    # Reference to the frozen game scene

    def render(self, screen):
        # 1. Draw the frozen game world underneath
        self.game_scene.render(screen)

        # 2. Semi-transparent dim overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # 3. Pause menu UI on top
        draw_pause_menu(screen, self.selected)

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            self.director.pop()         # ESC closes the pause menu
```

---

## Scripted Event Scenes

For cinematic events that briefly take control and then return to the game,
use `push` + automatic `pop` when the sequence ends.

```python
class MyEventScene(Scene):

    STEP_DIALOG = 0
    STEP_DONE   = 1

    def __init__(self, game_scene):
        super().__init__()
        self.game_scene = game_scene
        self.step = self.STEP_DIALOG
        self.dialog_manager = DialogManager()
        self.dialog_manager.start_dialog(create_my_dialog())

    def handle_events(self, input_handler):
        if self.step == self.STEP_DIALOG:
            self.dialog_manager.handle_input(
                input_handler.get_keys_pressed(),
                input_handler.get_keys_just_pressed(),
            )

    def update(self, delta_time):
        if self.step == self.STEP_DIALOG:
            if not self.dialog_manager.is_dialog_active:
                self.director.pop()     # Dialog finished – return to the game

    def render(self, screen):
        self.game_scene.render(screen)  # Frozen game in the background
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        draw_dialog_ui(screen, self.dialog_manager)
```

To trigger the event from `GameScene`:

```python
# In GameScene.handle_events or GameScene.update:
self.director.push(MyEventScene(self))
```

---

## Operation Summary

| Situation | Operation |
|---|---|
| Open pause / dialog / inventory | `push` |
| Close pause / dialog / inventory | `pop` |
| Go to gameplay from the main menu | `replace` |
| Game Over → main menu | `replace` |
| Scripted event ends → return to game | `pop` |
| Exit the application | let the stack become empty after the last `pop` |
