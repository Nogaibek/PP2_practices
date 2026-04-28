import pygame
import sys
import os
from datetime import datetime

from tools import (
    draw_shape, flood_fill,
    POLYGON_TOOLS, get_polygon,
)

pygame.init()

# ── Window ────────────────────────────────────────────────────
SCREEN_W  = 1100
SCREEN_H  = 720
TOOLBAR_H = 80          # two rows of buttons

# ── Color palette ─────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (210, 210, 210)
DARK_GRAY  = (90,  90,  90)
LIGHT_GRAY = (235, 235, 235)
ACCENT     = (60,  120, 230)   # highlight color for active tool

PALETTE = [
    (0,   0,   0),    (255,255,255),
    (210, 30,  30),   (30,  180, 60),
    (30,  60,  220),  (255, 140, 0),
    (255, 220, 0),    (150, 0,   200),
    (0,   200, 210),  (170, 90,  30),
    (255, 140, 170),  (110, 110, 110),
]

# ── Brush sizes (pixels) ──────────────────────────────────────
SIZES = [2, 5, 10]      # small / medium / large

# ── Display ───────────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()

# Canvas lives below the toolbar
canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
canvas.fill(WHITE)

# ── Fonts ─────────────────────────────────────────────────────
font_btn  = pygame.font.SysFont("Courier New", 11, bold=True)
font_tiny = pygame.font.SysFont("Courier New", 10)
font_text = pygame.font.SysFont("Arial", 20)          # used for text tool

def load_cursor(name, size=(40, 32)):
    img = pygame.image.load(f"defense/TSIS2/assets/{name}").convert_alpha()
    return pygame.transform.smoothscale(img, size)

cursor_images = {
    "pencil": load_cursor("pen.png"),
}

cursor_offsets = {
    "pencil": (2, 28),
}

# ════════════════════════════════════════════════════════════ #
#  ToolButton                                                  #
# ════════════════════════════════════════════════════════════ #
class ToolButton:
    """A single labelled clickable button in the toolbar."""

    def __init__(self, x, y, w, h, label, name):
        self.rect  = pygame.Rect(x, y, w, h)
        self.label = label
        self.name  = name

    def draw(self, surf, active):
        bg = ACCENT     if active else LIGHT_GRAY
        fg = WHITE      if active else DARK_GRAY
        pygame.draw.rect(surf, bg,        self.rect, border_radius=5)
        pygame.draw.rect(surf, DARK_GRAY, self.rect, 1, border_radius=5)
        t = font_btn.render(self.label, True, fg)
        surf.blit(t, (self.rect.centerx - t.get_width()  // 2,
                      self.rect.centery - t.get_height() // 2))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


# ════════════════════════════════════════════════════════════ #
#  Build toolbar                                               #
# ════════════════════════════════════════════════════════════ #
BW, BH, GAP = 62, 24, 3

def _row(items, y):
    btns = []
    x = 6
    for lbl, nm in items:
        btns.append(ToolButton(x, y, BW, BH, lbl, nm))
        x += BW + GAP
    return btns

# Row 1: drawing tools
ROW1 = _row([
    ("Pencil",  "pencil"),
    ("Line",    "line"),
    ("Rect",    "rect"),
    ("Circle",  "circle"),
    ("Eraser",  "eraser"),
    ("Fill",    "fill"),
    ("Text",    "text"),
    ("Clear",   "clear"),
], y=4)

# Row 2: shape tools (Practice 10-11)
ROW2 = _row([
    ("Square",  "square"),
    ("R.Tri",   "rtriangle"),
    ("Eq.Tri",  "etriangle"),
    ("Rhombus", "rhombus"),
], y=32)

ALL_BTNS = ROW1 + ROW2

# ── Size buttons (3 levels) ───────────────────────────────────
# Displayed as small filled squares of increasing size
SIZE_RECTS = []
sx = 570
for s in SIZES:
    SIZE_RECTS.append((pygame.Rect(sx, 20, 30, 30), s))
    sx += 36

# ── Palette swatches ──────────────────────────────────────────
SW = 24
SWATCHES = []
sw_x = 690
for i, col in enumerate(PALETTE):
    SWATCHES.append((pygame.Rect(sw_x + i*(SW+3), (TOOLBAR_H-SW)//2, SW, SW), col))


# ════════════════════════════════════════════════════════════ #
#  Toolbar renderer                                            #
# ════════════════════════════════════════════════════════════ #
def draw_toolbar(cur_tool, cur_color, cur_size):
    """Render the full toolbar onto `screen`."""
    pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_W, TOOLBAR_H))
    pygame.draw.line(screen, DARK_GRAY, (0, TOOLBAR_H-1), (SCREEN_W, TOOLBAR_H-1), 2)

    # Tool buttons
    for btn in ALL_BTNS:
        btn.draw(screen, btn.name == cur_tool)

    # Size buttons
    for rect, s in SIZE_RECTS:
        active = (s == cur_size)
        bg = ACCENT if active else LIGHT_GRAY
        pygame.draw.rect(screen, bg, rect, border_radius=4)
        pygame.draw.rect(screen, DARK_GRAY, rect, 1, border_radius=4)
        r = min(s // 2 + 1, 10)
        pygame.draw.circle(screen, WHITE if active else DARK_GRAY, rect.center, r)
        lbl = font_tiny.render(f"{s}px", True, WHITE if active else DARK_GRAY)
        screen.blit(lbl, (rect.x + 1, rect.bottom - 11))

    # Color swatches
    for rect, col in SWATCHES:
        pygame.draw.rect(screen, col, rect)
        border = WHITE if col == cur_color else DARK_GRAY
        pygame.draw.rect(screen, border, rect, 2)

    # Active color preview
    prev = pygame.Rect(SCREEN_W - 52, 8, 44, TOOLBAR_H - 16)
    pygame.draw.rect(screen, cur_color, prev)
    pygame.draw.rect(screen, DARK_GRAY, prev, 2)
    lbl = font_tiny.render("color", True, DARK_GRAY)
    screen.blit(lbl, (SCREEN_W - 50, TOOLBAR_H - 13))

    # Keyboard hint strip
    hints = font_tiny.render(
        "1/2/3=size  Ctrl+S=save  [T]=text  [F]=fill  [E]=eraser  Del=clear", True, DARK_GRAY)
    screen.blit(hints, (6, TOOLBAR_H - 13))


# ════════════════════════════════════════════════════════════ #
#  Coordinate helpers                                          #
# ════════════════════════════════════════════════════════════ #
def to_canvas(sp):
    """Screen → canvas coordinates (strip toolbar offset)."""
    return (sp[0], sp[1] - TOOLBAR_H)

def on_canvas(sp):
    """Return True if screen position is inside the drawable canvas."""
    return sp[1] >= TOOLBAR_H


# ════════════════════════════════════════════════════════════ #
#  Save canvas                                                 #
# ════════════════════════════════════════════════════════════ #
def save_canvas():
    """
    Save the canvas surface as a PNG file.
    Filename includes a timestamp so saves never overwrite each other.
    Uses pygame.image.save — no extra libraries needed.
    """
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    # Save to the same directory as paint.py
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    pygame.image.save(canvas, path)
    return filename   # returned so we can show a flash message


# ════════════════════════════════════════════════════════════ #
#  Application state                                           #
# ════════════════════════════════════════════════════════════ #
cur_tool  = "pencil"    # active tool name
cur_color = BLACK       # active drawing color
cur_size  = 5           # active brush size (px)

drawing    = False      # True while left mouse button held
drag_start = None       # canvas-space start of current drag
last_pos   = None       # previous frame canvas-space mouse position

# Text tool state
text_active   = False   # True when text cursor is placed
text_pos      = None    # (x, y) on canvas where text starts
text_buffer   = ""      # characters typed so far

# Status message (e.g. "Saved canvas_…png")
status_msg    = ""
status_timer  = 0       # seconds remaining to show the message

# Tools that render a live preview during drag
PREVIEW_TOOLS = {"line", "rect", "circle"} | POLYGON_TOOLS


def draw_cursor():
    tool = cur_tool if cur_tool in cursor_images else "default"

    img = cursor_images.get(tool)
    if img is None:
        return  # ничего не рисуем, но и не падаем

    mx, my = pygame.mouse.get_pos()
    ox, oy = cursor_offsets.get(tool, (0, 0))

    screen.blit(img, (mx - ox, my - oy))

# ════════════════════════════════════════════════════════════ #
#  Main loop                                                   #
# ════════════════════════════════════════════════════════════ #
while True:
    dt         = clock.tick(60) / 1000.0
    mouse_pos  = pygame.mouse.get_pos()
    canvas_pos = to_canvas(mouse_pos)

    # ── Events ───────────────────────────────────────────────
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ── KEYDOWN ──────────────────────────────────────────
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()

            # ── Text tool input (highest priority) ───────────
            if text_active:
                if event.key == pygame.K_RETURN:
                    # Commit text permanently to canvas
                    if text_buffer:
                        rendered = font_text.render(text_buffer, True, cur_color)
                        canvas.blit(rendered, text_pos)
                    text_active  = False
                    text_buffer  = ""
                    text_pos     = None

                elif event.key == pygame.K_ESCAPE:
                    # Cancel without drawing
                    text_active  = False
                    text_buffer  = ""
                    text_pos     = None

                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]

                else:
                    # Append printable characters to buffer
                    if event.unicode and event.unicode.isprintable():
                        text_buffer += event.unicode

            else:
                # ── Global shortcuts ──────────────────────────
                if mods & pygame.KMOD_CTRL and event.key == pygame.K_s:
                    # Ctrl+S — save canvas as timestamped PNG
                    fname = save_canvas()
                    status_msg   = f"Saved: {fname}"
                    status_timer = 3.0

                elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    canvas.fill(WHITE)

                # Brush size: keys 1, 2, 3
                elif event.key == pygame.K_1:  cur_size = SIZES[0]
                elif event.key == pygame.K_2:  cur_size = SIZES[1]
                elif event.key == pygame.K_3:  cur_size = SIZES[2]

                # Tool shortcuts
                elif event.key == pygame.K_p:  cur_tool = "pencil"
                elif event.key == pygame.K_l:  cur_tool = "line"
                elif event.key == pygame.K_r:  cur_tool = "rect"
                elif event.key == pygame.K_c:  cur_tool = "circle"
                elif event.key == pygame.K_e:  cur_tool = "eraser"
                elif event.key == pygame.K_f:  cur_tool = "fill"
                elif event.key == pygame.K_t:  cur_tool = "text"
                elif event.key == pygame.K_s:  cur_tool = "square"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ── MOUSE BUTTON DOWN ─────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if not on_canvas(mouse_pos):
                # ── Toolbar clicks ────────────────────────────
                for btn in ALL_BTNS:
                    if btn.hit(mouse_pos):
                        if btn.name == "clear":
                            canvas.fill(WHITE)
                        else:
                            cur_tool = btn.name
                            # Switching tool cancels active text entry
                            if text_active:
                                text_active = False
                                text_buffer = ""

                for rect, sz in SIZE_RECTS:
                    if rect.collidepoint(mouse_pos):
                        cur_size = sz

                for rect, col in SWATCHES:
                    if rect.collidepoint(mouse_pos):
                        cur_color = col
                        if cur_tool == "eraser":
                            cur_tool = "pencil"

            else:
                # ── Canvas clicks ─────────────────────────────

                if cur_tool == "fill":
                    # Flood-fill immediately on click — no drag needed
                    flood_fill(canvas, canvas_pos, cur_color)

                elif cur_tool == "text":
                    # Place text cursor at click position
                    text_active = True
                    text_pos    = canvas_pos
                    text_buffer = ""

                else:
                    # Begin drag for pencil / line / shapes / eraser
                    drawing    = True
                    drag_start = canvas_pos
                    last_pos   = canvas_pos

                    # Pencil and eraser start painting on press
                    if cur_tool == "pencil":
                        pygame.draw.circle(canvas, cur_color, canvas_pos, cur_size)
                    elif cur_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, canvas_pos, cur_size * 3)

        # ── MOUSE MOTION ──────────────────────────────────────
        if event.type == pygame.MOUSEMOTION:
            if drawing and on_canvas(mouse_pos):

                if cur_tool == "pencil":
                    # Connect consecutive positions for smooth freehand stroke
                    if last_pos:
                        pygame.draw.line(canvas, cur_color,
                                         last_pos, canvas_pos, cur_size * 2)
                    pygame.draw.circle(canvas, cur_color, canvas_pos, cur_size)
                    last_pos = canvas_pos

                elif cur_tool == "eraser":
                    esz = cur_size * 3
                    if last_pos:
                        pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, esz * 2)
                    pygame.draw.circle(canvas, WHITE, canvas_pos, esz)
                    last_pos = canvas_pos

                # Shape/line tools: preview is rendered each frame from canvas copy

        # ── MOUSE BUTTON UP ───────────────────────────────────
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and drag_start:
                # Commit shape to canvas
                draw_shape(canvas, cur_tool, drag_start,
                           canvas_pos, cur_color, cur_size)

            drawing    = False
            drag_start = None
            last_pos   = None

    # ── Status timer countdown ────────────────────────────────
    if status_timer > 0:
        status_timer = max(0, status_timer - dt)

    # ════════════════════════════════════════════════════════ #
    #  Render                                                  #
    # ════════════════════════════════════════════════════════ #
    screen.fill(WHITE)

    # 1. Canvas (base layer)
    screen.blit(canvas, (0, TOOLBAR_H))

    # 2. Live shape preview while dragging (line / rect / circle / polygon tools)
    #    We blit a copy so the canvas pixel data is never dirtied mid-drag.
    if drawing and drag_start and cur_tool in PREVIEW_TOOLS:
        preview = canvas.copy()
        draw_shape(preview, cur_tool, drag_start, canvas_pos, cur_color, cur_size)
        screen.blit(preview, (0, TOOLBAR_H))

    # 3. Eraser cursor: circle outline follows mouse
    if cur_tool == "eraser":
        pygame.draw.circle(screen, DARK_GRAY, mouse_pos, cur_size * 3, 2)

    # 4. Text tool: render live preview of typed text + blinking cursor
    if text_active and text_pos:
        # Convert canvas coords back to screen coords
        sx = text_pos[0]
        sy = text_pos[1] + TOOLBAR_H
        preview_surf = font_text.render(text_buffer + "|", True, cur_color)
        # Semi-transparent background so text is readable over any color
        bg = pygame.Surface((preview_surf.get_width() + 4,
                              preview_surf.get_height() + 2), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 160))
        screen.blit(bg, (sx - 2, sy - 1))
        screen.blit(preview_surf, (sx, sy))

    # 5. Toolbar (always on top)
    draw_toolbar(cur_tool, cur_color, cur_size)

    # 6. Status flash message (e.g. after Ctrl+S)
    if status_timer > 0:
        alpha    = min(255, int(255 * min(status_timer, 1.0)))
        msg_surf = font_btn.render(status_msg, True, (0, 160, 60))
        screen.blit(msg_surf, (SCREEN_W // 2 - msg_surf.get_width() // 2,
                               TOOLBAR_H + 10))
    
    draw_cursor()
    pygame.display.flip()