import pygame
import sys
import os
import math
import time
from player import MusicPlayer

# ── Window ────────────────────────────────────────────────────────────────── #
WIDTH, HEIGHT = 520, 420
FPS = 30

# ── Palette  (dark retro-cassette theme) ─────────────────────────────────── #
BG         = (10,  10,  16)
PANEL      = (20,  20,  32)
ACCENT     = (255, 80,  80)   # red-orange glow
ACCENT2    = (255, 180, 60)   # amber
WHITE      = (230, 230, 230)
GRAY       = (100, 100, 120)
DARK_GRAY  = (40,  40,  56)
GREEN      = (80,  220, 120)


# ── Helpers ──────────────────────────────────────────────────────────────── #
def fmt_time(seconds):
    s = int(seconds)
    return f"{s // 60:02d}:{s % 60:02d}"


def draw_rounded_rect(surf, color, rect, radius, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_glow_circle(surf, color, center, radius, alpha=60):
    glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    for r in range(radius * 2, 0, -1):
        a = int(alpha * (1 - r / (radius * 2)))
        pygame.draw.circle(glow, (*color[:3], a), (radius * 2, radius * 2), r)
    surf.blit(glow, (center[0] - radius * 2, center[1] - radius * 2))


# ── VU Meter bars ─────────────────────────────────────────────────────────── #
class VUMeter:
    def __init__(self, x, y, w, h, bars=12):
        self.rect = pygame.Rect(x, y, w, h)
        self.bars = bars
        self.levels = [0.0] * bars
        self.targets = [0.0] * bars

    def update(self, active):
        t = time.time()
        for i in range(self.bars):
            if active:
                self.targets[i] = 0.2 + 0.8 * abs(math.sin(t * (1.5 + i * 0.4) + i))
            else:
                self.targets[i] = 0.0
            self.levels[i] += (self.targets[i] - self.levels[i]) * 0.18

    def draw(self, surf):
        bw = self.rect.width // self.bars
        gap = 3
        for i, lvl in enumerate(self.levels):
            bh = int(self.rect.height * lvl)
            x = self.rect.x + i * bw + gap // 2
            y = self.rect.bottom - bh
            # gradient color: green → amber → red
            ratio = lvl
            if ratio < 0.6:
                r = int(80  + (255 - 80)  * ratio / 0.6)
                g = int(220 - (220 - 180) * ratio / 0.6)
                b = 60
            else:
                r = 255
                g = int(180 - 180 * (ratio - 0.6) / 0.4)
                b = 40
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.rect(surf, color,
                             pygame.Rect(x, y, bw - gap, bh), border_radius=2)
            # dead bar background
            pygame.draw.rect(surf, DARK_GRAY,
                             pygame.Rect(x, self.rect.y, bw - gap,
                                         self.rect.height - bh), border_radius=2)


# ── Spinning record ───────────────────────────────────────────────────────── #
class SpinningRecord:
    def __init__(self, cx, cy, radius=62):
        self.cx, self.cy = cx, cy
        self.radius = radius
        self.angle = 0.0

    def update(self, active):
        if active:
            self.angle = (self.angle + 2.5) % 360

    def draw(self, surf):
        r = self.radius
        cx, cy = self.cx, self.cy
        # Outer disc
        pygame.draw.circle(surf, (25, 22, 35), (cx, cy), r)
        pygame.draw.circle(surf, ACCENT, (cx, cy), r, 2)
        # Grooves
        for gr in range(r - 8, r // 2, -8):
            pygame.draw.circle(surf, (45, 40, 60), (cx, cy), gr, 1)
        # Spinning arm indicator
        rad = math.radians(self.angle)
        ex = int(cx + (r - 6) * math.cos(rad))
        ey = int(cy + (r - 6) * math.sin(rad))
        pygame.draw.line(surf, ACCENT2, (cx, cy), (ex, ey), 2)
        # Center label
        pygame.draw.circle(surf, ACCENT, (cx, cy), 14)
        pygame.draw.circle(surf, BG,    (cx, cy), 7)
        pygame.draw.circle(surf, WHITE, (cx, cy), 3)


# ── Main ─────────────────────────────────────────────────────────────────── #
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎵 Mickey's Music Player")
    clock = pygame.time.Clock()

    music_dir = os.path.join(os.path.dirname(__file__), "music")
    player = MusicPlayer(music_dir)

    vu   = VUMeter(30, 260, WIDTH - 60, 80)
    rec  = SpinningRecord(WIDTH // 2, 130, radius=68)

    # Fonts — fallback chain to monospace for retro feel
    def load_font(size, bold=False):
        for name in ["Courier New", "Courier", "monospace"]:
            try:
                return pygame.font.SysFont(name, size, bold=bold)
            except Exception:
                pass
        return pygame.font.Font(None, size)

    font_big   = load_font(22, bold=True)
    font_med   = load_font(16)
    font_small = load_font(13)

    # Status message (shown briefly on key press)
    status_msg   = ""
    status_timer = 0

    def set_status(msg):
        nonlocal status_msg, status_timer
        status_msg   = msg
        status_timer = 2.0   # seconds

    # ── event loop ──────────────────────────────────────────────────────── #
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                key = event.key

                if key == pygame.K_p:
                    if not player.is_playing:
                        player.play()
                        set_status("▶  PLAY")

                elif key == pygame.K_s:
                    player.stop()
                    set_status("■  STOP")

                elif key == pygame.K_n:
                    player.next_track()
                    set_status("⏭  NEXT")

                elif key == pygame.K_b:
                    player.prev_track()
                    set_status("⏮  BACK")

                elif key == pygame.K_q or key == pygame.K_ESCAPE:
                    running = False

        player.update()
        vu.update(player.is_playing)
        rec.update(player.is_playing)

        if status_timer > 0:
            status_timer -= dt

        # ── Drawing ─────────────────────────────────────────────────────── #
        screen.fill(BG)

        # Top panel background
        draw_rounded_rect(screen, PANEL, pygame.Rect(20, 10, WIDTH - 40, HEIGHT - 20), 14,
                          border=1, border_color=(60, 60, 80))

        # ── Record ── #
        if player.is_playing:
            draw_glow_circle(screen, ACCENT, (WIDTH // 2, 130), 80, alpha=35)
        rec.draw(screen)

        # ── Track info ── #
        track_name = player.get_track_name()
        idx, total = player.get_playlist_info()

        # Scrolling track name if too long
        max_chars = 34
        if len(track_name) > max_chars:
            t       = time.time()
            offset  = int((t * 30) % (len(track_name) * 12))
            display = track_name + "    " + track_name
        else:
            display = track_name

        name_surf = font_big.render(display[:max_chars], True, WHITE)
        screen.blit(name_surf, (WIDTH // 2 - name_surf.get_width() // 2, 214))

        # Track counter
        counter = f"Track  {idx} / {total}"
        cs = font_med.render(counter, True, GRAY)
        screen.blit(cs, (WIDTH // 2 - cs.get_width() // 2, 240))

        # ── VU Meter ── #
        vu.draw(screen)

        # ── Progress bar ── #
        elapsed = player.get_elapsed()
        bar_x, bar_y, bar_w, bar_h = 30, 358, WIDTH - 60, 8
        draw_rounded_rect(screen, DARK_GRAY, pygame.Rect(bar_x, bar_y, bar_w, bar_h), 4)
        fill = min(1.0, elapsed / 180.0)   # assume ≤3 min track
        if fill > 0:
            draw_rounded_rect(screen, ACCENT,
                              pygame.Rect(bar_x, bar_y, int(bar_w * fill), bar_h), 4)

        # Elapsed time
        ts = font_small.render(fmt_time(elapsed), True, ACCENT2)
        screen.blit(ts, (bar_x, bar_y + 12))

        # ── Status flash ── #
        if status_timer > 0:
            alpha = min(255, int(255 * status_timer / 0.6))
            color = (*ACCENT[:3],) if status_timer < 0.6 else ACCENT2
            ss = font_big.render(status_msg, True, color)
            screen.blit(ss, (WIDTH // 2 - ss.get_width() // 2, 380))

        # ── State indicator dot ── #
        dot_color = GREEN if player.is_playing else GRAY
        pygame.draw.circle(screen, dot_color, (WIDTH - 40, 28), 7)
        pygame.draw.circle(screen, BG, (WIDTH - 40, 28), 4 if player.is_playing else 0)

        # ── Key hint bar ── #
        hints = "[P] Play  [S] Stop  [N] Next  [B] Back  [Q] Quit"
        hs = font_small.render(hints, True, (70, 70, 90))
        screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, HEIGHT - 26))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()