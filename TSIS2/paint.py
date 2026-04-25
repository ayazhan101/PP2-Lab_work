import pygame
import datetime
from tools import flood_fill, draw_shape

pygame.init()

WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 90

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint")

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22)
small_font = pygame.font.SysFont("Arial", 16)

canvas_rect = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

current_color = (0, 0, 0)
brush_size = 5

tool = "pencil"

drawing = False
start_pos = None
last_pos = None

text_mode = False
text_pos = None
text_value = ""

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 180, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 165, 0),
    (128, 0, 128),
    (255, 255, 255)
]

tools = [
    "pencil",
    "line",
    "rectangle",
    "circle",
    "square",
    "right_triangle",
    "equilateral_triangle",
    "rhombus",
    "eraser",
    "fill",
    "text"
]


def get_canvas_pos(pos):
    return pos[0], pos[1] - TOOLBAR_HEIGHT


def save_canvas():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paint_{timestamp}.png"
    pygame.image.save(canvas, filename)
    print(f"Saved as {filename}")


def draw_toolbar():
    pygame.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, TOOLBAR_HEIGHT))

    x = 10
    y = 10

    for t in tools:
        rect = pygame.Rect(x, y, 85, 30)

        if tool == t:
            pygame.draw.rect(screen, (180, 180, 255), rect)
        else:
            pygame.draw.rect(screen, (240, 240, 240), rect)

        pygame.draw.rect(screen, (0, 0, 0), rect, 1)

        text = small_font.render(t, True, (0, 0, 0))
        screen.blit(text, (x + 5, y + 7))

        x += 90

        if x > WIDTH - 100:
            x = 10
            y += 35

    color_x = 10
    color_y = 55

    for c in colors:
        rect = pygame.Rect(color_x, color_y, 30, 25)
        pygame.draw.rect(screen, c, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        if current_color == c:
            pygame.draw.rect(screen, (255, 0, 0), rect, 3)

        color_x += 35

    info = f"Tool: {tool} | Size: {brush_size}px | Keys: 1=small, 2=medium, 3=large | Ctrl+S=save"
    info_text = small_font.render(info, True, (0, 0, 0))
    screen.blit(info_text, (350, 60))


running = True

while running:
    screen.fill((255, 255, 255))
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    preview = canvas.copy()

    if drawing and start_pos and tool in [
        "line",
        "rectangle",
        "circle",
        "square",
        "right_triangle",
        "equilateral_triangle",
        "rhombus"
    ]:
        mouse_pos = pygame.mouse.get_pos()

        if canvas_rect.collidepoint(mouse_pos):
            end_pos = get_canvas_pos(mouse_pos)
            draw_shape(preview, tool, start_pos, end_pos, current_color, brush_size)

        screen.blit(preview, (0, TOOLBAR_HEIGHT))

    if text_mode and text_pos:
        temp_canvas_pos = (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT)
        text_surface = font.render(text_value + "|", True, current_color)
        screen.blit(text_surface, temp_canvas_pos)

    draw_toolbar()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LCTRL] and event.key == pygame.K_s:
                save_canvas()

            elif event.key == pygame.K_1:
                brush_size = 2

            elif event.key == pygame.K_2:
                brush_size = 5

            elif event.key == pygame.K_3:
                brush_size = 10

            elif text_mode:
                if event.key == pygame.K_RETURN:
                    text_surface = font.render(text_value, True, current_color)
                    canvas.blit(text_surface, text_pos)
                    text_mode = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]

                else:
                    text_value += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if mouse_pos[1] < TOOLBAR_HEIGHT:
                clicked = False

                x = 10
                y = 10

                for t in tools:
                    rect = pygame.Rect(x, y, 85, 30)

                    if rect.collidepoint(mouse_pos):
                        tool = t
                        clicked = True

                    x += 90

                    if x > WIDTH - 100:
                        x = 10
                        y += 35

                color_x = 10
                color_y = 55

                for c in colors:
                    rect = pygame.Rect(color_x, color_y, 30, 25)

                    if rect.collidepoint(mouse_pos):
                        current_color = c
                        clicked = True

                    color_x += 35

            elif canvas_rect.collidepoint(mouse_pos):
                canvas_pos = get_canvas_pos(mouse_pos)

                if tool == "text":
                    text_mode = True
                    text_pos = canvas_pos
                    text_value = ""

                elif tool == "fill":
                    flood_fill(canvas, canvas_pos, current_color, canvas.get_rect())

                else:
                    drawing = True
                    start_pos = canvas_pos
                    last_pos = canvas_pos

        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                mouse_pos = pygame.mouse.get_pos()

                if canvas_rect.collidepoint(mouse_pos):
                    canvas_pos = get_canvas_pos(mouse_pos)

                    if tool == "pencil":
                        pygame.draw.line(
                            canvas,
                            current_color,
                            last_pos,
                            canvas_pos,
                            brush_size
                        )
                        last_pos = canvas_pos

                    elif tool == "eraser":
                        pygame.draw.line(
                            canvas,
                            (255, 255, 255),
                            last_pos,
                            canvas_pos,
                            brush_size
                        )
                        last_pos = canvas_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                mouse_pos = pygame.mouse.get_pos()

                if canvas_rect.collidepoint(mouse_pos):
                    end_pos = get_canvas_pos(mouse_pos)

                    if tool in [
                        "line",
                        "rectangle",
                        "circle",
                        "square",
                        "right_triangle",
                        "equilateral_triangle",
                        "rhombus"
                    ]:
                        draw_shape(canvas, tool, start_pos, end_pos, current_color, brush_size)

                drawing = False
                start_pos = None
                last_pos = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()