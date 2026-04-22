# ============================================================
# Paint — extended from NerdParadise PyGame Tutorial Part 6
# Added: Rectangle tool, Circle tool, Eraser, Color picker
# ============================================================

import pygame
import sys

pygame.init()

# ── Window dimensions ────────────────────────────────────────
SCREEN_W   = 900
SCREEN_H   = 650
TOOLBAR_H  = 70       # height of the top toolbar

# ── Colors ───────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (200, 200, 200)
DARK_GRAY  = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)

# Palette of selectable drawing colors
PALETTE = [
    (0,   0,   0),       # black
    (255, 255, 255),     # white
    (200, 0,   0),       # red
    (0,   180, 0),       # green
    (0,   0,   220),     # blue
    (255, 165, 0),       # orange
    (255, 220, 0),       # yellow
    (160, 0,   200),     # purple
    (0,   200, 200),     # cyan
    (180, 100, 40),      # brown
    (255, 150, 180),     # pink
    (100, 100, 100),     # dark gray
]

# ── Setup ────────────────────────────────────────────────────
screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")
clock   = pygame.time.Clock()

# Canvas is a separate surface below the toolbar
canvas  = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
canvas.fill(WHITE)

# ── Fonts ────────────────────────────────────────────────────
font      = pygame.font.SysFont("Courier New", 13, bold=True)
font_tiny = pygame.font.SysFont("Courier New", 11)


# ════════════════════════════════════════════════════════════ #
#  Tool button                                                 #
# ════════════════════════════════════════════════════════════ #
class ToolButton:
    """A clickable toolbar button with a label."""

    def __init__(self, x, y, w, h, label, tool_name):
        self.rect      = pygame.Rect(x, y, w, h)
        self.label     = label
        self.tool_name = tool_name

    def draw(self, surf, active):
        # Active tool gets a highlighted background
        bg = DARK_GRAY if active else LIGHT_GRAY
        pygame.draw.rect(surf, bg, self.rect, border_radius=6)
        pygame.draw.rect(surf, DARK_GRAY, self.rect, 2, border_radius=6)

        color = WHITE if active else BLACK
        text  = font.render(self.label, True, color)
        surf.blit(text, (self.rect.centerx - text.get_width()  // 2,
                         self.rect.centery - text.get_height() // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ════════════════════════════════════════════════════════════ #
#  Build toolbar buttons                                       #
# ════════════════════════════════════════════════════════════ #
TOOLS = [
    ToolButton(10,  10, 70, 40, "Brush",  "brush"),
    ToolButton(90,  10, 70, 40, "Line",   "line"),
    ToolButton(170, 10, 70, 40, "Rect",   "rect"),
    ToolButton(250, 10, 70, 40, "Circle", "circle"),
    ToolButton(330, 10, 70, 40, "Eraser", "eraser"),
    ToolButton(410, 10, 70, 40, "Clear",  "clear"),   # special action, not a drawing tool
]

# ── Palette color swatches ────────────────────────────────────
SWATCH_SIZE  = 28
SWATCH_START = 500    # x offset where palette starts
SWATCHES     = []
for i, color in enumerate(PALETTE):
    x = SWATCH_START + i * (SWATCH_SIZE + 4)
    SWATCHES.append(pygame.Rect(x, (TOOLBAR_H - SWATCH_SIZE) // 2,
                                SWATCH_SIZE, SWATCH_SIZE))

# ── Brush size buttons ────────────────────────────────────────
SIZE_BUTTONS = []
for i, size in enumerate([2, 5, 10, 18]):
    x = SWATCH_START - 110 + i * 26
    SIZE_BUTTONS.append((pygame.Rect(x, 20, 22, 22), size))


# ════════════════════════════════════════════════════════════ #
#  Draw the toolbar                                            #
# ════════════════════════════════════════════════════════════ #
def draw_toolbar(surf, current_tool, current_color, current_size):
    # Toolbar background
    pygame.draw.rect(surf, GRAY, (0, 0, SCREEN_W, TOOLBAR_H))
    pygame.draw.line(surf, DARK_GRAY, (0, TOOLBAR_H - 1), (SCREEN_W, TOOLBAR_H - 1), 2)

    # Tool buttons
    for btn in TOOLS:
        btn.draw(surf, btn.tool_name == current_tool)

    # Size buttons — small filled circles of increasing size
    for rect, size in SIZE_BUTTONS:
        active = (size == current_size)
        bg     = DARK_GRAY if active else LIGHT_GRAY
        pygame.draw.rect(surf, bg, rect, border_radius=4)
        pygame.draw.rect(surf, DARK_GRAY, rect, 1, border_radius=4)
        r = min(size // 2, 7)
        pygame.draw.circle(surf, BLACK if active else DARK_GRAY, rect.center, r)

    # Color swatches
    for i, (rect, color) in enumerate(zip(SWATCHES, PALETTE)):
        pygame.draw.rect(surf, color, rect)
        # White border on currently selected color
        border = WHITE if color == current_color else DARK_GRAY
        pygame.draw.rect(surf, border, rect, 2)

    # Current color preview box
    preview_rect = pygame.Rect(SCREEN_W - 50, 10, 40, 50 - 10)
    pygame.draw.rect(surf, current_color, preview_rect)
    pygame.draw.rect(surf, DARK_GRAY, preview_rect, 2)
    label = font_tiny.render("color", True, DARK_GRAY)
    surf.blit(label, (SCREEN_W - 48, TOOLBAR_H - 14))


# ════════════════════════════════════════════════════════════ #
#  Draw preview of shape being dragged                         #
# ════════════════════════════════════════════════════════════ #
def draw_preview(surf, tool, start, end, color, size):
    """
    Render a live preview of a rect or line while the user is dragging.
    We blit a temporary surface so the canvas isn't permanently modified.
    """
    if tool == "rect":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        pygame.draw.rect(surf, color, (x, y, w, h), size)

    elif tool == "circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        rx = abs(end[0] - start[0]) // 2
        ry = abs(end[1] - start[1]) // 2
        r  = max(rx, ry, 1)
        pygame.draw.circle(surf, color, (cx, cy), r, size)

    elif tool == "line":
        pygame.draw.line(surf, color, start, end, size)


# ════════════════════════════════════════════════════════════ #
#  State                                                       #
# ════════════════════════════════════════════════════════════ #
current_tool  = "brush"        # active drawing tool
current_color = BLACK          # active drawing color
brush_size    = 5              # brush / stroke width

drawing       = False          # is the mouse button held down?
drag_start    = None           # (x, y) where the drag started (canvas coords)
last_pos      = None           # last mouse position for continuous brush stroke


# ════════════════════════════════════════════════════════════ #
#  Helper: canvas coordinates from screen position             #
# ════════════════════════════════════════════════════════════ #
def to_canvas(screen_pos):
    """Subtract the toolbar height to convert screen → canvas coordinates."""
    return (screen_pos[0], screen_pos[1] - TOOLBAR_H)


def on_canvas(screen_pos):
    """Return True if the position is within the drawable canvas area."""
    return screen_pos[1] >= TOOLBAR_H


# ════════════════════════════════════════════════════════════ #
#  Main loop                                                   #
# ════════════════════════════════════════════════════════════ #
while True:
    clock.tick(60)

    mouse_pos    = pygame.mouse.get_pos()
    canvas_pos   = to_canvas(mouse_pos)

    for event in pygame.event.get():

        # ── Quit ─────────────────────────────────────────────
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            # Keyboard shortcuts for tools
            elif event.key == pygame.K_b:
                current_tool = "brush"
            elif event.key == pygame.K_l:
                current_tool = "line"
            elif event.key == pygame.K_r:
                current_tool = "rect"
            elif event.key == pygame.K_c:
                current_tool = "circle"
            elif event.key == pygame.K_e:
                current_tool = "eraser"
            elif event.key == pygame.K_DELETE:
                canvas.fill(WHITE)   # clear canvas

        # ── Mouse button DOWN ─────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Check toolbar clicks first
            clicked_toolbar = not on_canvas(mouse_pos)

            if clicked_toolbar:
                # Tool buttons
                for btn in TOOLS:
                    if btn.is_clicked(mouse_pos):
                        if btn.tool_name == "clear":
                            canvas.fill(WHITE)    # clear action
                        else:
                            current_tool = btn.tool_name

                # Size buttons
                for rect, size in SIZE_BUTTONS:
                    if rect.collidepoint(mouse_pos):
                        brush_size = size

                # Color swatches
                for rect, color in zip(SWATCHES, PALETTE):
                    if rect.collidepoint(mouse_pos):
                        current_color = color
                        # Switching to a color deselects eraser
                        if current_tool == "eraser":
                            current_tool = "brush"

            else:
                # Start drawing on canvas
                drawing    = True
                drag_start = canvas_pos
                last_pos   = canvas_pos

                # Brush & eraser paint immediately on press
                if current_tool in ("brush", "eraser"):
                    color = WHITE if current_tool == "eraser" else current_color
                    size  = brush_size * 3 if current_tool == "eraser" else brush_size
                    pygame.draw.circle(canvas, color, canvas_pos, size)

        # ── Mouse MOTION (held) ───────────────────────────────
        if event.type == pygame.MOUSEMOTION:
            if drawing and on_canvas(mouse_pos):
                if current_tool == "brush":
                    # Draw a line segment between last and current position
                    # for a smooth continuous stroke
                    if last_pos:
                        pygame.draw.line(canvas, current_color,
                                         last_pos, canvas_pos, brush_size * 2)
                    pygame.draw.circle(canvas, current_color, canvas_pos, brush_size)
                    last_pos = canvas_pos

                elif current_tool == "eraser":
                    # Eraser: paint white with a larger radius
                    eraser_size = brush_size * 3
                    if last_pos:
                        pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, eraser_size * 2)
                    pygame.draw.circle(canvas, WHITE, canvas_pos, eraser_size)
                    last_pos = canvas_pos

                # Line, rect, circle preview is rendered live (not on canvas yet)

        # ── Mouse button UP ───────────────────────────────────
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and drag_start:
                end = canvas_pos

                # Commit shape to canvas permanently on mouse release
                if current_tool == "line":
                    pygame.draw.line(canvas, current_color,
                                     drag_start, end, brush_size)

                elif current_tool == "rect":
                    x = min(drag_start[0], end[0])
                    y = min(drag_start[1], end[1])
                    w = abs(end[0] - drag_start[0])
                    h = abs(end[1] - drag_start[1])
                    pygame.draw.rect(canvas, current_color,
                                     (x, y, w, h), brush_size)

                elif current_tool == "circle":
                    cx = (drag_start[0] + end[0]) // 2
                    cy = (drag_start[1] + end[1]) // 2
                    r  = max(abs(end[0] - drag_start[0]) // 2,
                             abs(end[1] - drag_start[1]) // 2, 1)
                    pygame.draw.circle(canvas, current_color,
                                       (cx, cy), r, brush_size)

            drawing    = False
            drag_start = None
            last_pos   = None

    # ── Render ───────────────────────────────────────────────
    screen.fill(WHITE)

    # 1. Draw canvas (below toolbar)
    screen.blit(canvas, (0, TOOLBAR_H))

    # 2. Draw live shape preview while dragging (line / rect / circle)
    if drawing and drag_start and current_tool in ("line", "rect", "circle"):
        # Temporary surface so preview doesn't dirty the canvas
        preview = canvas.copy()
        draw_preview(preview, current_tool, drag_start, canvas_pos,
                     current_color, brush_size)
        screen.blit(preview, (0, TOOLBAR_H))

    # 3. Draw eraser cursor outline
    if current_tool == "eraser":
        pygame.draw.circle(screen, DARK_GRAY,
                           mouse_pos, brush_size * 3, 2)

    # 4. Draw toolbar on top
    draw_toolbar(screen, current_tool, current_color, brush_size)

    pygame.display.flip()