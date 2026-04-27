# ============================================================
# Paint — extended from Practice 8
# New tools added:
#   1. Square          — drag to define side length
#   2. Right Triangle  — right angle at drag start corner
#   3. Equilateral Triangle — drag sets base width; apex auto-calculated
#   4. Rhombus         — drag defines bounding box; diagonals connect midpoints
# All existing tools (Brush, Line, Rect, Circle, Eraser, Color) kept intact.
# ============================================================

import pygame
import sys
import math

pygame.init()

# ── Window ────────────────────────────────────────────────────
SCREEN_W  = 1000          # wider to fit more toolbar buttons
SCREEN_H  = 680
TOOLBAR_H = 70            # top bar height in pixels

# ── UI Colors ─────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (200, 200, 200)
DARK_GRAY  = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)

# ── Drawing palette ───────────────────────────────────────────
PALETTE = [
    (0,   0,   0),    # black
    (255, 255, 255),  # white
    (200, 0,   0),    # red
    (0,   180, 0),    # green
    (0,   0,   220),  # blue
    (255, 165, 0),    # orange
    (255, 220, 0),    # yellow
    (160, 0,   200),  # purple
    (0,   200, 200),  # cyan
    (180, 100, 40),   # brown
    (255, 150, 180),  # pink
    (100, 100, 100),  # dark gray
]

# ── Display & canvas ──────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()

# Canvas: a separate surface below the toolbar.
# All drawing is committed here permanently on mouse-up.
canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
canvas.fill(WHITE)

# ── Fonts ─────────────────────────────────────────────────────
font      = pygame.font.SysFont("Courier New", 12, bold=True)
font_tiny = pygame.font.SysFont("Courier New", 11)


# ════════════════════════════════════════════════════════════ #
#  ToolButton — a single clickable button in the toolbar       #
# ════════════════════════════════════════════════════════════ #
class ToolButton:
    """Renders a labelled rectangular button; highlights when active."""

    def __init__(self, x, y, w, h, label, tool_name):
        self.rect      = pygame.Rect(x, y, w, h)
        self.label     = label
        self.tool_name = tool_name

    def draw(self, surf, active):
        """Draw the button; active tool gets a dark background."""
        bg    = DARK_GRAY if active else LIGHT_GRAY
        fg    = WHITE     if active else BLACK
        pygame.draw.rect(surf, bg,        self.rect, border_radius=5)
        pygame.draw.rect(surf, DARK_GRAY, self.rect, 2, border_radius=5)
        txt = font.render(self.label, True, fg)
        surf.blit(txt, (self.rect.centerx - txt.get_width()  // 2,
                        self.rect.centery - txt.get_height() // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ════════════════════════════════════════════════════════════ #
#  Toolbar layout                                              #
# ════════════════════════════════════════════════════════════ #
# Two rows of tools fit neatly in the toolbar area.
# Row 1: original tools  |  Row 2: new shape tools
BTN_W, BTN_H = 66, 26
GAP          = 4

def make_row(tools_list, y):
    """Create a list of ToolButtons laid out horizontally starting at x=6."""
    buttons = []
    x = 6
    for label, name in tools_list:
        buttons.append(ToolButton(x, y, BTN_W, BTN_H, label, name))
        x += BTN_W + GAP
    return buttons

ROW1 = make_row([
    ("Brush",   "brush"),
    ("Line",    "line"),
    ("Rect",    "rect"),
    ("Circle",  "circle"),
    ("Eraser",  "eraser"),
    ("Clear",   "clear"),
], y=4)

ROW2 = make_row([
    ("Square",   "square"),
    ("R.Tri",    "rtriangle"),   # right triangle
    ("Eq.Tri",   "etriangle"),   # equilateral triangle
    ("Rhombus",  "rhombus"),
], y=36)

ALL_BUTTONS = ROW1 + ROW2

# ── Palette swatches ──────────────────────────────────────────
SWATCH_SZ    = 26
SWATCH_START = 530    # x offset where swatches begin
SWATCHES = [
    (pygame.Rect(SWATCH_START + i * (SWATCH_SZ + 3),
                 (TOOLBAR_H - SWATCH_SZ) // 2,
                 SWATCH_SZ, SWATCH_SZ), color)
    for i, color in enumerate(PALETTE)
]

# ── Brush size buttons ────────────────────────────────────────
SIZE_BTNS = []
for i, sz in enumerate([2, 5, 10, 18]):
    r = pygame.Rect(SWATCH_START - 115 + i * 27, 22, 24, 24)
    SIZE_BTNS.append((r, sz))


# ════════════════════════════════════════════════════════════ #
#  Shape geometry helpers                                      #
# ════════════════════════════════════════════════════════════ #

def square_points(start, end):
    """
    Return the four corners of a square whose one corner is `start`.
    The side length is the larger of |dx| or |dy|, preserving the sign
    of the drag direction so the square always follows the cursor.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    # Use the larger axis as the side, keep direction sign for each axis
    side = max(abs(dx), abs(dy))
    sx   = side if dx >= 0 else -side
    sy   = side if dy >= 0 else -side
    x0, y0 = start
    return [(x0,      y0),
            (x0 + sx, y0),
            (x0 + sx, y0 + sy),
            (x0,      y0 + sy)]


def right_triangle_points(start, end):
    """
    Return three corners of a right triangle.
    The right angle is placed at `start` (top-left of the bounding box).
    The other two corners are at the bottom-left and bottom-right of the
    drag rectangle, giving legs along the X and Y axes.

        start ─────── (end_x, start_y)
          │              ╱
          │            ╱
        (start_x, end_y)
    """
    x0, y0 = start
    x1, y1 = end
    return [(x0, y0),   # right-angle corner
            (x0, y1),   # bottom-left (vertical leg endpoint)
            (x1, y1)]   # bottom-right (hypotenuse endpoint)


def equilateral_triangle_points(start, end):
    """
    Return three corners of an equilateral triangle.
    The base runs horizontally between start and (end_x, start_y).
    The apex is above (or below, depending on drag) the base midpoint
    at height = (√3/2) × base_width.
    """
    x0, y0 = start
    x1, y1 = end
    base_w  = x1 - x0                          # signed width of the base
    mid_x   = (x0 + x1) / 2
    # Height of equilateral triangle: h = (√3/2) × |base|
    h = abs(base_w) * math.sqrt(3) / 2
    # If the user dragged downward, apex goes up; otherwise down
    apex_y  = y0 - h if y1 <= y0 else y0 + h
    return [(x0,        y0),
            (x1,        y0),
            (int(mid_x), int(apex_y))]


def rhombus_points(start, end):
    """
    Return four corners of a rhombus inscribed in the drag bounding box.
    The four points are the midpoints of the bounding box's four sides:
      top-mid, right-mid, bottom-mid, left-mid.
    """
    x0, y0 = start
    x1, y1 = end
    mid_x = (x0 + x1) // 2
    mid_y = (y0 + y1) // 2
    return [(mid_x, y0),   # top
            (x1,    mid_y),  # right
            (mid_x, y1),   # bottom
            (x0,    mid_y)]  # left


# ════════════════════════════════════════════════════════════ #
#  Unified shape drawing (used for both preview and commit)    #
# ════════════════════════════════════════════════════════════ #
# Tools that need polygon drawing (all new shapes + rect/circle kept separate)
POLYGON_TOOLS = {"square", "rtriangle", "etriangle", "rhombus"}

def get_polygon(tool, start, end):
    """
    Return the list of (x, y) vertices for the given tool and drag coords.
    Returns None for non-polygon tools.
    """
    if tool == "square":
        return square_points(start, end)
    elif tool == "rtriangle":
        return right_triangle_points(start, end)
    elif tool == "etriangle":
        return equilateral_triangle_points(start, end)
    elif tool == "rhombus":
        return rhombus_points(start, end)
    return None


def draw_shape(surf, tool, start, end, color, stroke):
    """
    Draw the finished shape for `tool` onto `surf`.
    Handles all tools: brush/eraser are handled elsewhere (live),
    polygon tools use pygame.draw.polygon with an outline stroke.
    """
    if tool == "line":
        pygame.draw.line(surf, color, start, end, stroke)

    elif tool == "rect":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(surf, color, (x, y, w, h), stroke)

    elif tool == "circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(abs(end[0] - start[0]) // 2,
                 abs(end[1] - start[1]) // 2, 1)
        pygame.draw.circle(surf, color, (cx, cy), r, stroke)

    elif tool in POLYGON_TOOLS:
        pts = get_polygon(tool, start, end)
        if pts:
            pygame.draw.polygon(surf, color, pts, stroke)


# ════════════════════════════════════════════════════════════ #
#  Toolbar renderer                                            #
# ════════════════════════════════════════════════════════════ #
def draw_toolbar(surf, current_tool, current_color, current_size):
    """Render the full toolbar: background, all buttons, sizes, palette."""
    # Background + bottom separator line
    pygame.draw.rect(surf, GRAY, (0, 0, SCREEN_W, TOOLBAR_H))
    pygame.draw.line(surf, DARK_GRAY, (0, TOOLBAR_H - 1), (SCREEN_W, TOOLBAR_H - 1), 2)

    # All tool buttons (two rows)
    for btn in ALL_BUTTONS:
        btn.draw(surf, btn.tool_name == current_tool)

    # Size selector buttons — drawn as filled circles of increasing radius
    for rect, sz in SIZE_BTNS:
        active = (sz == current_size)
        bg     = DARK_GRAY if active else LIGHT_GRAY
        pygame.draw.rect(surf, bg,        rect, border_radius=4)
        pygame.draw.rect(surf, DARK_GRAY, rect, 1, border_radius=4)
        r = min(sz // 2, 8)
        pygame.draw.circle(surf, BLACK if active else DARK_GRAY, rect.center, r)

    # Color swatches
    for rect, color in SWATCHES:
        pygame.draw.rect(surf, color, rect)
        border = WHITE if color == current_color else DARK_GRAY
        pygame.draw.rect(surf, border, rect, 2)

    # Current-color preview box (far right)
    prev = pygame.Rect(SCREEN_W - 48, 8, 40, TOOLBAR_H - 16)
    pygame.draw.rect(surf, current_color, prev)
    pygame.draw.rect(surf, DARK_GRAY,     prev, 2)
    lbl = font_tiny.render("color", True, DARK_GRAY)
    surf.blit(lbl, (SCREEN_W - 46, TOOLBAR_H - 14))


# ════════════════════════════════════════════════════════════ #
#  Coordinate helpers                                          #
# ════════════════════════════════════════════════════════════ #
def to_canvas(screen_pos):
    """Convert a screen position to canvas coordinates (subtract toolbar)."""
    return (screen_pos[0], screen_pos[1] - TOOLBAR_H)


def on_canvas(screen_pos):
    """Return True if the screen position is inside the drawable canvas."""
    return screen_pos[1] >= TOOLBAR_H


# ════════════════════════════════════════════════════════════ #
#  Application state                                           #
# ════════════════════════════════════════════════════════════ #
current_tool  = "brush"   # name of the active tool
current_color = BLACK     # active drawing color
brush_size    = 5         # stroke width / brush radius

drawing    = False        # True while left mouse button is held
drag_start = None         # canvas-space position where the drag began
last_pos   = None         # canvas-space position from the previous frame

# All tools that show a live drag preview (not brush/eraser)
PREVIEW_TOOLS = {"line", "rect", "circle"} | POLYGON_TOOLS


# ════════════════════════════════════════════════════════════ #
#  Main loop                                                   #
# ════════════════════════════════════════════════════════════ #
while True:
    clock.tick(60)

    mouse_pos  = pygame.mouse.get_pos()
    canvas_pos = to_canvas(mouse_pos)

    # ── Event processing ─────────────────────────────────────
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ── Keyboard shortcuts ────────────────────────────────
        if event.type == pygame.KEYDOWN:
            if   event.key == pygame.K_ESCAPE:  pygame.quit(); sys.exit()
            elif event.key == pygame.K_b:        current_tool = "brush"
            elif event.key == pygame.K_l:        current_tool = "line"
            elif event.key == pygame.K_r:        current_tool = "rect"
            elif event.key == pygame.K_c:        current_tool = "circle"
            elif event.key == pygame.K_e:        current_tool = "eraser"
            elif event.key == pygame.K_s:        current_tool = "square"
            elif event.key == pygame.K_t:        current_tool = "rtriangle"
            elif event.key == pygame.K_y:        current_tool = "etriangle"
            elif event.key == pygame.K_h:        current_tool = "rhombus"
            elif event.key == pygame.K_DELETE:   canvas.fill(WHITE)

        # ── Mouse button DOWN ─────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if not on_canvas(mouse_pos):
                # ── Toolbar click ─────────────────────────────
                for btn in ALL_BUTTONS:
                    if btn.is_clicked(mouse_pos):
                        if btn.tool_name == "clear":
                            canvas.fill(WHITE)
                        else:
                            current_tool = btn.tool_name

                for rect, sz in SIZE_BTNS:
                    if rect.collidepoint(mouse_pos):
                        brush_size = sz

                for rect, color in SWATCHES:
                    if rect.collidepoint(mouse_pos):
                        current_color = color
                        if current_tool == "eraser":
                            current_tool = "brush"
            else:
                # ── Start drawing ─────────────────────────────
                drawing    = True
                drag_start = canvas_pos
                last_pos   = canvas_pos

                # Brush and eraser start painting immediately on press
                if current_tool == "brush":
                    pygame.draw.circle(canvas, current_color, canvas_pos, brush_size)
                elif current_tool == "eraser":
                    pygame.draw.circle(canvas, WHITE, canvas_pos, brush_size * 3)

        # ── Mouse MOTION ──────────────────────────────────────
        if event.type == pygame.MOUSEMOTION:
            if drawing and on_canvas(mouse_pos):
                if current_tool == "brush":
                    # Connect last and current position with a filled line
                    # for a smooth, continuous stroke
                    if last_pos:
                        pygame.draw.line(canvas, current_color,
                                         last_pos, canvas_pos, brush_size * 2)
                    pygame.draw.circle(canvas, current_color, canvas_pos, brush_size)
                    last_pos = canvas_pos

                elif current_tool == "eraser":
                    # Erase by painting white with a larger radius
                    esz = brush_size * 3
                    if last_pos:
                        pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, esz * 2)
                    pygame.draw.circle(canvas, WHITE, canvas_pos, esz)
                    last_pos = canvas_pos

                # All other tools only render a live preview; canvas not touched here

        # ── Mouse button UP ───────────────────────────────────
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and drag_start:
                # Commit the finished shape to the canvas permanently
                draw_shape(canvas, current_tool, drag_start,
                           canvas_pos, current_color, brush_size)

            drawing    = False
            drag_start = None
            last_pos   = None

    # ── Render ───────────────────────────────────────────────
    screen.fill(WHITE)

    # 1. Blit the canvas below the toolbar
    screen.blit(canvas, (0, TOOLBAR_H))

    # 2. Live drag preview for shape tools (drawn on a canvas copy so
    #    the original canvas pixel data is never dirtied mid-drag)
    if drawing and drag_start and current_tool in PREVIEW_TOOLS:
        preview = canvas.copy()
        draw_shape(preview, current_tool, drag_start,
                   canvas_pos, current_color, brush_size)
        screen.blit(preview, (0, TOOLBAR_H))

    # 3. Eraser cursor: show a circle outline at the mouse position
    if current_tool == "eraser":
        pygame.draw.circle(screen, DARK_GRAY, mouse_pos, brush_size * 3, 2)

    # 4. Toolbar is drawn last so it always sits on top
    draw_toolbar(screen, current_tool, current_color, brush_size)

    pygame.display.flip()