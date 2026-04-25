import pygame


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)
BLUE = (50, 120, 255)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()

        color = BLUE if self.rect.collidepoint(mouse_pos) else GRAY

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)

        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def draw_text(screen, text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


def ask_username(screen, clock):
    font = pygame.font.SysFont("Arial", 34)
    small_font = pygame.font.SysFont("Arial", 24)

    name = ""
    active = True

    while active:
        screen.fill((25, 25, 25))

        draw_text(screen, "Enter your name", font, WHITE, 400, 200, center=True)
        draw_text(screen, name + "|", font, WHITE, 400, 280, center=True)
        draw_text(screen, "Press ENTER to start", small_font, GRAY, 400, 350, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip() == "":
                        name = "Player"
                    return name

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    if len(name) < 12:
                        name += event.unicode

        pygame.display.flip()
        clock.tick(60)