import pygame
import random
import sys


pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer with Weighted Coins")

clock = pygame.time.Clock()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
GREEN = (30, 180, 60)
BLUE = (40, 90, 220)
RED = (220, 40, 40)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 0, 180)


# Fonts
font_small = pygame.font.SysFont("Verdana", 20)
font_big = pygame.font.SysFont("Verdana", 42)

# Road settings
ROAD_LEFT = 50
ROAD_RIGHT = 350
LANE_COUNT = 3
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT


enemy_speed = 5
road_speed = 5


COINS_TO_LEVEL_UP = 5

score = 0                 
coins_collected = 0       
coin_points = 0            

SPAWN_COIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_COIN, 1400)


def lane_center(lane_index):
    """
    Return x-coordinate of the center of a lane.
    """
    return ROAD_LEFT + lane_index * LANE_WIDTH + LANE_WIDTH // 2


def draw_road(surface, offset):
    """
    Draw road, borders, and moving dashed lines.
    """
    #Grass/background
    surface.fill(GREEN)

    #Road
    pygame.draw.rect(surface, DARK_GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))

    #Borders
    pygame.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    #Dashed lane lines
    dash_height = 30
    gap = 20

    for lane_x in [ROAD_LEFT + LANE_WIDTH, ROAD_LEFT + 2 * LANE_WIDTH]:
        y = -offset
        while y < HEIGHT:
            pygame.draw.rect(surface, WHITE, (lane_x - 3, y, 6, dash_height))
            y += dash_height + gap


class Player(pygame.sprite.Sprite):
    """
    Player car controlled by arrow keys.
    """
    def __init__(self):
        super().__init__()

        self.width = 40
        self.height = 70
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        #Draw simple blue car
        pygame.draw.rect(self.image, BLUE, (0, 10, self.width, self.height - 20), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (5, 0, self.width - 10, 20), border_radius=6)
        pygame.draw.rect(self.image, BLACK, (5, self.height - 15, 10, 10), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (self.width - 15, self.height - 15, 10, 10), border_radius=3)

        self.rect = self.image.get_rect()
        self.rect.center = (lane_center(1), HEIGHT - 90)

        self.move_speed = 6

    def move(self):
        """
        Move player left or right.
        Keep the car inside the road.
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-self.move_speed, 0)
        if keys[pygame.K_RIGHT]:
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

        #Draw simple red car
        pygame.draw.rect(self.image, RED, (0, 10, self.width, self.height - 20), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (5, 0, self.width - 10, 20), border_radius=6)
        pygame.draw.rect(self.image, BLACK, (5, self.height - 15, 10, 10), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (self.width - 15, self.height - 15, 10, 10), border_radius=3)

        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        """
        Put enemy in a random lane above the screen.
        """
        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-220, -80))

    def move(self):
        """
        Move enemy down.
        If it leaves screen, reset position and add score.
        """
        global score

        self.rect.move_ip(0, enemy_speed)

        if self.rect.top > HEIGHT:
            score += 1
            self.reset_position()


class Coin(pygame.sprite.Sprite):
    """
    Coin with random weight.
    Different weights give different coin values.
    """
    def __init__(self):
        super().__init__()

        # Random weight:
        # 1 = small coin
        # 2 = medium coin
        # 3 = heavy/valuable coin
        self.weight = random.choice([1, 2, 3])

       
        if self.weight == 1:
            self.color = YELLOW
            self.radius = 10
        elif self.weight == 2:
            self.color = ORANGE
            self.radius = 13
        else:
            self.color = PURPLE
            self.radius = 16

        size = self.radius * 2 + 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

       
        pygame.draw.circle(self.image, self.color, (size // 2, size // 2), self.radius)
        pygame.draw.circle(self.image, BLACK, (size // 2, size // 2), self.radius, 2)

       
        text = font_small.render(str(self.weight), True, BLACK)
        text_rect = text.get_rect(center=(size // 2, size // 2))
        self.image.blit(text, text_rect)

        self.rect = self.image.get_rect()

        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-150, -50))

    def update(self):
        """
        Move coin downward.
        Remove it if it leaves screen.
        """
        self.rect.move_ip(0, road_speed)

        if self.rect.top > HEIGHT:
            self.kill()


def draw_hud(surface):
    """
    Draw score, number of coins, and total coin points.
    """
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    coins_text = font_small.render(f"Coins: {coins_collected}", True, WHITE)
    weight_text = font_small.render(f"Coin points: {coin_points}", True, WHITE)
    speed_text = font_small.render(f"Enemy speed: {enemy_speed}", True, WHITE)

    surface.blit(score_text, (10, 10))
    surface.blit(coins_text, (10, 35))
    surface.blit(weight_text, (10, 60))
    surface.blit(speed_text, (10, 85))


def draw_game_over(surface):
    """
    Draw game over message.
    """
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(WHITE)
    surface.blit(overlay, (0, 0))

    game_over_text = font_big.render("Game Over", True, BLACK)
    info_text = font_small.render("Press R to restart or Q to quit", True, BLACK)

    surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 240))
    surface.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 310))


def reset_game():
    """
    Reset all game variables and objects.
    """
    global enemy_speed, road_speed, score, coins_collected, coin_points, road_offset, game_over

    enemy_speed = 5
    road_speed = 5
    score = 0
    coins_collected = 0
    coin_points = 0
    road_offset = 0
    game_over = False

    player.rect.center = (lane_center(1), HEIGHT - 90)

    for enemy in enemies:
        enemy.reset_position()

    for coin in coins:
        coin.kill()



player = Player()

enemy1 = Enemy()
enemy2 = Enemy()

enemies = pygame.sprite.Group()
enemies.add(enemy1, enemy2)

coins = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(player, enemy1, enemy2)

road_offset = 0
game_over = False
running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        
        if event.type == SPAWN_COIN and not game_over:
            if len(coins) < 3:
                coin = Coin()
                coins.add(coin)
                all_sprites.add(coin)

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_q:
                running = False

    if not game_over:
        #Move player
        player.move()

        #Move enemies
        for enemy in enemies:
            enemy.move()

        #Move coins
        coins.update()

    
        collected_coins = pygame.sprite.spritecollide(player, coins, True)
        for coin in collected_coins:
            coins_collected += 1
            coin_points += coin.weight

            
            if coins_collected % COINS_TO_LEVEL_UP == 0:
                enemy_speed += 1
                road_speed += 1

        
        if pygame.sprite.spritecollideany(player, enemies):
            game_over = True

        # Update moving road line offset
        road_offset = (road_offset + road_speed) % 50

    # Draw everything
    draw_road(screen, road_offset)

    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)

    draw_hud(screen)

    # Small legend for coin weights
    legend1 = font_small.render("Yellow=1", True, WHITE)
    legend2 = font_small.render("Orange=2", True, WHITE)
    legend3 = font_small.render("Purple=3", True, WHITE)

    screen.blit(legend1, (250, 10))
    screen.blit(legend2, (250, 35))
    screen.blit(legend3, (250, 60))

    if game_over:
        draw_game_over(screen)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()