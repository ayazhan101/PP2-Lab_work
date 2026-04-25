import pygame
from collections import deque


def flood_fill(surface, start_pos, fill_color, canvas_rect):
    x, y = start_pos

    if not canvas_rect.collidepoint(x, y):
        return

    target_color = surface.get_at((x, y))
    fill_color = pygame.Color(fill_color)

    if target_color == fill_color:
        return

    queue = deque()
    queue.append((x, y))

    while queue:
        px, py = queue.popleft()

        if not canvas_rect.collidepoint(px, py):
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), fill_color)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def draw_shape(surface, tool, start_pos, end_pos, color, thickness):
    x1, y1 = start_pos
    x2, y2 = end_pos

    rect = pygame.Rect(
        min(x1, x2),
        min(y1, y2),
        abs(x2 - x1),
        abs(y2 - y1)
    )

    if tool == "line":
        pygame.draw.line(surface, color, start_pos, end_pos, thickness)

    elif tool == "rectangle":
        pygame.draw.rect(surface, color, rect, thickness)

    elif tool == "circle":
        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        pygame.draw.circle(surface, color, start_pos, radius, thickness)

    elif tool == "square":
        size = min(abs(x2 - x1), abs(y2 - y1))
        rect = pygame.Rect(
            x1,
            y1,
            size if x2 >= x1 else -size,
            size if y2 >= y1 else -size
        )
        rect.normalize()
        pygame.draw.rect(surface, color, rect, thickness)

    elif tool == "right_triangle":
        points = [
            (x1, y1),
            (x1, y2),
            (x2, y2)
        ]
        pygame.draw.polygon(surface, color, points, thickness)

    elif tool == "equilateral_triangle":
        points = [
            ((x1 + x2) // 2, y1),
            (x1, y2),
            (x2, y2)
        ]
        pygame.draw.polygon(surface, color, points, thickness)

    elif tool == "rhombus":
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        points = [
            (cx, y1),
            (x2, cy),
            (cx, y2),
            (x1, cy)
        ]
        pygame.draw.polygon(surface, color, points, thickness)