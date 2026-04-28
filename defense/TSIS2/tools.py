# ============================================================
# tools.py — Drawing tool implementations for Paint TSIS 2
# Each tool class handles its own draw / preview / commit logic.
# ============================================================

import pygame
import math
from collections import deque


# ════════════════════════════════════════════════════════════ #
#  Geometry helpers (reused by multiple shape tools)           #
# ════════════════════════════════════════════════════════════ #

def square_points(start, end):
    """
    Four corners of a square anchored at `start`.
    Side = max(|dx|, |dy|), direction preserved so shape tracks cursor.
    """
    dx   = end[0] - start[0]
    dy   = end[1] - start[1]
    side = max(abs(dx), abs(dy))
    sx   = side if dx >= 0 else -side
    sy   = side if dy >= 0 else -side
    x0, y0 = start
    return [(x0, y0), (x0+sx, y0), (x0+sx, y0+sy), (x0, y0+sy)]


def right_triangle_points(start, end):
    """
    Right angle at `start`; legs run along X and Y axes.
    """
    x0, y0 = start
    x1, y1 = end
    return [(x0, y0), (x0, y1), (x1, y1)]


def equilateral_triangle_points(start, end):
    """
    Base is horizontal from start to (end_x, start_y).
    Apex height = (√3/2) × |base width|.
    """
    x0, y0 = start
    x1, y1 = end
    mid_x  = (x0 + x1) / 2
    h      = abs(x1 - x0) * math.sqrt(3) / 2
    # Apex goes opposite to drag direction
    apex_y = y0 - h if y1 <= y0 else y0 + h
    return [(x0, y0), (x1, y0), (int(mid_x), int(apex_y))]


def rhombus_points(start, end):
    """
    Rhombus inscribed in the bounding box — four midpoint vertices.
    """
    x0, y0 = start
    x1, y1 = end
    mx, my = (x0+x1)//2, (y0+y1)//2
    return [(mx, y0), (x1, my), (mx, y1), (x0, my)]


# ════════════════════════════════════════════════════════════ #
#  Flood-fill (BFS, pixel-level)                               #
# ════════════════════════════════════════════════════════════ #

def flood_fill(surface, pos, fill_color):
    """
    BFS flood-fill starting at canvas pixel `pos`.
    Replaces all contiguous pixels matching the seed color with `fill_color`.
    Stops at pixels whose color differs from the seed (boundary detection).

    Args:
        surface    : pygame.Surface to fill in-place
        pos        : (x, y) click position in surface coordinates
        fill_color : (R, G, B) tuple for the fill
    """
    x, y = pos
    w, h = surface.get_size()

    # Clamp click position to surface bounds
    if not (0 <= x < w and 0 <= y < h):
        return

    # Get the target color at the click point (ignore alpha)
    target = surface.get_at((x, y))[:3]
    fill   = tuple(fill_color[:3])

    # Nothing to do if the region is already the fill color
    if target == fill:
        return

    # BFS queue
    queue   = deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        # Check this pixel still matches target (guards against already filled)
        if surface.get_at((cx, cy))[:3] != target:
            continue
        surface.set_at((cx, cy), fill)

        # Add 4-connected neighbours
        for nx, ny in ((cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if surface.get_at((nx, ny))[:3] == target:
                    visited.add((nx, ny))
                    queue.append((nx, ny))


# ════════════════════════════════════════════════════════════ #
#  Shape commit / preview                                      #
# ════════════════════════════════════════════════════════════ #

# Set of tools whose geometry is computed as a polygon vertex list
POLYGON_TOOLS = {"square", "rtriangle", "etriangle", "rhombus"}

def get_polygon(tool, start, end):
    """Return vertex list for polygon tools; None otherwise."""
    if tool == "square":    return square_points(start, end)
    if tool == "rtriangle": return right_triangle_points(start, end)
    if tool == "etriangle": return equilateral_triangle_points(start, end)
    if tool == "rhombus":   return rhombus_points(start, end)
    return None


def draw_shape(surf, tool, start, end, color, stroke):
    """
    Commit a finished shape to `surf`.
    Works for: line, rect, circle, and all polygon tools.
    Pencil, eraser, fill, and text are handled elsewhere.
    """
    if tool == "line":
        pygame.draw.line(surf, color, start, end, max(1, stroke))

    elif tool == "rect":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(surf, color, (x, y, w, h), max(1, stroke))

    elif tool == "circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(abs(end[0]-start[0])//2, abs(end[1]-start[1])//2, 1)
        pygame.draw.circle(surf, color, (cx, cy), r, max(1, stroke))

    elif tool in POLYGON_TOOLS:
        pts = get_polygon(tool, start, end)
        if pts and len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts, max(1, stroke))