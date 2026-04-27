# ============================================================
# Snake Game — extended from Practice 8
# New features:
#   1. Food with different weights (Cherry=1, Apple=3, Star=5)
#   2. Food disappears after a timer; replaced with a new one
# ============================================================

import pygame
import sys
import random
import time as _time   # renamed to avoid clash with game variable
from pygame.locals import *

# ── Initialize pygame ────────────────────────────────────────
pygame.init()

# ── Grid & window constants ───────────────────────────────────
CELL         = 20    # pixel size of one grid cell
COLS         = 30    # grid columns  → WIDTH  = 600 px
ROWS         = 30    # grid rows     → play area = 600 px tall
HUD_HEIGHT   = 50    # pixels for the top HUD bar
WIDTH        = COLS * CELL
HEIGHT       = ROWS * CELL + HUD_HEIGHT

# ── Speed / level constants ───────────────────────────────────
FPS_BASE     = 8     # starting snake speed (frames per second)
FPS_STEP     = 2     # FPS increase per level
FOOD_PER_LVL = 3     # foods eaten to advance one level

# ── Food lifetime ─────────────────────────────────────────────
FOOD_LIFETIME = 5.0  # seconds before a food item disappears

# ── Colors ───────────────────────────────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
DARK_GREEN   = (0,   140, 0)
LIGHT_GREEN  = (0,   200, 50)
GRAY         = (40,  40,  40)
WALL_COLOR   = (80,  80,  80)
HUD_BG       = (20,  20,  20)
YELLOW       = (255, 215, 0)
RED          = (200, 0,   0)

# ── Food type definitions ─────────────────────────────────────
# Each dict defines one food variant:
#   value  — score points and growth signal (snake grows once per eat)
#   color  — fill color of the food circle
#   label  — single character drawn on the food
#   prob   — relative probability used by random.choices()
FOOD_TYPES = [
    {"name": "Cherry", "value": 1,  "color": (220,  30,  30), "label": "♥", "prob": 60},
    {"name": "Apple",  "value": 3,  "color": ( 60, 180,  60), "label": "A", "prob": 30},
    {"name": "Star",   "value": 5,  "color": (255, 200,   0), "label": "★", "prob": 10},
]
FOOD_PROBS = [ft["prob"] for ft in FOOD_TYPES]   # weights for random.choices

# ── Display ──────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

# ── Fonts ────────────────────────────────────────────────────
font_hud   = pygame.font.SysFont("Courier New", 20, bold=True)
font_big   = pygame.font.SysFont("Courier New", 48, bold=True)
font_med   = pygame.font.SysFont("Courier New", 20)
font_food  = pygame.font.SysFont("Segoe UI Emoji", 12, bold=True)  # for food label
font_timer = pygame.font.SysFont("Courier New", 11, bold=True)


# ════════════════════════════════════════════════════════════ #
#  Helper: grid coords → pixel Rect                            #
# ════════════════════════════════════════════════════════════ #
def cell_rect(col, row):
    """Convert grid position (col, row) to a pygame.Rect on screen."""
    return pygame.Rect(col * CELL, HUD_HEIGHT + row * CELL, CELL, CELL)


# ════════════════════════════════════════════════════════════ #
#  Snake                                                       #
# ════════════════════════════════════════════════════════════ #
class Snake:
    """Represents the player-controlled snake."""

    def __init__(self):
        # Start in the middle of the grid, 3 segments, moving right
        mid_col = COLS // 2
        mid_row = ROWS // 2
        # body[0] is the head; list of (col, row) tuples
        self.body      = [(mid_col, mid_row),
                          (mid_col - 1, mid_row),
                          (mid_col - 2, mid_row)]
        self.direction = (1, 0)   # (dc, dr) — currently moving right
        self.grew      = False    # flag set after eating; cleared after move

    def set_direction(self, dc, dr):
        """
        Update direction unless the new direction is a direct reversal.
        Reversing into yourself would be an instant self-collision.
        """
        if (dc, dr) != (-self.direction[0], -self.direction[1]):
            self.direction = (dc, dr)

    def move(self):
        """Advance the snake one cell. Grow if food was eaten last step."""
        head_col, head_row = self.body[0]
        dc, dr = self.direction
        new_head = (head_col + dc, head_row + dr)

        self.body.insert(0, new_head)   # prepend new head

        if self.grew:
            self.grew = False           # reset flag — tail is kept (snake grew)
        else:
            self.body.pop()             # remove tail — same length

    def grow(self):
        """Signal that the snake should grow on its next move."""
        self.grew = True

    def head(self):
        """Return the (col, row) position of the snake's head."""
        return self.body[0]

    def occupies(self, col, row):
        """Return True if any part of the snake is at (col, row)."""
        return (col, row) in self.body

    def self_collision(self):
        """Return True if the head overlaps any body segment (death condition)."""
        return self.body[0] in self.body[1:]

    def draw(self, surf):
        """Draw each body segment; head is drawn in a lighter shade."""
        for i, (col, row) in enumerate(self.body):
            color = LIGHT_GREEN if i == 0 else DARK_GREEN
            rect  = cell_rect(col, row)
            pygame.draw.rect(surf, color, rect)
            pygame.draw.rect(surf, BLACK, rect, 1)   # thin border for segmented look


# ════════════════════════════════════════════════════════════ #
#  Food  (weighted type + disappear timer)                      #
# ════════════════════════════════════════════════════════════ #
class Food:
    """
    A food item on the grid.

    - Type is chosen randomly using weighted probability:
        Cherry (60%) → +1 pt    Apple (30%) → +3 pts    Star (10%) → +5 pts
    - Each food has a FOOD_LIFETIME-second timer.
      When the timer expires the food disappears and a new one spawns.
    - The timer is drawn as a small countdown above the food circle.
      The food pulses (changes radius) as time runs out to warn the player.
    """

    def __init__(self, snake):
        # Pick a random type with weighted probability
        self.food_type  = random.choices(FOOD_TYPES, weights=FOOD_PROBS, k=1)[0]
        self.value      = self.food_type["value"]   # score value of this food
        self.pos        = self._random_pos(snake)
        self.spawn_time = _time.time()              # wall-clock time of spawn

    def _random_pos(self, snake):
        """
        Find a valid grid cell:
          - Not on the outer border wall (col/row 0 or max)
          - Not occupied by any snake segment
        """
        while True:
            col = random.randint(1, COLS - 2)
            row = random.randint(1, ROWS - 2)
            if not snake.occupies(col, row):
                return (col, row)

    def time_left(self):
        """Return seconds remaining before this food disappears (≥ 0)."""
        elapsed = _time.time() - self.spawn_time
        return max(0.0, FOOD_LIFETIME - elapsed)

    def is_expired(self):
        """Return True when the food's lifetime has elapsed."""
        return self.time_left() <= 0

    def draw(self, surf):
        """
        Draw the food circle with:
          - its type color
          - a small label character
          - a countdown number above the food
          - a pulsing radius when < 2 s remain (urgency signal)
        """
        col, row = self.pos
        rect     = cell_rect(col, row)
        center   = rect.center
        t_left   = self.time_left()

        # Base radius; shrinks slightly as time runs out to create a pulse
        base_r = CELL // 2 - 2
        if t_left < 2.0:
            # Pulse: oscillate radius ±2 px at ~4 Hz
            pulse = int(2 * abs(pygame.time.get_ticks() % 250 - 125) / 125)
            radius = base_r - 2 + pulse
        else:
            radius = base_r

        # Draw filled circle + dark outline
        pygame.draw.circle(surf, self.food_type["color"], center, radius)
        pygame.draw.circle(surf, BLACK, center, radius, 1)

        # Food label (emoji / letter) in the centre
        lbl = font_food.render(self.food_type["label"], True, WHITE)
        surf.blit(lbl, (center[0] - lbl.get_width() // 2,
                        center[1] - lbl.get_height() // 2))

        # Timer countdown above the food cell
        # Color shifts red when < 2 s remain
        timer_color = (255, 60, 60) if t_left < 2.0 else (200, 200, 200)
        t_txt = font_timer.render(f"{t_left:.1f}s", True, timer_color)
        surf.blit(t_txt, (rect.x, rect.y - 14))

        # Value badge (bottom-right corner of cell)
        val_txt = font_timer.render(f"+{self.value}", True, YELLOW)
        surf.blit(val_txt, (rect.right - val_txt.get_width(),
                            rect.bottom - val_txt.get_height()))


# ════════════════════════════════════════════════════════════ #
#  Board drawing                                               #
# ════════════════════════════════════════════════════════════ #
def draw_board(surf):
    """Fill the play area, draw faint grid, then paint the border wall."""
    # Dark play area background
    surf.fill(BLACK, pygame.Rect(0, HUD_HEIGHT, WIDTH, HEIGHT - HUD_HEIGHT))

    # Faint grid lines for visual reference
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(surf, GRAY, cell_rect(c, r), 1)

    # Solid border wall (outermost row/column on each side)
    for c in range(COLS):
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(c, 0))
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(c, ROWS - 1))
    for r in range(ROWS):
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(0, r))
        pygame.draw.rect(surf, WALL_COLOR, cell_rect(COLS - 1, r))


# ════════════════════════════════════════════════════════════ #
#  HUD                                                         #
# ════════════════════════════════════════════════════════════ #
def draw_hud(surf, score, level, foods_eaten):
    """
    Top bar showing:
      - Score (left)
      - Level (centre)
      - Progress dots toward next level (right)
      - Food type legend (far right)
    """
    pygame.draw.rect(surf, HUD_BG, pygame.Rect(0, 0, WIDTH, HUD_HEIGHT))

    # Score
    score_txt = font_hud.render(f"SCORE: {score}", True, WHITE)
    surf.blit(score_txt, (10, HUD_HEIGHT // 2 - score_txt.get_height() // 2))

    # Level (centred)
    level_txt = font_hud.render(f"LEVEL: {level}", True, YELLOW)
    surf.blit(level_txt, (WIDTH // 2 - level_txt.get_width() // 2,
                          HUD_HEIGHT // 2 - level_txt.get_height() // 2))

    # Progress dots — one per food needed to level up
    dot_x = WIDTH - 20
    for i in range(FOOD_PER_LVL - 1, -1, -1):
        color = RED if i < foods_eaten else GRAY
        pygame.draw.circle(surf, color, (dot_x, HUD_HEIGHT // 2), 7)
        pygame.draw.circle(surf, WHITE,  (dot_x, HUD_HEIGHT // 2), 7, 1)
        dot_x -= 20

    # Mini food type legend (bottom strip of HUD)
    lx = WIDTH - 10
    for ft in reversed(FOOD_TYPES):
        leg = font_timer.render(f"{ft['label']}+{ft['value']}", True, ft["color"])
        lx -= leg.get_width() + 6
        surf.blit(leg, (lx, HUD_HEIGHT - 14))


# ════════════════════════════════════════════════════════════ #
#  Overlay helpers                                             #
# ════════════════════════════════════════════════════════════ #
def draw_overlay(surf, title, subtitle):
    """Draw a semi-transparent black overlay with a title and subtitle."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surf.blit(overlay, (0, 0))

    t = font_big.render(title,    True, YELLOW)
    s = font_med.render(subtitle, True, WHITE)
    surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
    surf.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.update()


def level_up_screen(surf, level):
    """Show a brief 'LEVEL UP' message and pause for 1.2 seconds."""
    draw_overlay(surf, f"LEVEL {level}!", "Get ready...")
    pygame.time.wait(1200)


# ════════════════════════════════════════════════════════════ #
#  Boundary collision                                          #
# ════════════════════════════════════════════════════════════ #
def hit_wall(snake):
    """
    Return True if the snake's head has moved into a border wall cell.
    Border cells are column 0, column COLS-1, row 0, and row ROWS-1.
    """
    col, row = snake.head()
    return col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1


# ════════════════════════════════════════════════════════════ #
#  Main game loop                                              #
# ════════════════════════════════════════════════════════════ #
def run_game():
    """
    Run one full game session.
    Returns (score, level, reason) when the game ends.
    reason is 'wall', 'self', or 'expired' (food expired too many times — unused,
    but left as an extension point).
    """
    snake            = Snake()
    food             = Food(snake)   # first food item
    score            = 0
    level            = 1
    foods_this_level = 0             # how many foods eaten in the current level
    fps              = FPS_BASE      # snake move speed (frames per second)

    # Buffer the next direction so a keypress between frames isn't lost
    next_dir = snake.direction

    while True:

        # ── Events ───────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if   event.key in (K_UP,    K_w): next_dir = (0, -1)
                elif event.key in (K_DOWN,  K_s): next_dir = (0,  1)
                elif event.key in (K_LEFT,  K_a): next_dir = (-1, 0)
                elif event.key in (K_RIGHT, K_d): next_dir = (1,  0)
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Apply the buffered direction (validates reversal internally)
        snake.set_direction(*next_dir)

        # ── Move snake one step ───────────────────────────────
        snake.move()

        # ── Death checks ──────────────────────────────────────
        if hit_wall(snake):
            return score, level, "wall"
        if snake.self_collision():
            return score, level, "self"

        # ── Food expiry check ─────────────────────────────────
        # If the food's timer ran out, spawn a new food without awarding points
        if food.is_expired():
            food = Food(snake)   # new random type and position

        # ── Eating check ──────────────────────────────────────
        if snake.head() == food.pos:
            snake.grow()                         # grow on next move
            score            += food.value * 10  # higher-value food → more score
            foods_this_level += 1
            food = Food(snake)                   # spawn fresh food immediately

            # ── Level up ─────────────────────────────────────
            if foods_this_level >= FOOD_PER_LVL:
                level            += 1
                foods_this_level  = 0
                fps               = FPS_BASE + (level - 1) * FPS_STEP
                level_up_screen(screen, level)

        # ── Drawing ──────────────────────────────────────────
        draw_board(screen)
        food.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, level, foods_this_level)

        pygame.display.update()
        clock.tick(fps)   # controls snake speed: higher fps = faster snake


# ════════════════════════════════════════════════════════════ #
#  Game Over screen                                            #
# ════════════════════════════════════════════════════════════ #
def game_over_screen(score, level, reason):
    """
    Display the game-over overlay and wait for the player to
    press R (restart) or Q / Esc (quit).
    Returns True to restart, False to quit.
    """
    reasons = {
        "wall": "Hit a wall!",
        "self": "Ate yourself!",
    }
    msg = reasons.get(reason, "Game over!")
    draw_overlay(
        screen,
        "GAME OVER",
        f"{msg}   Score: {score}   Level: {level}   |   R = restart   Q = quit"
    )
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                if event.key == K_r:
                    return True    # restart
                if event.key in (K_q, K_ESCAPE):
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