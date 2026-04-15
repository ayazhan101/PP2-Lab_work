import pygame
import random
import sys

pygame.init()


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game")

clock = pygame.time.Clock()


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
RED = (220, 40, 40)
BLUE = (40, 80, 220)
GREEN = (30, 180, 60)
YELLOW = (255, 215, 0)

# Fonts
font_small = pygame.font.SysFont("Verdana", 20)
font_big = pygame.font.SysFont("Verdana", 48)


# Road settings
ROAD_LEFT = 50
ROAD_RIGHT = 350
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) // 3

# Enemy speed and score
enemy_speed = 5
score = 0
coins_collected = 0

# Custom event: increase difficulty over time
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Custom event: spawn coins from time to time
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 1500)


def lane_center(lane_index):
    """
    Returns the x-coordinate of the center of a lane.
    lane_index can be 0, 1, or 2.
    """
    return ROAD_LEFT + lane_index * LANE_WIDTH + LANE_WIDTH // 2


def draw_road(surface, offset):
    """
    Draw the road, borders, and moving dashed lane lines.
    """
    # Grass/background
    surface.fill(GREEN)

    # Road body
    pygame.draw.rect(surface, DARK_GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))

    # Road borders
    pygame.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, SCREEN_HEIGHT), 4)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 4)

    # Dashed vertical lane lines
    dash_height = 30
    gap = 20

    for lane_x in [ROAD_LEFT + LANE_WIDTH, ROAD_LEFT + 2 * LANE_WIDTH]:
        y = -offset
        while y < SCREEN_HEIGHT:
            pygame.draw.rect(surface, WHITE, (lane_x - 3, y, 6, dash_height))
            y += dash_height + gap



class Player(pygame.sprite.Sprite):
    """
    Player car controlled by the keyboard.
    """
    def __init__(self):
        super().__init__()

        self.width = 40
        self.height = 70
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

       
        pygame.draw.rect(self.image, BLUE, (0, 10, self.width, self.height - 20), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (5, 0, self.width - 10, 20), border_radius=6)
        pygame.draw.rect(self.image, BLACK, (5, self.height - 15, 10, 10), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (self.width - 15, self.height - 15, 10, 10), border_radius=3)

        self.rect = self.image.get_rect()
        self.rect.center = (lane_center(1), SCREEN_HEIGHT - 90)

        self.move_speed = 6

    def move(self):
        """
        Move left/right with arrow keys and keep the player inside the road.
        """
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_LEFT]:
            self.rect.move_ip(-self.move_speed, 0)

        if pressed_keys[pygame.K_RIGHT]:
            self.rect.move_ip(self.move_speed, 0)

        if self.rect.left < ROAD_LEFT + 5:
            self.rect.left = ROAD_LEFT + 5

        if self.rect.right > ROAD_RIGHT - 5:
            self.rect.right = ROAD_RIGHT - 5


class Enemy(pygame.sprite.Sprite):
    """
    Enemy car that moves downward.
    """
    def __init__(self):
        super().__init__()

        self.width = 40
        self.height = 70
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    
        pygame.draw.rect(self.image, RED, (0, 10, self.width, self.height - 20), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (5, 0, self.width - 10, 20), border_radius=6)
        pygame.draw.rect(self.image, BLACK, (5, self.height - 15, 10, 10), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (self.width - 15, self.height - 15, 10, 10), border_radius=3)

        self.rect = self.image.get_rect()

        self.reset_position()

    def reset_position(self):
        """
        Put the enemy back above the screen in a random lane.
        """
        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-200, -80))

    def move(self):
        """
        Move enemy downward. If it leaves the screen,
        reset it to the top and increase score.
        """
        global score

        self.rect.move_ip(0, enemy_speed)

        if self.rect.top > SCREEN_HEIGHT:
            score += 1
            self.reset_position()


class Coin(pygame.sprite.Sprite):
    """
    Coin sprite that appears randomly on the road.
    The player can collect it.
    """
    def __init__(self):
        super().__init__()

        size = 22
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)


        pygame.draw.circle(self.image, YELLOW, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, BLACK, (size // 2, size // 2), size // 2, 2)

        self.rect = self.image.get_rect()

        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-120, -40))

        self.speed = enemy_speed

    def update(self):
        """
        Move the coin downward.
        If it goes off-screen, remove it.
        """
        self.rect.move_ip(0, enemy_speed)

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


player = Player()

enemy1 = Enemy()
enemy2 = Enemy()

enemies = pygame.sprite.Group()
enemies.add(enemy1, enemy2)

coins = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(player, enemy1, enemy2)

road_offset = 0

game_over_text = font_big.render("Game Over", True, BLACK)
restart_text = font_small.render("Press R to Restart or Q to Quit", True, BLACK)

running = True
game_over = False

# Main game loop

while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    
        if event.type == INC_SPEED and not game_over:
            enemy_speed += 0.2

    
        if event.type == SPAWN_COIN and not game_over:
            if len(coins) < 3:
                coin = Coin()
                coins.add(coin)
                all_sprites.add(coin)


        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                enemy_speed = 5
                score = 0
                coins_collected = 0
                game_over = False

                for coin in coins:
                    coin.kill()

                player.rect.center = (lane_center(1), SCREEN_HEIGHT - 90)
                enemy1.reset_position()
                enemy2.reset_position()

            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    if not game_over:
        player.move()

        for enemy in enemies:
            enemy.move()

        coins.update()

        collected = pygame.sprite.spritecollide(player, coins, True)
        if collected:
            coins_collected += len(collected)

        if pygame.sprite.spritecollideany(player, enemies):
            game_over = True


        road_offset = (road_offset + int(enemy_speed)) % 50

    
    draw_road(screen, road_offset)

    
    for entity in all_sprites:
        screen.blit(entity.image, entity.rect)


    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))


    coin_text = font_small.render(f"Coins: {coins_collected}", True, WHITE)
    screen.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 10, 10))

    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))

        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 240))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 310))

    pygame.display.update()
    clock.tick(FPS)