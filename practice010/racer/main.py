# ============================================================
# Racer Game — based on CodersLegacy Pygame Tutorial (Parts 1-3)
# Extra features: randomly appearing coins + coin counter
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
FPS          = 60
SCREEN_WIDTH = 400
SCREEN_HEIGHT= 600
SPEED        = 5       # starting speed of enemy cars
SCORE        = 0       # score increases over time
COINS        = 0       # number of collected coins

# ── Colors ───────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
GREEN  = (0,   255, 0)
BLUE   = (0,   0,   255)
YELLOW = (255, 215, 0)   # coin color

# ── Fonts ────────────────────────────────────────────────────
font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over  = font.render("Game Over", True, BLACK)

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
    """Handles the infinitely scrolling road background."""

    def __init__(self):
        # Load road image and get its rect dimensions
        self.bgimage    = pygame.image.load(os.path.join(BASE_DIR, "AnimatedStreet.png"))
        self.rectBGimg  = self.bgimage.get_rect()
        # Two copies placed one after another vertically
        self.bgY1       = 0
        self.bgX1       = 0
        self.bgY2       = -self.rectBGimg.height   # second copy above the first
        self.bgX2       = 0
        self.moving_speed = SPEED

    def update(self):
        """Move both copies downward; loop back when off-screen."""
        self.bgY1 += self.moving_speed
        self.bgY2 += self.moving_speed

        # When a copy scrolls fully below the screen, reset it above
        if self.bgY1 >= self.rectBGimg.height:
            self.bgY1 = -self.rectBGimg.height
        if self.bgY2 >= self.rectBGimg.height:
            self.bgY2 = -self.rectBGimg.height

    def render(self):
        """Draw both background copies."""
        DISPLAYSURF.blit(self.bgimage, (self.bgX1, self.bgY1))
        DISPLAYSURF.blit(self.bgimage, (self.bgX2, self.bgY2))


# ════════════════════════════════════════════════════════════ #
#  Enemy Car                                                   #
# ════════════════════════════════════════════════════════════ #
class Enemy(pygame.sprite.Sprite):
    """Enemy car that spawns at the top and moves downward."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Enemy.png"))
        # Collision rect derived from image size
        self.rect  = self.image.get_rect()
        # Spawn at a random horizontal position at the top of the screen
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """Move enemy downward; respawn at top when it leaves the screen."""
        global SCORE
        self.rect.move_ip(0, SPEED)  # move in place (no new rect object)

        if self.rect.top > SCREEN_HEIGHT:
            # Passed the player without collision → increase score
            SCORE += 1
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


# ════════════════════════════════════════════════════════════ #
#  Player Car                                                  #
# ════════════════════════════════════════════════════════════ #
class Player(pygame.sprite.Sprite):
    """Player-controlled car at the bottom of the screen."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Player.png"))
        self.rect  = self.image.get_rect()
        # Start centered horizontally near the bottom
        self.rect.center = (160, 520)

    def move(self):
        """Read arrow-key input and move player, clamped to screen edges."""
        pressed_keys = pygame.key.get_pressed()

        # Move left — don't go past the left edge
        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)

        # Move right — don't go past the right edge
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)


# ════════════════════════════════════════════════════════════ #
#  Coin                                                        #
# ════════════════════════════════════════════════════════════ #
class Coin(pygame.sprite.Sprite):
    """A yellow coin that appears randomly on the road for the player to collect."""

    RADIUS = 12   # pixel radius of the drawn circle

    def __init__(self):
        super().__init__()
        # Create a transparent surface to hold the drawn circle
        size = self.RADIUS * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # Draw a yellow filled circle + dark outline
        pygame.draw.circle(self.image, YELLOW,   (self.RADIUS, self.RADIUS), self.RADIUS)
        pygame.draw.circle(self.image, (180, 140, 0), (self.RADIUS, self.RADIUS), self.RADIUS, 2)
        # Draw a small "$" symbol in the centre for style
        coin_font  = pygame.font.SysFont("Verdana", 12, bold=True)
        label      = coin_font.render("$", True, (120, 80, 0))
        self.image.blit(label, (self.RADIUS - label.get_width() // 2,
                                self.RADIUS - label.get_height() // 2))

        self.rect = self.image.get_rect()
        self._respawn()

    def _respawn(self):
        """Place coin at a new random position at the top of the screen."""
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """Coin falls at the same speed as the road; respawns when off-screen."""
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()


# ════════════════════════════════════════════════════════════ #
#  Sprite Groups                                               #
# ════════════════════════════════════════════════════════════ #
P1      = Player()
E1      = Enemy()
C1      = Coin()

# Groups for batch operations and collision detection
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, C1)

# ── Background & sounds ──────────────────────────────────────
background = Background()

# Load sound effects (gracefully skip if files are missing)
try:
    pygame.mixer.music.load(os.path.join(BASE_DIR, "bg_music.ogg"))
    pygame.mixer.music.play(-1)
    crash_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "crash.wav"))
    coin_sound  = pygame.mixer.Sound(os.path.join(BASE_DIR, "coin.wav"))
except Exception:
    crash_sound = None
    coin_sound  = None


# ════════════════════════════════════════════════════════════ #
#  Helper: draw HUD (score + coins)                            #
# ════════════════════════════════════════════════════════════ #
def draw_hud():
    """Render score on the left and coin count on the right."""
    # Score — top left
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    # Coin counter — top right (with a small yellow coin icon)
    coin_text  = font_small.render(f"Coins: {COINS}", True, (140, 100, 0))
    cx         = SCREEN_WIDTH - coin_text.get_width() - 15
    pygame.draw.circle(DISPLAYSURF, YELLOW,      (cx - 14, 20), 10)
    pygame.draw.circle(DISPLAYSURF, (180,140,0), (cx - 14, 20), 10, 2)
    DISPLAYSURF.blit(coin_text, (cx, 10))


# ════════════════════════════════════════════════════════════ #
#  Main Game Loop                                              #
# ════════════════════════════════════════════════════════════ #
while True:

    # ── Event handling ───────────────────────────────────────
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # ── Draw scrolling background first (bottom layer) ───────
    background.update()
    background.render()

    # ── Update & draw all sprites ────────────────────────────
    for sprite in all_sprites:
        DISPLAYSURF.blit(sprite.image, sprite.rect)

    P1.move()     # player reacts to keyboard input
    E1.move()     # enemy moves downward

    # Move every coin; new coins can be spawned via the group
    for coin in coins:
        coin.move()

    # ── Coin collection detection ────────────────────────────
    # spritecollide returns a list of coins that overlap the player rect
    collected = pygame.sprite.spritecollide(P1, coins, False)
    for coin in collected:
        COINS += 1                    # increment counter
        if coin_sound:
            coin_sound.play()
        coin._respawn()               # send coin back to top

    # Randomly spawn an extra coin (1-in-300 chance each frame ≈ every ~5 s)
    if random.randint(1, 300) == 1:
        new_coin = Coin()
        coins.add(new_coin)
        all_sprites.add(new_coin)

    # ── Collision: player vs enemy ───────────────────────────
    if pygame.sprite.spritecollideany(P1, enemies):
        if crash_sound:
            crash_sound.play()
        time.sleep(0.5)

        # Show "Game Over" screen
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # ── Speed increases every 5 points ───────────────────────
    if SCORE > 0 and SCORE % 5 == 0:
        SPEED = 5 + SCORE // 5   # gradually get faster

    # ── Draw HUD on top of everything ────────────────────────
    draw_hud()

    # ── Refresh display & tick clock ────────────────────────
    pygame.display.update()
    FramePerSec.tick(FPS)