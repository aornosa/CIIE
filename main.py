import pygame
import pygame._sdl2 as sdl2
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()

# Try to initialize audio, but continue if it fails (no audio device)
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Warning: Audio initialization failed ({e}). Game will run without sound.")

if not pygame.get_init():
    exit(-1)

from settings import *

# Detectar resolución real del monitor
info = pygame.display.Info()
NATIVE_W = info.current_w
NATIVE_H = info.current_h

# El surface interno sigue siendo SCREEN_WIDTH x SCREEN_HEIGHT (1920x1080)
# pygame.SCALED se encarga de escalar al monitor automáticamente
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pygame.SCALED | pygame.FULLSCREEN
)

from core import input_handler as ih
from core.scene_director import SceneDirector
from scenes.main_menu_scene import MainMenuScene
from core.monolite_behaviour import MonoliteBehaviour
from core.audio.music_manager import MusicManager

pygame.display.set_caption("Armengard")
pygame.display.set_icon(pygame.image.load("assets/icon.png").convert())

# Set clock
clock = pygame.time.Clock()
im = ih.InputHandler()

# Scene Director — manages scene stack, starts at main menu
director = SceneDirector()
director.clock = clock
director.push(MainMenuScene())

while director.running:
    im.reset_frame()  # Clear single-frame inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            director.running = False
        im.handle_event(event)
        MusicManager.instance().handle_event(event)

    screen.fill(SCREEN_BACKGROUND_COLOR)
    director.handle_events(im)
    director.update(clock.get_time() / 1000.0)
    director.render(screen)

    # Monolite Behavior update
    MonoliteBehaviour.update_all(clock.get_time() / 1000)
    pygame.display.flip()

    if FPS > 0:
        clock.tick(FPS)
    else:
        clock.tick()  # No limit on FPS