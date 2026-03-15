class SceneDirector:

    def __init__(self):
        self.scene_stack = []
        self.running = True
        self._input_handler = None  
        self.clock = None            

    def push(self, scene):
        if self.scene_stack:
            self.scene_stack[-1].on_pause()

        scene.director = self
        self.scene_stack.append(scene)
        scene.on_enter()

    def pop(self):
        if self.scene_stack:
            old_scene = self.scene_stack.pop()
            old_scene.on_exit()
            old_scene.director = None

        if self.scene_stack:
            self.scene_stack[-1].on_resume()
        else:
            self.running = False

    def replace(self, scene):
        if self.scene_stack:
            old_scene = self.scene_stack.pop()
            old_scene.on_exit()
            old_scene.director = None

        scene.director = self
        self.scene_stack.append(scene)
        scene.on_enter()

    def get_current(self):
        return self.scene_stack[-1] if self.scene_stack else None

    def handle_events(self, input_handler):
        self._input_handler = input_handler
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