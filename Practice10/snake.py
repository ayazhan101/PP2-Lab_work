import pygame
import random
import sys

pygame.init()


WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20

# Number of cells
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 215, 0)

# Fonts
font = pygame.font.SysFont("Verdana", 24)
big_font = pygame.font.SysFont("Verdana", 48)


snake_speed = 8

# Score and level
score = 0
level = 1

# How many foods are needed to go to the next level
FOODS_PER_LEVEL = 4



class Snake:
    def __init__(self):
        
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)  
        self.grow = False

    def move(self):
        """
        Move the snake by adding a new head
        in the current direction.
        """
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction

        new_head = (head_x + dir_x, head_y + dir_y)

    
        self.body.insert(0, new_head)

        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_dir):
        """
        Change snake direction.
        Prevent moving directly backward.
        """
        dir_x, dir_y = self.direction
        new_x, new_y = new_dir

        
        if (dir_x + new_x, dir_y + new_y) != (0, 0):
            self.direction = new_dir

    def check_collision(self):
        """
        Check:
        1. collision with border
        2. collision with itself
        """
        head_x, head_y = self.body[0]

       
        # snake leaves playing area
        if head_x < 0 or head_x >= COLS or head_y < 0 or head_y >= ROWS:
            return True

        # Self collision:
        if self.body[0] in self.body[1:]:
            return True

        return False

    def draw(self, surface):
        """
        Draw snake on the screen.
        """
        for i, segment in enumerate(self.body):
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            
            if i == 0:
                pygame.draw.rect(surface, DARK_GREEN, rect)
            else:
                pygame.draw.rect(surface, GREEN, rect)

            # Small border for each segment
            pygame.draw.rect(surface, BLACK, rect, 1)



class Food:
    def __init__(self, snake_body):
        self.position = self.generate_position(snake_body)

    def generate_position(self, snake_body):
        """
        Generate random food position.

        Food must NOT appear:
        - outside the grid
        - on the snake body
        """
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)

            # If position is not on snake, use it
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self, surface):
        """
        Draw food on the screen.
        """
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)



def draw_grid():
    """
    Draw grid lines to make cells visible.
    """
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


def draw_text():
    """
    Draw score and level counters.
    """
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, YELLOW)

    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))


def game_over_screen():
    """
    Show game over message.
    """
    screen.fill(BLACK)

    game_over_text = big_font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    level_text = font.render(f"Level Reached: {level}", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 180))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 260))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 300))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 360))

    pygame.display.update()


def reset_game():
    """
    Reset all game variables.
    """
    global snake, food, score, level, snake_speed

    snake = Snake()
    food = Food(snake.body)
    score = 0
    level = 1
    snake_speed = 8



# Create game objects
snake = Snake()
food = Food(snake.body)

game_over = False
running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #control
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
        snake.move()
        if snake.check_collision():
            game_over = True


        if snake.body[0] == food.position:
            snake.grow = True
            score += 1

            food = Food(snake.body)
            new_level = score // FOODS_PER_LEVEL + 1

            if new_level > level:
                level = new_level

            
                snake_speed += 2

    
        screen.fill(BLACK)
        draw_grid()
        snake.draw(screen)
        food.draw(screen)
        draw_text()
        pygame.display.update()

        #control2
        clock.tick(snake_speed)

    else:
        game_over_screen()
        clock.tick(10)

pygame.quit()
sys.exit()