import pygame
import pygame._sdl2 as sdl2   

pygame.init()

if not pygame.get_init():
    exit(-1)

from settings import *

# Set screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SCALED | pygame.HIDDEN)
window = sdl2.Window.from_display_module()
window.size = (int(SCREEN_WIDTH * SCREEN_SCALE), int(SCREEN_HEIGHT * SCREEN_SCALE))
window.position = sdl2.WINDOWPOS_CENTERED
window.show()

from core import input_handler as ih
from game import game_loop

from core.monolite_behaviour import MonoliteBehaviour


pygame.display.set_caption("Armengard")
pygame.display.set_icon(pygame.image.load("assets/icon.png").convert())

# Set clock
clock = pygame.time.Clock()
im = ih.InputHandler()

# render loop
running = True

# Monolite Behavior initialization
#MonoliteBehaviour.instantiate_all()

while running:
    im.reset_frame()  # Clear single-frame inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        im.handle_event(event)

    screen.fill(SCREEN_BACKGROUND_COLOR)  # Clear screen with black

    # main loop
    game_loop(screen, clock, im)

    # Monolite Behavior update
    MonoliteBehaviour.update_all(clock.get_time()/1000)

    pygame.display.flip()

    if FPS > 0:
        clock.tick(FPS)
    else :
        clock.tick()  # No limit on FPS