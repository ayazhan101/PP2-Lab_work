import pygame
import sys
from ball import Ball

pygame.init()

# Размер окна
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")

# Цвета
WHITE = (255, 255, 255)

# Создаём шар в центре
ball = Ball(
    x=WIDTH // 2,
    y=HEIGHT // 2,
    radius=25,
    screen_width=WIDTH,
    screen_height=HEIGHT
)

clock = pygame.time.Clock()


def main():
    running = True

    while running:
        screen.fill(WHITE)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    ball.move_up()

                elif event.key == pygame.K_DOWN:
                    ball.move_down()

                elif event.key == pygame.K_LEFT:
                    ball.move_left()

                elif event.key == pygame.K_RIGHT:
                    ball.move_right()

        
        ball.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()