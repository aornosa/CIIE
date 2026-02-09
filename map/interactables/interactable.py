class Interactable:
    def __init__(self, name, description, interact_text, interact_radius=50):
        self.name = name
        self.description = description
        self.interact_text = interact_text
        self.interact_radius = interact_radius

    def get_tooltip(self):
        return self.interact_text

    def interact(self, player):
        pass