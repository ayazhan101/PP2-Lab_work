import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Practice10")

clock = pygame.time.Clock()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 180, 0)

current_color = BLACK


# Tools
TOOL_SQUARE = "SQUARE"
TOOL_RIGHT_TRI = "RIGHT_TRI"
TOOL_EQ_TRI = "EQ_TRI"
TOOL_RHOMBUS = "RHOMBUS"

current_tool = TOOL_SQUARE


# Canvas
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)


# Buttons
font = pygame.font.SysFont("Arial", 20)

square_btn = pygame.Rect(20, 20, 120, 40)
right_tri_btn = pygame.Rect(150, 20, 160, 40)
eq_tri_btn = pygame.Rect(320, 20, 180, 40)
rhombus_btn = pygame.Rect(510, 20, 140, 40)


# Drawing state
drawing = False
start_pos = None
preview = None


def draw_button(rect, text, active):
    """
    Draw UI button with highlight if selected.
    """
    color = GRAY if active else WHITE
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

    label = font.render(text, True, BLACK)
    screen.blit(label, (rect.x + 10, rect.y + 10))


def draw_toolbar():
    """
    Draw toolbar with tool buttons.
    """
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    draw_button(square_btn, "Square", current_tool == TOOL_SQUARE)
    draw_button(right_tri_btn, "Right Triangle", current_tool == TOOL_RIGHT_TRI)
    draw_button(eq_tri_btn, "Equilateral", current_tool == TOOL_EQ_TRI)
    draw_button(rhombus_btn, "Rhombus", current_tool == TOOL_RHOMBUS)


def get_square_rect(start, end):
    """
    Create a perfect square (equal width and height).
    """
    x1, y1 = start
    x2, y2 = end

    size = min(abs(x2 - x1), abs(y2 - y1))

    return pygame.Rect(
        x1,
        y1 - TOOLBAR_HEIGHT,
        size if x2 > x1 else -size,
        size if y2 > y1 else -size
    )


def draw_right_triangle(surface, start, end):
    """
    Draw right triangle using 3 points.
    """
    x1, y1 = start
    x2, y2 = end

    points = [
        (x1, y1 - TOOLBAR_HEIGHT),
        (x2, y2 - TOOLBAR_HEIGHT),
        (x1, y2 - TOOLBAR_HEIGHT)
    ]

    pygame.draw.polygon(surface, current_color, points, 2)


def draw_equilateral_triangle(surface, start, end):
    """
    Draw equilateral triangle using math.
    """
    x1, y1 = start
    x2, y2 = end

    side = abs(x2 - x1)

    height = side * math.sqrt(3) / 2

    p1 = (x1, y1 - TOOLBAR_HEIGHT)
    p2 = (x1 + side, y1 - TOOLBAR_HEIGHT)
    p3 = (x1 + side / 2, y1 - height - TOOLBAR_HEIGHT)

    pygame.draw.polygon(surface, current_color, [p1, p2, p3], 2)


def draw_rhombus(surface, start, end):
    """
    Draw rhombus (diamond shape).
    """
    x1, y1 = start
    x2, y2 = end

    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2 - TOOLBAR_HEIGHT

    dx = abs(x2 - x1) // 2
    dy = abs(y2 - y1) // 2

    points = [
        (cx, cy - dy),
        (cx + dx, cy),
        (cx, cy + dy),
        (cx - dx, cy)
    ]

    pygame.draw.polygon(surface, current_color, points, 2)



running = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if square_btn.collidepoint((mx, my)):
                current_tool = TOOL_SQUARE
            elif right_tri_btn.collidepoint((mx, my)):
                current_tool = TOOL_RIGHT_TRI
            elif eq_tri_btn.collidepoint((mx, my)):
                current_tool = TOOL_EQ_TRI
            elif rhombus_btn.collidepoint((mx, my)):
                current_tool = TOOL_RHOMBUS

            elif my > TOOLBAR_HEIGHT:
                drawing = True
                start_pos = (mx, my)
                preview = canvas.copy()

        # Mouse move (preview)
        elif event.type == pygame.MOUSEMOTION and drawing:
            mx, my = event.pos

            canvas = preview.copy()

            if current_tool == TOOL_SQUARE:
                rect = get_square_rect(start_pos, (mx, my))
                pygame.draw.rect(canvas, current_color, rect, 2)

            elif current_tool == TOOL_RIGHT_TRI:
                draw_right_triangle(canvas, start_pos, (mx, my))

            elif current_tool == TOOL_EQ_TRI:
                draw_equilateral_triangle(canvas, start_pos, (mx, my))

            elif current_tool == TOOL_RHOMBUS:
                draw_rhombus(canvas, start_pos, (mx, my))

        # Mouse release
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False

    draw_toolbar()
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()