import pygame
from core.scene import Scene
from core.audio.audio_manager import AudioManager
from core.audio.audio_mixer_category import SoundCategory
from ui.settings_menu import draw_settings_menu

_STEP = 0.05  
_OPTIONS_DEF = [
    {"label": "Controles", "type": "action"},
    {"label": "Música",    "type": "slider", "category": SoundCategory.MUSIC},
    {"label": "Efectos",   "type": "slider", "category": SoundCategory.SFX},
    {"label": "Volver",    "type": "action"},
]

class SettingsScene(Scene):

    def __init__(self):
        super().__init__()
        self.selected = 0

    def _render_options(self):
        am = AudioManager.instance()
        result = []
        for opt in _OPTIONS_DEF:
            if opt["type"] == "slider":
                result.append({
                    "label":  opt["label"],
                    "slider": am.mixer_volumes.get(opt["category"], 1.0),
                })
            else:
                result.append({"label": opt["label"]})
        return result

    def handle_events(self, input_handler):
        if input_handler.actions.get("pause"):
            input_handler.actions["pause"] = False
            self.director.pop()
            return

        jp = input_handler.keys_just_pressed

        # Navegar arriba/abajo
        if jp.get(pygame.K_UP) or jp.get(pygame.K_w):
            self.selected = (self.selected - 1) % len(_OPTIONS_DEF)
        if jp.get(pygame.K_DOWN) or jp.get(pygame.K_s):
            self.selected = (self.selected + 1) % len(_OPTIONS_DEF)

        opt = _OPTIONS_DEF[self.selected]

        if opt["type"] == "slider":
            am  = AudioManager.instance()
            cat = opt["category"]
            vol = am.mixer_volumes.get(cat, 1.0)
            if jp.get(pygame.K_LEFT)  or jp.get(pygame.K_a):
                am.set_mixer_volume(cat, vol - _STEP)
            if jp.get(pygame.K_RIGHT) or jp.get(pygame.K_d):
                am.set_mixer_volume(cat, vol + _STEP)

        elif jp.get(pygame.K_RETURN):
            self._activate(opt)

    def update(self, delta_time):
        pass

    def render(self, screen):
        draw_settings_menu(screen, self._render_options(), self.selected)

    def on_enter(self):
        pygame.mouse.set_visible(True)

    def _activate(self, opt):
        if opt["label"] == "Controles":
            from scenes.keybindings_scene import KeybindingsScene
            self.director.push(KeybindingsScene())
        elif opt["label"] == "Volver":
            self.director.pop()