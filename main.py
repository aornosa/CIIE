import pygame

pygame.init()

if not pygame.get_init():
    exit(-1)

from core import input_handler as ih
from game import game_loop
from settings import *

from core.monolite_behaviour import MonoliteBehaviour


# Set screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Horde Game")
pygame.display.set_icon(pygame.image.load("assets/icon.png"))

# Set clock
clock = pygame.time.Clock()
im = ih.InputHandler()

# render loop
running = True

# Monolite Behavior initialization
#MonoliteBehaviour.instantiate_all()

while running:
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