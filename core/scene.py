from abc import ABC, abstractmethod


class Scene(ABC):
    """Base class for all game scenes (menu, gameplay, pause, etc.)"""

    def __init__(self):
        self.director = None  # Set by SceneDirector when pushed

    @abstractmethod
    def handle_events(self, input_handler):
        """Process input for this scene."""
        pass

    @abstractmethod
    def update(self, delta_time):
        """Update scene logic."""
        pass

    @abstractmethod
    def render(self, screen):
        """Draw the scene."""
        pass

    def on_enter(self):
        """Called when this scene becomes the active scene (first time or after replace)."""
        pass

    def on_exit(self):
        """Called when this scene is permanently removed from the stack."""
        pass

    def on_pause(self):
        """Called when another scene is pushed on top of this one."""
        pass

    def on_resume(self):
        """Called when the scene on top is popped and this one becomes active again."""
        pass