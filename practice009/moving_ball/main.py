import pygame
import sys
from ball import Ball

WIDTH, HEIGHT = 600, 600
FPS = 60
BG_COLOR = (255, 255, 255)
GRID_COLOR = (235, 235, 235)


def draw_background(screen):
    screen.fill(BG_COLOR)
    # Subtle grid for visual reference
    step = 40
    for x in range(0, WIDTH, step):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, step):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


def draw_ui(screen, font, ball):
    # Position label
    pos_text = font.render(f"x: {ball.x}   y: {ball.y}", True, (160, 160, 160))
    screen.blit(pos_text, (10, HEIGHT - 28))

    # Controls hint
    hint = font.render("Arrow keys to move", True, (200, 200, 200))
    screen.blit(hint, (WIDTH - hint.get_width() - 10, HEIGHT - 28))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Courier New", 14)

    # Start ball in center
    ball = Ball(WIDTH // 2, HEIGHT // 2, radius=25,
                screen_width=WIDTH, screen_height=HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            ball.handle_key(pygame.K_UP)
        if keys[pygame.K_DOWN]:
            ball.handle_key(pygame.K_DOWN)
        if keys[pygame.K_LEFT]:
            ball.handle_key(pygame.K_LEFT)
        if keys[pygame.K_RIGHT]:
            ball.handle_key(pygame.K_RIGHT)

        draw_background(screen)
        ball.draw(screen)
        draw_ui(screen, font, ball)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()