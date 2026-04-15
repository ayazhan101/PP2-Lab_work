import pygame
import sys


pygame.init()


# Screen settings
WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 100
CANVAS_Y = TOOLBAR_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Paint - Pygame")

clock = pygame.time.Clock()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 180)
ORANGE = (255, 140, 0)

COLOR_LIST = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]


# Fonts
font = pygame.font.SysFont("Arial", 22)


# Tool settings
TOOL_PEN = "PEN"
TOOL_RECT = "RECT"
TOOL_CIRCLE = "CIRCLE"
TOOL_ERASER = "ERASER"

current_tool = TOOL_PEN
current_color = BLACK
brush_size = 5
eraser_size = 20


canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# UI button rectangles
pen_button = pygame.Rect(20, 20, 90, 40)
rect_button = pygame.Rect(120, 20, 120, 40)
circle_button = pygame.Rect(250, 20, 120, 40)
eraser_button = pygame.Rect(380, 20, 100, 40)
clear_button = pygame.Rect(490, 20, 100, 40)

# Color buttons
color_buttons = []
start_x = 620
for i, color in enumerate(COLOR_LIST):
    color_buttons.append((pygame.Rect(start_x + i * 45, 25, 35, 35), color))

# Drawing state
drawing = False
start_pos = None
last_pos = None

# Temporary preview surface for shapes
preview_canvas = None


def draw_toolbar():
    """
    Draw the top toolbar with tool buttons and color selection.
    """
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    draw_button(pen_button, "Pen", current_tool == TOOL_PEN)
    draw_button(rect_button, "Rectangle", current_tool == TOOL_RECT)
    draw_button(circle_button, "Circle", current_tool == TOOL_CIRCLE)
    draw_button(eraser_button, "Eraser", current_tool == TOOL_ERASER)
    draw_button(clear_button, "Clear", False)

    # Draw color selection boxes
    text = font.render("Colors:", True, BLACK)
    screen.blit(text, (620, 0))

    for rect, color in color_buttons:
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        # Highlight selected color
        if color == current_color:
            pygame.draw.rect(screen, WHITE, rect, 3)

    # Show current tool
    tool_text = font.render(f"Tool: {current_tool}", True, BLACK)
    screen.blit(tool_text, (20, 70))


def draw_button(rect, text, active=False):
    """
    Draw a button. Highlight it if active.
    """
    color = DARK_GRAY if active else WHITE
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

    label = font.render(text, True, BLACK)
    label_x = rect.x + (rect.width - label.get_width()) // 2
    label_y = rect.y + (rect.height - label.get_height()) // 2
    screen.blit(label, (label_x, label_y))


def draw_on_canvas(surface, pos, color, size):
    """
    Draw a filled circle for freehand drawing.
    This makes the pen stroke look smooth enough for a simple paint app.
    """
    x, y = pos
    pygame.draw.circle(surface, color, (x, y - TOOLBAR_HEIGHT), size)


def draw_line_continuous(surface, start, end, color, size):
    """
    Draw continuous line by connecting the previous point to the current point.
    """
    x1, y1 = start
    x2, y2 = end

    pygame.draw.line(
        surface,
        color,
        (x1, y1 - TOOLBAR_HEIGHT),
        (x2, y2 - TOOLBAR_HEIGHT),
        size * 2
    )


def normalize_rect(start, end):
    """
    Create a rectangle from two points,
    even if the user drags in reverse direction.
    """
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    return pygame.Rect(left, top - TOOLBAR_HEIGHT, width, height)


running = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Check tool buttons
            if pen_button.collidepoint((mx, my)):
                current_tool = TOOL_PEN
            elif rect_button.collidepoint((mx, my)):
                current_tool = TOOL_RECT
            elif circle_button.collidepoint((mx, my)):
                current_tool = TOOL_CIRCLE
            elif eraser_button.collidepoint((mx, my)):
                current_tool = TOOL_ERASER
            elif clear_button.collidepoint((mx, my)):
                canvas.fill(WHITE)

            # Check color buttons
            for rect, color in color_buttons:
                if rect.collidepoint((mx, my)):
                    current_color = color
                    
            # Start drawing only inside canvas area
            if my >= TOOLBAR_HEIGHT:
                drawing = True
                start_pos = (mx, my)
                last_pos = (mx, my)

                # Save a copy of canvas for previewing shapes
                preview_canvas = canvas.copy()

                # For pen or eraser, draw first point immediately
                if current_tool == TOOL_PEN:
                    draw_on_canvas(canvas, (mx, my), current_color, brush_size)
                elif current_tool == TOOL_ERASER:
                    draw_on_canvas(canvas, (mx, my), WHITE, eraser_size)


        # Mouse movement
        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos

            if drawing and my >= TOOLBAR_HEIGHT:
                if current_tool == TOOL_PEN:
                    draw_line_continuous(canvas, last_pos, (mx, my), current_color, brush_size)
                    draw_on_canvas(canvas, (mx, my), current_color, brush_size)
                    last_pos = (mx, my)

                elif current_tool == TOOL_ERASER:
                    draw_line_continuous(canvas, last_pos, (mx, my), WHITE, eraser_size)
                    draw_on_canvas(canvas, (mx, my), WHITE, eraser_size)
                    last_pos = (mx, my)

                elif current_tool in (TOOL_RECT, TOOL_CIRCLE):
                    canvas = preview_canvas.copy()

                    if current_tool == TOOL_RECT:
                        rect = normalize_rect(start_pos, (mx, my))
                        pygame.draw.rect(canvas, current_color, rect, 2)

                    elif current_tool == TOOL_CIRCLE:
                        center_x = start_pos[0]
                        center_y = start_pos[1] - TOOLBAR_HEIGHT
                        radius = int(((mx - start_pos[0]) ** 2 + (my - start_pos[1]) ** 2) ** 0.5)

                        pygame.draw.circle(canvas, current_color, (center_x, center_y), radius, 2)

    
        # Mouse button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                mx, my = event.pos

                if my >= TOOLBAR_HEIGHT:
                    # Finalize shape on release
                    if current_tool == TOOL_RECT:
                        rect = normalize_rect(start_pos, (mx, my))
                        pygame.draw.rect(canvas, current_color, rect, 2)

                    elif current_tool == TOOL_CIRCLE:
                        center_x = start_pos[0]
                        center_y = start_pos[1] - TOOLBAR_HEIGHT
                        radius = int(((mx - start_pos[0]) ** 2 + (my - start_pos[1]) ** 2) ** 0.5)

                        pygame.draw.circle(canvas, current_color, (center_x, center_y), radius, 2)

            drawing = False
            start_pos = None
            last_pos = None
            preview_canvas = None

    
    draw_toolbar()
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()