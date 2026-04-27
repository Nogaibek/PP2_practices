import pygame
import sys
from clock import MickeyClock
 
WIDTH = 500
HEIGHT = 500
FPS = 1 
 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey's Clock")
 
    clock_app = MickeyClock(WIDTH, HEIGHT)
    clock = pygame.time.Clock()
 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
 
        clock_app.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
 
 
if __name__ == "__main__":
    main()
 