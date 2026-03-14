import pygame

HOTKEY_KEYS = [
    pygame.K_1, pygame.K_2, pygame.K_3,
    pygame.K_4, pygame.K_5, pygame.K_6,
]


class InputHandler:
    def __init__(self):
        self.actions = {
            "move_x": 0,
            "move_y": 0,
            "swap_weapon": False,
            "attack": False,
            "aim": False,
            "interact": False,
            "inventory": False,
            "reload": False,
            "pause": False,
            "shop": False,
            "look_around": False,
            "use_item": False,
            "hotkey_slot": -1,
            "dash": False,
            "look_x": 0,
            "look_y": 0,
        }
        self.mouse_position    = pygame.Vector2(0, 0)
        self.keys_just_pressed = {}

    def reset_frame(self):
        self.keys_just_pressed.clear()
        self.actions["use_item"]    = False
        self.actions["pause"]       = False
        self.actions["hotkey_slot"] = -1
        self.actions["dash"]        = False
        # attack y aim se sincronizan con el estado real del ratón cada frame
        mouse = pygame.mouse.get_pressed()
        self.actions["attack"] = mouse[0]
        self.actions["aim"]    = mouse[2]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.keys_just_pressed[event.key] = True

            if event.key in HOTKEY_KEYS:
                self.actions["hotkey_slot"] = HOTKEY_KEYS.index(event.key)

            elif event.key == pygame.K_a:
                self.actions["move_x"] += -1
            elif event.key == pygame.K_d:
                self.actions["move_x"] += 1
            elif event.key == pygame.K_w:
                self.actions["move_y"] += -1
            elif event.key == pygame.K_s:
                self.actions["move_y"] += 1
            elif event.key == pygame.K_e:
                self.actions["interact"] = True
            elif event.key == pygame.K_r:
                self.actions["reload"] = True
            elif event.key == pygame.K_q:
                self.actions["swap_weapon"] = True
            elif event.key == pygame.K_TAB:
                self.actions["inventory"] = True
            elif event.key == pygame.K_f:
                self.actions["use_item"] = True
            elif event.key == pygame.K_LSHIFT:
                self.actions["dash"] = True

            elif event.key == pygame.K_UP:
                self.actions["look_y"] += -1
            elif event.key == pygame.K_DOWN:
                self.actions["look_y"] += 1
            elif event.key == pygame.K_LEFT:
                self.actions["look_x"] += -1
            elif event.key == pygame.K_RIGHT:
                self.actions["look_x"] += 1
            elif event.key == pygame.K_LCTRL:
                self.actions["look_around"] = True

            elif event.key == pygame.K_p:
                self.actions["shop"] = True
            elif event.key == pygame.K_ESCAPE:
                self.actions["pause"] = True

        elif event.type == pygame.KEYUP:
            # Las teclas de movimiento usan +=/-= para soportar dos teclas pulsadas a la vez
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
            elif event.key == pygame.K_LCTRL:
                self.actions["look_around"] = False

            elif event.key == pygame.K_UP:
                self.actions["look_y"] += 1
            elif event.key == pygame.K_DOWN:
                self.actions["look_y"] += -1
            elif event.key == pygame.K_LEFT:
                self.actions["look_x"] += 1
            elif event.key == pygame.K_RIGHT:
                self.actions["look_x"] += -1

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.actions["attack"]     = True
                self.actions["click_drop"] = True
            if event.button == 3:
                self.actions["aim"] = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.actions["attack"] = False
            if event.button == 3:
                self.actions["aim"] = False

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_position = pygame.Vector2(event.pos)

    def get_keys_pressed(self):
        """Get current state of all keys"""
        return pygame.key.get_pressed()

    def get_keys_just_pressed(self):
        """Get dictionary of keys pressed this frame"""
        return self.keys_just_pressed