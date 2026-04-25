import pygame
import random
import time
from persistence import add_score


WIDTH = 800
HEIGHT = 700

ROAD_X = 180
ROAD_WIDTH = 440
LANES = 4
LANE_WIDTH = ROAD_WIDTH // LANES

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ROAD = (45, 45, 45)
GRASS = (35, 120, 35)
YELLOW = (255, 220, 0)
RED = (220, 40, 40)
BLUE = (40, 100, 255)
GREEN = (40, 200, 80)
ORANGE = (255, 150, 30)
PURPLE = (160, 80, 255)
GRAY = (130, 130, 130)


CAR_COLORS = {
    "blue": BLUE,
    "red": RED,
    "green": GREEN,
    "purple": PURPLE
}


class RacerGame:
    def __init__(self, screen, clock, settings, username):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.username = username

        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 42)

        self.running = True
        self.game_over = False

        self.player_w = 45
        self.player_h = 75
        self.player_x = ROAD_X + ROAD_WIDTH // 2 - self.player_w // 2
        self.player_y = HEIGHT - 120

        self.coins = []
        self.traffic = []
        self.obstacles = []
        self.powerups = []

        self.coin_count = 0
        self.score = 0
        self.distance = 0
        self.finish_distance = 3000

        self.shield = False
        self.active_power = None
        self.power_end_time = 0

        self.base_speed = self.get_base_speed()
        self.speed = self.base_speed

        self.spawn_timer = 0
        self.coin_timer = 0
        self.power_timer = 0

    def get_base_speed(self):
        difficulty = self.settings.get("difficulty", "normal")

        if difficulty == "easy":
            return 4
        elif difficulty == "hard":
            return 7
        return 5

    def player_rect(self):
        return pygame.Rect(self.player_x, self.player_y, self.player_w, self.player_h)

    def get_random_lane_x(self):
        lane = random.randint(0, LANES - 1)
        return ROAD_X + lane * LANE_WIDTH + LANE_WIDTH // 2

    def safe_to_spawn(self, x):
        return abs(x - (self.player_x + self.player_w // 2)) > 80

    def spawn_coin(self):
        x = self.get_random_lane_x()

        self.coins.append({
            "rect": pygame.Rect(x - 12, -30, 24, 24),
            "value": random.choice([1, 2, 5])
        })

    def spawn_traffic(self):
        x = self.get_random_lane_x()

        if not self.safe_to_spawn(x):
            return

        self.traffic.append({
            "rect": pygame.Rect(x - 25, -90, 50, 80),
            "speed": self.speed + random.randint(1, 3)
        })

    def spawn_obstacle(self):
        x = self.get_random_lane_x()

        if not self.safe_to_spawn(x):
            return

        kind = random.choice(["oil", "pothole", "barrier", "speed_bump"])

        self.obstacles.append({
            "rect": pygame.Rect(x - 28, -50, 56, 35),
            "kind": kind
        })

    def spawn_powerup(self):
        x = self.get_random_lane_x()

        self.powerups.append({
            "rect": pygame.Rect(x - 18, -40, 36, 36),
            "type": random.choice(["nitro", "shield", "repair"]),
            "created": time.time()
        })

    def activate_powerup(self, power_type):
        self.active_power = power_type

        if power_type == "nitro":
            self.speed = self.base_speed + 5
            self.power_end_time = time.time() + 4

        elif power_type == "shield":
            self.shield = True
            self.power_end_time = 0

        elif power_type == "repair":
            if self.obstacles:
                self.obstacles.pop(0)

            self.active_power = None

    def update_powerup(self):
        if self.active_power == "nitro":
            if time.time() > self.power_end_time:
                self.speed = self.base_speed
                self.active_power = None

    def handle_collision(self):
        player = self.player_rect()

        for car in self.traffic[:]:
            if player.colliderect(car["rect"]):
                if self.shield:
                    self.traffic.remove(car)
                    self.shield = False
                    self.active_power = None
                else:
                    self.end_game()

        for obs in self.obstacles[:]:
            if player.colliderect(obs["rect"]):
                if obs["kind"] == "oil":
                    self.player_x += random.choice([-50, 50])

                elif obs["kind"] == "speed_bump":
                    self.speed = max(2, self.speed - 2)

                else:
                    if self.shield:
                        self.obstacles.remove(obs)
                        self.shield = False
                        self.active_power = None
                    else:
                        self.end_game()

        for coin in self.coins[:]:
            if player.colliderect(coin["rect"]):
                self.coin_count += coin["value"]
                self.score += coin["value"] * 10
                self.coins.remove(coin)

                if self.coin_count % 10 == 0:
                    self.base_speed += 1

        for power in self.powerups[:]:
            if player.colliderect(power["rect"]):
                if self.active_power is None:
                    self.activate_powerup(power["type"])
                self.powerups.remove(power)

    def end_game(self):
        self.game_over = True
        final_score = int(self.score + self.distance * 0.2 + self.coin_count * 5)
        add_score(self.username, final_score, self.distance)

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= 7

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += 7

        self.player_x = max(ROAD_X, min(ROAD_X + ROAD_WIDTH - self.player_w, self.player_x))

        self.distance += self.speed * 0.4
        self.score += 0.1

        progress_factor = self.distance / 500

        self.spawn_timer += 1
        self.coin_timer += 1
        self.power_timer += 1

        obstacle_rate = max(25, 80 - int(progress_factor * 5))
        traffic_rate = max(35, 90 - int(progress_factor * 6))

        if self.spawn_timer > traffic_rate:
            self.spawn_traffic()
            if random.random() < 0.5:
                self.spawn_obstacle()
            self.spawn_timer = 0

        if self.coin_timer > 45:
            self.spawn_coin()
            self.coin_timer = 0

        if self.power_timer > 400:
            self.spawn_powerup()
            self.power_timer = 0

        for item in self.traffic:
            item["rect"].y += item["speed"]

        for item in self.obstacles:
            item["rect"].y += self.speed

        for coin in self.coins:
            coin["rect"].y += self.speed

        for power in self.powerups:
            power["rect"].y += self.speed

        self.traffic = [x for x in self.traffic if x["rect"].y < HEIGHT + 100]
        self.obstacles = [x for x in self.obstacles if x["rect"].y < HEIGHT + 100]
        self.coins = [x for x in self.coins if x["rect"].y < HEIGHT + 100]

        self.powerups = [
            p for p in self.powerups
            if p["rect"].y < HEIGHT + 100 and time.time() - p["created"] < 7
        ]

        self.update_powerup()
        self.handle_collision()

        if self.distance >= self.finish_distance:
            self.end_game()

    def draw_road(self):
        self.screen.fill(GRASS)

        pygame.draw.rect(self.screen, ROAD, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))

        for i in range(1, LANES):
            x = ROAD_X + i * LANE_WIDTH
            pygame.draw.line(self.screen, WHITE, (x, 0), (x, HEIGHT), 3)

        pygame.draw.rect(self.screen, YELLOW, (ROAD_X - 8, 0, 8, HEIGHT))
        pygame.draw.rect(self.screen, YELLOW, (ROAD_X + ROAD_WIDTH, 0, 8, HEIGHT))

    def draw_player(self):
        color_name = self.settings.get("car_color", "blue")
        color = CAR_COLORS.get(color_name, BLUE)

        rect = self.player_rect()
        pygame.draw.rect(self.screen, color, rect, border_radius=8)

        if self.shield:
            pygame.draw.circle(self.screen, (100, 200, 255), rect.center, 50, 3)

    def draw_items(self):
        for coin in self.coins:
            color = YELLOW if coin["value"] == 1 else ORANGE
            if coin["value"] == 5:
                color = PURPLE

            pygame.draw.ellipse(self.screen, color, coin["rect"])

        for car in self.traffic:
            pygame.draw.rect(self.screen, RED, car["rect"], border_radius=8)

        for obs in self.obstacles:
            rect = obs["rect"]

            if obs["kind"] == "oil":
                pygame.draw.ellipse(self.screen, BLACK, rect)

            elif obs["kind"] == "pothole":
                pygame.draw.ellipse(self.screen, DARK_GRAY := (40, 40, 40), rect)

            elif obs["kind"] == "speed_bump":
                pygame.draw.rect(self.screen, ORANGE, rect)

            else:
                pygame.draw.rect(self.screen, GRAY, rect)

        for power in self.powerups:
            rect = power["rect"]

            if power["type"] == "nitro":
                color = ORANGE
                label = "N"
            elif power["type"] == "shield":
                color = BLUE
                label = "S"
            else:
                color = GREEN
                label = "R"

            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            text = self.font.render(label, True, WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_hud(self):
        remaining = max(0, int(self.finish_distance - self.distance))

        texts = [
            f"Player: {self.username}",
            f"Coins: {self.coin_count}",
            f"Score: {int(self.score)}",
            f"Distance: {int(self.distance)} m",
            f"Remaining: {remaining} m",
            f"Speed: {self.speed}"
        ]

        y = 20

        for text in texts:
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (20, y))
            y += 30

        if self.active_power:
            power_text = f"Power: {self.active_power}"

            if self.active_power == "nitro":
                left = max(0, int(self.power_end_time - time.time()))
                power_text += f" {left}s"

            surface = self.font.render(power_text, True, YELLOW)
            self.screen.blit(surface, (560, 20))

    def draw(self):
        self.draw_road()
        self.draw_items()
        self.draw_player()
        self.draw_hud()

    def run(self):
        while self.running and not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)

        final_score = int(self.score + self.distance * 0.2 + self.coin_count * 5)

        return {
            "score": final_score,
            "distance": int(self.distance),
            "coins": self.coin_count
        }