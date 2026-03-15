import pygame

pygame.init()

try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Warning: Audio initialization failed ({e}). Game will run without sound.")

if not pygame.get_init():
    exit(-1)

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_BACKGROUND_COLOR, FPS
)

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    flags=pygame.SCALED | pygame.FULLSCREEN,
)

from core import input_handler as ih
from core.scene_director import SceneDirector
from core.monolite_behaviour import MonoliteBehaviour
from scenes.main_menu_scene import MainMenuScene
from core.audio.music_manager import MusicManager

pygame.display.set_caption("Armengard")
pygame.display.set_icon(pygame.image.load("assets/icon.png").convert())

clock    = pygame.time.Clock()
im       = ih.InputHandler()
director = SceneDirector()
director.clock = clock
director.push(MainMenuScene())

while director.running:
    im.reset_frame()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            director.running = False
        MusicManager.instance().handle_event(event)
        im.handle_event(event)

    screen.fill(SCREEN_BACKGROUND_COLOR)
    director.handle_events(im)
    director.update(clock.get_time() / 1000.0)
    director.render(screen)

    MonoliteBehaviour.update_all(clock.get_time() / 1000.0)
    pygame.display.flip()

    if FPS > 0:
        clock.tick(FPS)
    else:
        clock.tick()