# ============================================================
# Racer Game — extended from Practice 8
# New features:
#   1. Coins with different weights (Bronze=1, Silver=3, Gold=5)
#   2. Enemy speed increases every N coins collected
# ============================================================

import pygame
import sys
import os
import random
import time
from pygame.locals import *

# Directory where main.py lives — used to build absolute paths to assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Initialize pygame ────────────────────────────────────────
pygame.init()

# ── Constants ────────────────────────────────────────────────
FPS            = 60
SCREEN_WIDTH   = 400
SCREEN_HEIGHT  = 600

SPEED          = 5     # current speed of enemy cars (updated each frame)
SCORE          = 0     # score: increases each time an enemy passes the player
COINS          = 0     # total weighted coin value collected

# Every N coin-points → enemy speeds up by SPEED_STEP
SPEED_UP_EVERY = 10    # coin threshold between speed increases
SPEED_STEP     = 1     # how many pixels/frame to add per threshold
MAX_SPEED      = 20    # cap so the game stays playable

# ── Colors ───────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
YELLOW = (255, 215, 0)

# ── Coin type definitions ─────────────────────────────────────
# Each entry: (name, value/weight, color, outline_color, probability)
# Probability values are relative weights for random.choices()
COIN_TYPES = [
    {"name": "Bronze", "value": 1, "color": (205, 127, 50),  "outline": (139, 90, 43),   "prob": 60},
    {"name": "Silver", "value": 3, "color": (192, 192, 192), "outline": (128, 128, 128), "prob": 30},
    {"name": "Gold",   "value": 5, "color": (255, 215, 0),   "outline": (180, 140, 0),   "prob": 10},
]
COIN_PROBS = [ct["prob"] for ct in COIN_TYPES]   # weights list for random.choices

# ── Fonts ────────────────────────────────────────────────────
font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 18)
font_tiny  = pygame.font.SysFont("Verdana", 13)

# ── Display ──────────────────────────────────────────────────
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")

# ── Clock ────────────────────────────────────────────────────
FramePerSec = pygame.time.Clock()


# ════════════════════════════════════════════════════════════ #
#  Scrolling Background                                        #
# ════════════════════════════════════════════════════════════ #
class Background:
    """Infinitely scrolling road background using two image copies."""

    def __init__(self):
        self.bgimage   = pygame.image.load(os.path.join(BASE_DIR, "AnimatedStreet.png"))
        self.rectBGimg = self.bgimage.get_rect()
        self.bgY1      = 0
        self.bgX1      = 0
        # Second copy starts one full image-height above the first
        self.bgY2      = -self.rectBGimg.height
        self.bgX2      = 0

    def update(self):
        """Scroll both copies downward at current SPEED; wrap when off-screen."""
        self.bgY1 += SPEED
        self.bgY2 += SPEED
        if self.bgY1 >= self.rectBGimg.height:
            self.bgY1 = -self.rectBGimg.height
        if self.bgY2 >= self.rectBGimg.height:
            self.bgY2 = -self.rectBGimg.height

    def render(self):
        """Draw both background copies onto the display surface."""
        DISPLAYSURF.blit(self.bgimage, (self.bgX1, self.bgY1))
        DISPLAYSURF.blit(self.bgimage, (self.bgX2, self.bgY2))


# ════════════════════════════════════════════════════════════ #
#  Enemy Car                                                   #
# ════════════════════════════════════════════════════════════ #
class Enemy(pygame.sprite.Sprite):
    """Enemy car that falls from the top of the screen."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Enemy.png"))
        self.rect  = self.image.get_rect()
        # Spawn at a random horizontal position at the very top
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """
        Move downward at current SPEED.
        When the car passes the bottom: award score and respawn at top.
        """
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


# ════════════════════════════════════════════════════════════ #
#  Player Car                                                  #
# ════════════════════════════════════════════════════════════ #
class Player(pygame.sprite.Sprite):
    """Player car controlled by left/right arrow keys."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Player.png"))
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        """Move left or right; clamp position to screen boundaries."""
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]  and self.rect.left  > 0:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)


# ════════════════════════════════════════════════════════════ #
#  Coin  (with weight / value)                                 #
# ════════════════════════════════════════════════════════════ #
class Coin(pygame.sprite.Sprite):
    """
    A coin that falls down the road.

    Type is chosen randomly with weighted probability:
      Bronze (60%) → worth 1 coin-point
      Silver (30%) → worth 3 coin-points
      Gold   (10%) → worth 5 coin-points

    The coin's appearance (color + value label) reflects its type.
    Collecting more coin-points causes the enemy to drive faster.
    """

    RADIUS = 13  # pixel radius of the coin circle

    def __init__(self):
        super().__init__()

        # Weighted random selection of coin type
        self.coin_type = random.choices(COIN_TYPES, weights=COIN_PROBS, k=1)[0]
        self.value     = self.coin_type["value"]

        # Draw the coin onto a transparent surface
        size       = self.RADIUS * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        pygame.draw.circle(self.image, self.coin_type["color"],
                           (self.RADIUS, self.RADIUS), self.RADIUS)
        pygame.draw.circle(self.image, self.coin_type["outline"],
                           (self.RADIUS, self.RADIUS), self.RADIUS, 2)

        # Value label in the centre of the coin
        label_font = pygame.font.SysFont("Verdana", 11, bold=True)
        label      = label_font.render(str(self.value), True, (60, 40, 0))
        self.image.blit(label, (self.RADIUS - label.get_width()  // 2,
                                self.RADIUS - label.get_height() // 2))

        self.rect = self.image.get_rect()
        self._respawn()

    def _respawn(self):
        """Reset coin to a random position at the top of the screen."""
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """Fall at current road speed; respawn when below screen."""
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()


# ════════════════════════════════════════════════════════════ #
#  Sprite Groups                                               #
# ════════════════════════════════════════════════════════════ #
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies     = pygame.sprite.Group()
enemies.add(E1)

coins       = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, C1)

# ── Background ───────────────────────────────────────────────
background = Background()

# ── Sounds (skipped gracefully if audio files are missing) ───
try:
    pygame.mixer.music.load(os.path.join(BASE_DIR, "bg_music.ogg"))
    pygame.mixer.music.play(-1)
    crash_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "crash.wav"))
    coin_sound  = pygame.mixer.Sound(os.path.join(BASE_DIR, "coin.wav"))
except Exception:
    crash_sound = None
    coin_sound  = None


# ════════════════════════════════════════════════════════════ #
#  HUD                                                         #
# ════════════════════════════════════════════════════════════ #
def draw_hud():
    """
    Draw the heads-up display:
      top-left  — score + current speed level
      top-right — total coins + next speed-up threshold
      bottom    — coin type legend
    """
    # Current speed level (how many thresholds have been crossed)
    speed_level = COINS // SPEED_UP_EVERY

    # ── Score (top-left) ──────────────────────────────────────
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    spd_text = font_tiny.render(f"Speed lv: {speed_level}", True, (160, 0, 0))
    DISPLAYSURF.blit(spd_text, (10, 34))

    # ── Coins (top-right) ─────────────────────────────────────
    coin_text = font_small.render(f"Coins: {COINS}", True, (100, 60, 0))
    cx        = SCREEN_WIDTH - coin_text.get_width() - 15

    # Small gold dot as icon
    pygame.draw.circle(DISPLAYSURF, YELLOW,        (cx - 14, 19), 10)
    pygame.draw.circle(DISPLAYSURF, (180, 140, 0), (cx - 14, 19), 10, 2)
    DISPLAYSURF.blit(coin_text, (cx, 10))

    # "Next speed boost at X coins"
    next_at   = (speed_level + 1) * SPEED_UP_EVERY
    next_text = font_tiny.render(f"Boost at: {next_at}", True, (140, 60, 0))
    DISPLAYSURF.blit(next_text, (SCREEN_WIDTH - next_text.get_width() - 8, 34))

    # ── Coin legend (bottom-left) ─────────────────────────────
    legend_y = SCREEN_HEIGHT - 60
    for ct in COIN_TYPES:
        pygame.draw.circle(DISPLAYSURF, ct["color"],   (18, legend_y), 8)
        pygame.draw.circle(DISPLAYSURF, ct["outline"], (18, legend_y), 8, 1)
        leg = font_tiny.render(f"{ct['name']} +{ct['value']}", True, BLACK)
        DISPLAYSURF.blit(leg, (32, legend_y - 7))
        legend_y += 18


# ════════════════════════════════════════════════════════════ #
#  Main Game Loop                                              #
# ════════════════════════════════════════════════════════════ #
while True:

    # ── Events ───────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # ── Scroll & render background ────────────────────────────
    background.update()
    background.render()

    # ── Draw all sprites ──────────────────────────────────────
    for sprite in all_sprites:
        DISPLAYSURF.blit(sprite.image, sprite.rect)

    # ── Update sprite positions ───────────────────────────────
    P1.move()
    E1.move()
    for coin in coins:
        coin.move()

    # ── Coin collection ───────────────────────────────────────
    collected = pygame.sprite.spritecollide(P1, coins, False)
    for coin in collected:
        COINS += coin.value   # add the coin's weighted value to total
        if coin_sound:
            coin_sound.play()
        coin._respawn()       # send collected coin back to the top

    # ── Randomly spawn an extra coin ──────────────────────────
    # 1-in-300 chance each frame → roughly one new coin every 5 seconds
    if random.randint(1, 300) == 1:
        new_coin = Coin()
        coins.add(new_coin)
        all_sprites.add(new_coin)

    # ── Adjust enemy speed based on coins collected ───────────
    # Formula: base speed (5) + one SPEED_STEP per SPEED_UP_EVERY coins
    # Example with defaults: 0-9 coins → speed 5, 10-19 → 6, 20-29 → 7 …
    new_speed = 5 + (COINS // SPEED_UP_EVERY) * SPEED_STEP
    SPEED     = min(new_speed, MAX_SPEED)   # never exceed MAX_SPEED

    # ── Player vs Enemy collision → Game Over ─────────────────
    if pygame.sprite.spritecollideany(P1, enemies):
        if crash_sound:
            crash_sound.play()
        time.sleep(0.5)

        # Render Game Over screen with final stats
        DISPLAYSURF.fill(RED)
        go_surf = font.render("Game Over", True, BLACK)
        DISPLAYSURF.blit(go_surf, (SCREEN_WIDTH // 2 - go_surf.get_width() // 2, 210))

        stats = font_small.render(f"Score: {SCORE}   Coins: {COINS}", True, BLACK)
        DISPLAYSURF.blit(stats, (SCREEN_WIDTH // 2 - stats.get_width() // 2, 300))

        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # ── Draw HUD on top of everything ────────────────────────
    draw_hud()

    # ── Refresh display ───────────────────────────────────────
    pygame.display.update()
    FramePerSec.tick(FPS)