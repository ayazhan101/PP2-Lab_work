import pygame
import random
import sys


pygame.init()

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20

COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake with Weighted Food")

clock = pygame.time.Clock()


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
YELLOW = (255, 215, 0)
PURPLE = (170, 0, 170)
GRAY = (90, 90, 90)


# Fonts
font = pygame.font.SysFont("Verdana", 24)
small_font = pygame.font.SysFont("Verdana", 18)
big_font = pygame.font.SysFont("Verdana", 48)


snake_speed = 8
score = 0

# Food stays on screen only for this many milliseconds
FOOD_LIFETIME = 5000   # 5 seconds



class Snake:
    def __init__(self):
    
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)   #start moving right
        self.grow_by = 0          #how many body parts should be added

    def move(self):
        """
        Move snake by creating a new head.
        Remove tail unless snake should grow.
        """
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction

        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)

        if self.grow_by > 0:
            self.grow_by -= 1
        else:
            self.body.pop()

    def change_direction(self, new_direction):
        """
        Change movement direction.
        Prevent snake from moving directly backward.
        """
        current_x, current_y = self.direction
        new_x, new_y = new_direction

       
        if (current_x + new_x, current_y + new_y) != (0, 0):
            self.direction = new_direction

    def check_collision(self):
        """
        Check collision with walls and with itself.
        """
        head_x, head_y = self.body[0]

        
        if head_x < 0 or head_x >= COLS or head_y < 0 or head_y >= ROWS:
            return True

        if self.body[0] in self.body[1:]:
            return True

        return False

    def draw(self, surface):
        """
        Draw snake on the screen.
        """
        for index, segment in enumerate(self.body):
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            if index == 0:
                pygame.draw.rect(surface, DARK_GREEN, rect)
            else:
                pygame.draw.rect(surface, GREEN, rect)

            pygame.draw.rect(surface, BLACK, rect, 1)



class Food:
    def __init__(self, snake_body):
        """
        Create food with:
        - random position
        - random weight
        - spawn time for timer logic
        """
        self.weight = random.choice([1, 2, 3])

       
        if self.weight == 1:
            self.color = RED
        elif self.weight == 2:
            self.color = YELLOW
        else:
            self.color = PURPLE

        self.position = self.generate_position(snake_body)
        self.spawn_time = pygame.time.get_ticks()

    def generate_position(self, snake_body):
        """
        Generate random position for food.
        Food must not appear on the snake.
        """
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)

            if (x, y) not in snake_body:
                return (x, y)

    def is_expired(self):
        """
        Return True if the food has existed too long
        and should disappear.
        """
        current_time = pygame.time.get_ticks()
        return current_time - self.spawn_time > FOOD_LIFETIME

    def draw(self, surface):
        """
        Draw food on the field.
        Display its weight as a number.
        """
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

        #Draw weight number on food
        weight_text = small_font.render(str(self.weight), True, BLACK)
        text_rect = weight_text.get_rect(center=rect.center)
        surface.blit(weight_text, text_rect)



def draw_grid():
    """
    Draw grid lines.
    """
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


def draw_hud(food):
    """
    Draw score and food timer information.
    """
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    
    time_left_ms = FOOD_LIFETIME - (pygame.time.get_ticks() - food.spawn_time)
    time_left_sec = max(0, time_left_ms // 1000)

    timer_text = font.render(f"Food timer: {time_left_sec}", True, WHITE)
    screen.blit(timer_text, (350, 10))

    legend1 = small_font.render("Red=1", True, WHITE)
    legend2 = small_font.render("Yellow=2", True, WHITE)
    legend3 = small_font.render("Purple=3", True, WHITE)

    screen.blit(legend1, (10, 45))
    screen.blit(legend2, (80, 45))
    screen.blit(legend3, (180, 45))


def game_over_screen():
    """
    Show game over screen.
    """
    screen.fill(BLACK)

    game_over_text = big_font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 280))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 340))

    pygame.display.update()


def reset_game():
    """
    Reset game state.
    """
    global snake, food, score

    snake = Snake()
    food = Food(snake.body)
    score = 0



snake = Snake()
food = Food(snake.body)

game_over = False
running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
            else:
                if event.key == pygame.K_r:
                    reset_game()
                    game_over = False
                elif event.key == pygame.K_q:
                    running = False

    if not game_over:
        #move snake
        snake.move()

        if snake.check_collision():
            game_over = True

        
        if food.is_expired():
            food = Food(snake.body)

    
        if snake.body[0] == food.position:
            
            score += food.weight

        
            snake.grow_by += food.weight

            #Generate new food
            food = Food(snake.body)

        #Draw everything
        screen.fill(BLACK)
        draw_grid()
        snake.draw(screen)
        food.draw(screen)
        draw_hud(food)
        pygame.display.update()

        clock.tick(snake_speed)

    else:
        game_over_screen()
        clock.tick(10)

pygame.quit()
sys.exit()