import pygame


class Ball:
    def __init__(self, x, y, radius, screen_width, screen_height):
        self.x = x
        self.y = y
        self.radius = radius
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.step = 20

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # Only move if new position stays fully within screen bounds
        if self.radius <= new_x <= self.screen_width - self.radius:
            self.x = new_x
        if self.radius <= new_y <= self.screen_height - self.radius:
            self.y = new_y

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.move(0, -self.step)
        elif key == pygame.K_DOWN:
            self.move(0, self.step)
        elif key == pygame.K_LEFT:
            self.move(-self.step, 0)
        elif key == pygame.K_RIGHT:
            self.move(self.step, 0)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)