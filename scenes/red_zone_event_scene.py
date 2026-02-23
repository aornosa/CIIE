from scenes.event_scene import EventScene
from dialogs.test_dialogs import create_red_zone_dialog


class RedZoneEventScene(EventScene):
    """Scripted event scene triggered by the red zone.
    Inherits all behavior from EventScene – just binds the red zone dialog.
    """

    def __init__(self, game_scene):
        super().__init__(game_scene, create_red_zone_dialog())
