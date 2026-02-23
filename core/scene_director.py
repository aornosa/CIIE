class SceneDirector:
    """Manages a stack of scenes. The scene on top is the active one."""

    def __init__(self):
        self.scene_stack = []
        self.running = True
        self._input_handler = None  # Shared reference, set from main loop

    def push(self, scene):
        """Push a new scene onto the stack (pauses the current one)."""
        if self.scene_stack:
            self.scene_stack[-1].on_exit()

        scene.director = self
        self.scene_stack.append(scene)
        scene.on_enter()

    def pop(self):
        """Remove the current scene and return to the previous one."""
        if self.scene_stack:
            old_scene = self.scene_stack.pop()
            old_scene.on_exit()
            old_scene.director = None

        if self.scene_stack:
            self.scene_stack[-1].on_enter()
        else:
            self.running = False

    def replace(self, scene):
        """Replace the current scene with a new one (no going back)."""
        if self.scene_stack:
            old_scene = self.scene_stack.pop()
            old_scene.on_exit()
            old_scene.director = None

        scene.director = self
        self.scene_stack.append(scene)
        scene.on_enter()

    def get_current(self):
        """Return the scene at the top of the stack, or None."""
        return self.scene_stack[-1] if self.scene_stack else None

    # -- Delegated to the active scene each frame --

    def handle_events(self, input_handler):
        self._input_handler = input_handler  # Keep reference for scenes that need it
        scene = self.get_current()
        if scene:
            scene.handle_events(input_handler)

    def update(self, delta_time):
        scene = self.get_current()
        if scene:
            scene.update(delta_time)

    def render(self, screen):
        scene = self.get_current()
        if scene:
            scene.render(screen)
