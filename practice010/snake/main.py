# ============================================================
# Snake Game — extended from lecture example
# Features: wall collision, smart food spawn, levels,
#           speed increase, score/level HUD, comments
# ============================================================

import pygame
import sys
import random
from pygame.locals import *

# ── Initialize pygame ────────────────────────────────────────
pygame.init()

# ── Constants ────────────────────────────────────────────────
CELL        = 20          # size of one grid cell in pixels
COLS        = 30          # number of columns  (width  = COLS * CELL = 600)
ROWS        = 30          # number of rows     (height = ROWS * CELL + HUD)
HUD_HEIGHT  = 50          # pixels reserved at the top for score/level
WIDTH       = COLS * CELL
HEIGHT      = ROWS * CELL + HUD_HEIGHT

FPS_BASE    = 8           # starting frames-per-second (snake speed)
FPS_STEP    = 2           # extra FPS added per level
FOOD_PER_LVL= 3           # foods needed to advance one level

# ── Colors ───────────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
DARK_GREEN  = (0,   140, 0)
LIGHT_GREEN = (0,   200, 50)
RED         = (200, 0,   0)
YELLOW      = (255, 215, 0)
GRAY        = (40,  40,  40)
WALL_COLOR  = (80,  80,  80)
HUD_BG      = (20,  20,  20)

# ── Display ──────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

# ── Fonts ────────────────────────────────────────────────────
font_hud   = pygame.font.SysFont("Courier New", 20, bold=True)
font_big   = pygame.font.SysFont("Courier New", 48, bold=True)
font_med   = pygame.font.SysFont("Courier New", 24)


# ════════════════════════════════════════════════════════════ #
#  Helper: convert grid coords → pixel rect                    #
# ════════════════════════════════════════════════════════════ #
def cell_rect(col, row):
    """Return a pygame.Rect for the grid cell (col, row)."""
    return pygame.Rect(col * CELL, HUD_HEIGHT + row * CELL, CELL, CELL)


# ════════════════════════════════════════════════════════════ #
#  Snake                                                       #
# ════════════════════════════════════════════════════════════ #
class Snake:
    def __init__(self):
        # Snake starts as 3 cells in the middle of the grid, moving right
        mid_col = COLS // 2
        mid_row = ROWS // 2
        # body is a list of (col, row) tuples; head is body[0]
        self.body      = [(mid_col, mid_row),
                          (mid_col - 1, mid_row),
                          (mid_col - 2, mid_row)]
        self.direction = (1, 0)   # (dc, dr): right
        self.grew      = False    # flag: did snake eat food this step?

    def set_direction(self, dc, dr):
        """Change direction — prevent reversing into itself."""
        # Ignore if trying to go directly opposite current direction
        if (dc, dr) != (-self.direction[0], -self.direction[1]):
            self.direction = (dc, dr)

    def move(self):
        """Advance the snake one cell in the current direction."""
        head_col, head_row = self.body[0]
        dc, dr = self.direction
        new_head = (head_col + dc, head_row + dr)

        # Insert new head at the front
        self.body.insert(0, new_head)

        # Remove tail only if the snake did NOT eat food last step
        if self.grew:
            self.grew = False   # reset flag
        else:
            self.body.pop()

    def grow(self):
        """Signal that the snake should grow on the next move."""
        self.grew = True

    def head(self):
        """Return (col, row) of the snake's head."""
        return self.body[0]

    def occupies(self, col, row):
        """Check whether any part of the snake occupies (col, row)."""
        return (col, row) in self.body

    def self_collision(self):
        """Return True if the head overlaps any body segment."""
        return self.body[0] in self.body[1:]

    def draw(self, surf):
        """Draw every segment; head is a brighter shade."""
        for i, (col, row) in enumerate(self.body):
            color = LIGHT_GREEN if i == 0 else DARK_GREEN
            rect  = cell_rect(col, row)
            pygame.draw.rect(surf, color, rect)
            # thin border around each cell for a segmented look
            pygame.draw.rect(surf, BLACK, rect, 1)


# ════════════════════════════════════════════════════════════ #
#  Food                                                        #
# ════════════════════════════════════════════════════════════ #
class Food:
    def __init__(self, snake):
        self.pos = self._random_pos(snake)

    def _random_pos(self, snake):
        """
        Pick a random grid cell that is:
        - not on the outer wall (border cells)
        - not occupied by any snake segment
        """
        while True:
            col = random.randint(1, COLS - 2)   # 1…COLS-2 avoids wall columns
            row = random.randint(1, ROWS - 2)   # 1…ROWS-2 avoids wall rows
            if not snake.occupies(col, row):
                return (col, row)

    def respawn(self, snake):
        """Move food to a new valid position after being eaten."""
        self.pos = self._random_pos(snake)

    def draw(self, surf):
        col, row = self.pos
        rect = cell_rect(col, row)
        # Draw a red circle inside the cell
        center = rect.center
        radius = CELL // 2 - 2
        pygame.draw.circle(surf, RED,    center, radius)
        pygame.draw.circle(surf, YELLOW, center, radius // 3)   # shine dot


# ════════════════════════════════════════════════════════════ #
#  Draw grid & walls                                           #
# ════════════════════════════════════════════════════════════ #
def draw_board(surf):
    """Fill background, draw grid lines, then draw the border wall."""
    # Dark background for the play area
    surf.fill(BLACK, pygame.Rect(0, HUD_HEIGHT, WIDTH, HEIGHT - HUD_HEIGHT))

    # Faint grid lines (optional visual aid)
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(surf, GRAY, cell_rect(c, r), 1)

    # Border wall — top/bottom rows and left/right columns
    for c in range(COLS):
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(c, 0))           # top wall
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(c, ROWS - 1))    # bottom wall
    for r in range(ROWS):
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(0, r))           # left wall
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(COLS - 1, r))    # right wall


# ════════════════════════════════════════════════════════════ #
#  HUD                                                         #
# ════════════════════════════════════════════════════════════ #
def draw_hud(surf, score, level, foods_this_level):
    """Render the top bar with score, level, and level-progress dots."""
    pygame.draw.rect(surf, HUD_BG, pygame.Rect(0, 0, WIDTH, HUD_HEIGHT))

    score_txt = font_hud.render(f"SCORE: {score}", True, WHITE)
    level_txt = font_hud.render(f"LEVEL: {level}", True, YELLOW)
    surf.blit(score_txt, (10,  HUD_HEIGHT // 2 - score_txt.get_height() // 2))
    surf.blit(level_txt, (WIDTH // 2 - level_txt.get_width() // 2,
                          HUD_HEIGHT // 2 - level_txt.get_height() // 2))

    # Progress dots: filled = food eaten this level
    dot_x = WIDTH - 20
    for i in range(FOOD_PER_LVL - 1, -1, -1):
        color = RED if i < foods_this_level else GRAY
        pygame.draw.circle(surf, color, (dot_x, HUD_HEIGHT // 2), 7)
        pygame.draw.circle(surf, WHITE,  (dot_x, HUD_HEIGHT // 2), 7, 1)
        dot_x -= 20


# ════════════════════════════════════════════════════════════ #
#  Overlay screens                                             #
# ════════════════════════════════════════════════════════════ #
def draw_overlay(surf, title, subtitle):
    """Semi-transparent overlay with a title and subtitle."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surf.blit(overlay, (0, 0))

    t = font_big.render(title,    True, YELLOW)
    s = font_med.render(subtitle, True, WHITE)
    surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
    surf.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.update()


def level_up_screen(surf, level):
    """Brief 'LEVEL UP' flash."""
    draw_overlay(surf, f"LEVEL {level}!", "Get ready...")
    pygame.time.wait(1200)


# ════════════════════════════════════════════════════════════ #
#  Wall / boundary collision check                             #
# ════════════════════════════════════════════════════════════ #
def hit_wall(snake):
    """
    Return True if the snake's head has entered a border cell
    (col == 0, col == COLS-1, row == 0, or row == ROWS-1).
    """
    col, row = snake.head()
    return col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1


# ════════════════════════════════════════════════════════════ #
#  Main game function                                          #
# ════════════════════════════════════════════════════════════ #
def run_game():
    snake           = Snake()
    food            = Food(snake)
    score           = 0
    level           = 1
    foods_this_level= 0          # counts food eaten in current level
    fps             = FPS_BASE   # current speed (increases with level)

    # Direction buffer — store the next intended direction so diagonal
    # inputs between frames are not lost
    next_dir = snake.direction

    running = True
    while running:

        # ── Event handling ───────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_UP    or event.key == K_w:
                    next_dir = (0, -1)
                elif event.key == K_DOWN  or event.key == K_s:
                    next_dir = (0,  1)
                elif event.key == K_LEFT  or event.key == K_a:
                    next_dir = (-1, 0)
                elif event.key == K_RIGHT or event.key == K_d:
                    next_dir = (1,  0)
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Apply buffered direction
        snake.set_direction(*next_dir)

        # ── Move snake ───────────────────────────────────────
        snake.move()

        # ── Collision: wall ──────────────────────────────────
        if hit_wall(snake):
            return score, level, "wall"   # game over

        # ── Collision: self ──────────────────────────────────
        if snake.self_collision():
            return score, level, "self"   # game over

        # ── Food eaten? ──────────────────────────────────────
        if snake.head() == food.pos:
            snake.grow()
            score           += 10
            foods_this_level += 1
            food.respawn(snake)   # food won't spawn on wall or snake

            # ── Level up ─────────────────────────────────────
            if foods_this_level >= FOOD_PER_LVL:
                level           += 1
                foods_this_level = 0
                fps              = FPS_BASE + (level - 1) * FPS_STEP
                level_up_screen(screen, level)

        # ── Drawing ──────────────────────────────────────────
        draw_board(screen)
        food.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, level, foods_this_level)

        pygame.display.update()
        clock.tick(fps)   # speed controlled by current level


# ════════════════════════════════════════════════════════════ #
#  Game-over screen → returns True to restart, False to quit   #
# ════════════════════════════════════════════════════════════ #
def game_over_screen(score, level, reason):
    msg = "Hit a wall!" if reason == "wall" else "Ate yourself!"
    draw_overlay(screen,
                 "GAME OVER",
                 f"{msg}  Score: {score}  Level: {level}  |  R = restart  Q = quit")
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                if event.key == K_r:
                    return True    # restart
                if event.key == K_q or event.key == K_ESCAPE:
                    return False   # quit


# ════════════════════════════════════════════════════════════ #
#  Entry point                                                 #
# ════════════════════════════════════════════════════════════ #
while True:
    score, level, reason = run_game()
    if not game_over_screen(score, level, reason):
        break

pygame.quit()
sys.exit()