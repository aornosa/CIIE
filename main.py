import pygame

pygame.init()

if not pygame.get_init():
    exit(-1)

from core import input_handler as ih
from game import game_loop
from settings import *


# Set screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Horde Game")
pygame.display.set_icon(pygame.image.load("assets/icon.png"))

# Set clock
clock = pygame.time.Clock()
im = ih.InputHandler()

# render loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        im.handle_event(event)

    screen.fill(SCREEN_BACKGROUND_COLOR)  # Clear screen with black

    # main loop
    game_loop(screen, clock, im)


    pygame.display.flip()
    clock.tick(FPS)