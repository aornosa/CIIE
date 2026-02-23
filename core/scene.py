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
        """Called when this scene becomes the active scene."""
        pass

    def on_exit(self):
        """Called when this scene is no longer the active scene."""
        pass
