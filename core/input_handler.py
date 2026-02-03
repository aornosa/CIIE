import pygame

class InputHandler:
    def __init__(self):
        self.actions = {
            "move_x": 0,
            "move_y": 0,
            "attack": False,
            "aim": False,
            "interact": False,
            "inventory": False,
            "pause": False,

            # Lookaround -> change arrow keys to ctrl + mouse movement
            "look_x": 0,
            "look_y": 0,
        }
        self.mouse_position = pygame.Vector2(0, 0)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.actions["move_x"] += -1
            elif event.key == pygame.K_d:
                self.actions["move_x"] += 1
            elif event.key == pygame.K_w:
                self.actions["move_y"] += -1
            elif event.key == pygame.K_s:
                self.actions["move_y"] += 1
            elif event.key == pygame.K_e:
                self.actions["interact"] = True
            elif event.key == pygame.K_i:
                self.actions["inventory"] = True

            elif event.key == pygame.K_UP:
                self.actions["look_y"] += -1
            elif event.key == pygame.K_DOWN:
                self.actions["look_y"] += 1
            elif event.key == pygame.K_LEFT:
                self.actions["look_x"] += -1
            elif event.key == pygame.K_RIGHT:
                self.actions["look_x"] += 1

            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.actions["move_x"] += 1
            elif event.key == pygame.K_d:
                self.actions["move_x"] += -1
            elif event.key == pygame.K_w:
                self.actions["move_y"] += 1
            elif event.key == pygame.K_s:
                self.actions["move_y"] += -1
            elif event.key == pygame.K_e:
                self.actions["interact"] = False

            elif event.key == pygame.K_UP:
                self.actions["look_y"] += 1
            elif event.key == pygame.K_DOWN:
                self.actions["look_y"] += -1
            elif event.key == pygame.K_LEFT:
                self.actions["look_x"] += 1
            elif event.key == pygame.K_RIGHT:
                self.actions["look_x"] += -1

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.actions["attack"] = True
            if event.button == 3:  # Right click
                self.actions["aim"] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                self.actions["attack"] = False
            if event.button == 3:  # Right click
                self.actions["aim"] = False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_position = pygame.Vector2(event.pos)
