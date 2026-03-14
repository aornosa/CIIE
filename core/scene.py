from abc import ABC, abstractmethod

class Scene(ABC):

    def __init__(self):
        self.director = None  

    @abstractmethod
    def handle_events(self, input_handler):
        pass

    @abstractmethod
    def update(self, delta_time):
        pass

    @abstractmethod
    def render(self, screen):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass