import pygame
import random
import sys
import json
import os
import time
from datetime import datetime


pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer Game")

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
CYAN = (0, 200, 255)

# Fonts
font_small = pygame.font.SysFont("Verdana", 18)
font_medium = pygame.font.SysFont("Verdana", 24)
font_big = pygame.font.SysFont("Verdana", 40)

# Road settings
ROAD_LEFT = 50
ROAD_RIGHT = 350
LANE_COUNT = 3
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}

CAR_COLORS = {
    "blue": BLUE,
    "red": RED,
    "green": GREEN,
    "purple": PURPLE
}


def load_json(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump(default_data, file, indent=4)
        return default_data

    with open(filename, "r") as file:
        return json.load(file)


def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def load_settings():
    return load_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)


def load_leaderboard():
    return load_json(LEADERBOARD_FILE, [])


def save_score(name, score, distance):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": name,
        "score": int(score),
        "distance": int(distance),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]
    save_json(LEADERBOARD_FILE, leaderboard)


def lane_center(lane_index):
    return ROAD_LEFT + lane_index * LANE_WIDTH + LANE_WIDTH // 2


def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


def draw_button(rect, text):
    mouse_pos = pygame.mouse.get_pos()
    color = CYAN if rect.collidepoint(mouse_pos) else GRAY

    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)

    draw_text(text, font_medium, BLACK, rect.centerx, rect.centery, center=True)


def draw_road(surface, offset):
    surface.fill(GREEN)

    pygame.draw.rect(surface, DARK_GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))

    pygame.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    dash_height = 30
    gap = 20

    for lane_x in [ROAD_LEFT + LANE_WIDTH, ROAD_LEFT + 2 * LANE_WIDTH]:
        y = -offset
        while y < HEIGHT:
            pygame.draw.rect(surface, WHITE, (lane_x - 3, y, 6, dash_height))
            y += dash_height + gap


def ask_username():
    name = ""

    while True:
        screen.fill(DARK_GRAY)

        draw_text("Enter your name", font_big, WHITE, WIDTH // 2, 180, center=True)
        draw_text(name + "|", font_medium, YELLOW, WIDTH // 2, 260, center=True)
        draw_text("Press ENTER to start", font_small, WHITE, WIDTH // 2, 330, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip() == "":
                        return "Player"
                    return name

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    if len(name) < 12:
                        name += event.unicode

        pygame.display.update()
        clock.tick(FPS)


class Player(pygame.sprite.Sprite):
    def __init__(self, settings):
        super().__init__()

        self.width = 40
        self.height = 70
        self.settings = settings
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        color_name = settings.get("car_color", "blue")
        car_color = CAR_COLORS.get(color_name, BLUE)

        pygame.draw.rect(self.image, car_color, (0, 10, self.width, self.height - 20), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (5, 0, self.width - 10, 20), border_radius=6)
        pygame.draw.rect(self.image, BLACK, (5, self.height - 15, 10, 10), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (self.width - 15, self.height - 15, 10, 10), border_radius=3)

        self.rect = self.image.get_rect()
        self.rect.center = (lane_center(1), HEIGHT - 90)
        self.move_speed = 6

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.move_ip(-self.move_speed, 0)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.move_ip(self.move_speed, 0)

        if self.rect.left < ROAD_LEFT + 5:
            self.rect.left = ROAD_LEFT + 5

        if self.rect.right > ROAD_RIGHT - 5:
            self.rect.right = ROAD_RIGHT - 5


class Enemy(pygame.sprite.Sprite):
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
        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-260, -90))

    def move(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > HEIGHT:
            self.reset_position()


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

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
        self.rect.center = (lane_center(lane), random.randint(-180, -50))

    def update(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > HEIGHT:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.kind = random.choice(["oil", "barrier", "pothole", "speed_bump"])

        self.image = pygame.Surface((55, 35), pygame.SRCALPHA)

        if self.kind == "oil":
            pygame.draw.ellipse(self.image, BLACK, (0, 5, 55, 25))

        elif self.kind == "barrier":
            pygame.draw.rect(self.image, ORANGE, (0, 5, 55, 25))
            pygame.draw.line(self.image, BLACK, (5, 5), (50, 30), 4)

        elif self.kind == "pothole":
            pygame.draw.ellipse(self.image, (30, 30, 30), (0, 2, 55, 30))

        elif self.kind == "speed_bump":
            pygame.draw.rect(self.image, YELLOW, (0, 10, 55, 15))
            pygame.draw.rect(self.image, BLACK, (0, 10, 55, 15), 2)

        self.rect = self.image.get_rect()

        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-250, -80))

    def update(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.kind = random.choice(["nitro", "shield", "repair"])
        self.created_time = time.time()

        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)

        if self.kind == "nitro":
            color = ORANGE
            letter = "N"
        elif self.kind == "shield":
            color = CYAN
            letter = "S"
        else:
            color = GREEN
            letter = "R"

        pygame.draw.rect(self.image, color, (0, 0, 36, 36), border_radius=8)
        pygame.draw.rect(self.image, BLACK, (0, 0, 36, 36), 2, border_radius=8)

        text = font_small.render(letter, True, BLACK)
        text_rect = text.get_rect(center=(18, 18))
        self.image.blit(text, text_rect)

        self.rect = self.image.get_rect()

        lane = random.randint(0, 2)
        self.rect.center = (lane_center(lane), random.randint(-220, -80))

    def update(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > HEIGHT:
            self.kill()

        if time.time() - self.created_time > 7:
            self.kill()


class Game:
    def __init__(self, username, settings):
        self.username = username
        self.settings = settings

        difficulty = settings.get("difficulty", "normal")

        if difficulty == "easy":
            self.enemy_speed = 4
            self.road_speed = 4
            self.enemy_count = 1

        elif difficulty == "hard":
            self.enemy_speed = 7
            self.road_speed = 7
            self.enemy_count = 3

        else:
            self.enemy_speed = 5
            self.road_speed = 5
            self.enemy_count = 2

        self.score = 0
        self.coins_collected = 0
        self.coin_points = 0
        self.distance = 0
        self.finish_distance = 3000

        self.road_offset = 0
        self.game_over = False
        self.saved_score = False

        self.active_power = None
        self.power_end_time = 0
        self.shield = False

        self.player = Player(settings)

        self.enemies = pygame.sprite.Group()
        for _ in range(self.enemy_count):
            self.enemies.add(Enemy())

        self.coins = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.enemies)

        self.spawn_coin_event = pygame.USEREVENT + 1
        self.spawn_obstacle_event = pygame.USEREVENT + 2
        self.spawn_powerup_event = pygame.USEREVENT + 3

        pygame.time.set_timer(self.spawn_coin_event, 1400)
        pygame.time.set_timer(self.spawn_obstacle_event, 2300)
        pygame.time.set_timer(self.spawn_powerup_event, 6500)

    def final_score(self):
        return int(self.score + self.coin_points * 10 + self.distance * 0.15)

    def activate_powerup(self, powerup):
        if self.active_power is not None:
            return

        if powerup.kind == "nitro":
            self.active_power = "Nitro"
            self.road_speed += 4
            self.enemy_speed += 2
            self.power_end_time = time.time() + 4

        elif powerup.kind == "shield":
            self.active_power = "Shield"
            self.shield = True

        elif powerup.kind == "repair":
            if len(self.obstacles) > 0:
                random.choice(self.obstacles.sprites()).kill()

    def update_powerup(self):
        if self.active_power == "Nitro":
            if time.time() > self.power_end_time:
                self.road_speed -= 4
                self.enemy_speed -= 2
                self.active_power = None

    def handle_collisions(self):
        enemy_hit = pygame.sprite.spritecollideany(self.player, self.enemies)

        if enemy_hit:
            if self.shield:
                enemy_hit.reset_position()
                self.shield = False
                self.active_power = None
            else:
                self.game_over = True

        obstacle_hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)

        for obstacle in obstacle_hits:
            if obstacle.kind == "oil":
                self.player.rect.x += random.choice([-35, 35])
                obstacle.kill()

            elif obstacle.kind == "speed_bump":
                self.road_speed = max(2, self.road_speed - 1)
                obstacle.kill()

            else:
                if self.shield:
                    obstacle.kill()
                    self.shield = False
                    self.active_power = None
                else:
                    self.game_over = True

        collected_coins = pygame.sprite.spritecollide(self.player, self.coins, True)

        for coin in collected_coins:
            self.coins_collected += 1
            self.coin_points += coin.weight
            self.score += coin.weight * 10

            if self.coins_collected % 5 == 0:
                self.enemy_speed += 1
                self.road_speed += 1

        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)

        for powerup in collected_powerups:
            self.activate_powerup(powerup)

    def spawn_coin(self):
        if len(self.coins) < 3:
            coin = Coin()
            self.coins.add(coin)
            self.all_sprites.add(coin)

    def spawn_obstacle(self):
        if len(self.obstacles) < 4:
            obstacle = Obstacle()

            if abs(obstacle.rect.centerx - self.player.rect.centerx) < 40:
                obstacle.rect.y -= 150

            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

    def spawn_powerup(self):
        if len(self.powerups) < 1:
            powerup = PowerUp()
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

    def draw_hud(self):
        remaining = max(0, int(self.finish_distance - self.distance))

        draw_text(f"Name: {self.username}", font_small, WHITE, 10, 10)
        draw_text(f"Score: {self.final_score()}", font_small, WHITE, 10, 35)
        draw_text(f"Coins: {self.coins_collected}", font_small, WHITE, 10, 60)
        draw_text(f"Distance: {int(self.distance)}m", font_small, WHITE, 10, 85)
        draw_text(f"Left: {remaining}m", font_small, WHITE, 10, 110)

        if self.active_power == "Nitro":
            left = max(0, int(self.power_end_time - time.time()))
            draw_text(f"Power: Nitro {left}s", font_small, YELLOW, 210, 10)

        elif self.active_power == "Shield":
            draw_text("Power: Shield", font_small, CYAN, 210, 10)

        else:
            draw_text("Power: None", font_small, WHITE, 210, 10)

        draw_text("N=nitro S=shield R=repair", font_small, WHITE, 170, 565)

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(WHITE)
        screen.blit(overlay, (0, 0))

        draw_text("Game Over", font_big, BLACK, WIDTH // 2, 190, center=True)
        draw_text(f"Score: {self.final_score()}", font_medium, BLACK, WIDTH // 2, 260, center=True)
        draw_text(f"Distance: {int(self.distance)}m", font_small, BLACK, WIDTH // 2, 305, center=True)
        draw_text(f"Coins: {self.coins_collected}", font_small, BLACK, WIDTH // 2, 335, center=True)
        draw_text("R - Retry", font_small, BLACK, WIDTH // 2, 390, center=True)
        draw_text("M - Main Menu", font_small, BLACK, WIDTH // 2, 420, center=True)
        draw_text("Q - Quit", font_small, BLACK, WIDTH // 2, 450, center=True)

    def save_result_once(self):
        if not self.saved_score:
            save_score(self.username, self.final_score(), self.distance)
            self.saved_score = True

    def run(self):
        running_game = True

        while running_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if not self.game_over:
                    if event.type == self.spawn_coin_event:
                        self.spawn_coin()

                    if event.type == self.spawn_obstacle_event:
                        self.spawn_obstacle()

                    if event.type == self.spawn_powerup_event:
                        self.spawn_powerup()

                if event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_r:
                        return "retry"

                    elif event.key == pygame.K_m:
                        return "menu"

                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

            if not self.game_over:
                self.player.move()

                for enemy in self.enemies:
                    enemy.move(self.enemy_speed)

                for coin in self.coins:
                    coin.update(self.road_speed)

                for obstacle in self.obstacles:
                    obstacle.update(self.road_speed)

                for powerup in self.powerups:
                    powerup.update(self.road_speed)

                self.handle_collisions()
                self.update_powerup()

                self.distance += self.road_speed * 0.25
                self.score += 0.05

                if self.distance >= self.finish_distance:
                    self.game_over = True

                self.road_offset = (self.road_offset + self.road_speed) % 50

            else:
                self.save_result_once()

            draw_road(screen, self.road_offset)

            for sprite in self.all_sprites:
                screen.blit(sprite.image, sprite.rect)

            if self.shield:
                pygame.draw.circle(screen, CYAN, self.player.rect.center, 45, 3)

            self.draw_hud()

            if self.game_over:
                self.draw_game_over()

            pygame.display.update()
            clock.tick(FPS)


def main_menu():
    play_btn = pygame.Rect(110, 210, 180, 45)
    leaderboard_btn = pygame.Rect(110, 270, 180, 45)
    settings_btn = pygame.Rect(110, 330, 180, 45)
    quit_btn = pygame.Rect(110, 390, 180, 45)

    while True:
        screen.fill(DARK_GRAY)

        draw_text("Racer Game", font_big, WHITE, WIDTH // 2, 120, center=True)

        draw_button(play_btn, "Play")
        draw_button(leaderboard_btn, "Leaderboard")
        draw_button(settings_btn, "Settings")
        draw_button(quit_btn, "Quit")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    username = ask_username()
                    settings = load_settings()

                    while True:
                        game = Game(username, settings)
                        result = game.run()

                        if result == "retry":
                            continue
                        else:
                            break

                elif leaderboard_btn.collidepoint(event.pos):
                    leaderboard_screen()

                elif settings_btn.collidepoint(event.pos):
                    settings_screen()

                elif quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(FPS)


def leaderboard_screen():
    back_btn = pygame.Rect(110, 530, 180, 45)

    while True:
        screen.fill(DARK_GRAY)

        draw_text("Leaderboard", font_big, WHITE, WIDTH // 2, 60, center=True)

        leaderboard = load_leaderboard()

        if not leaderboard:
            draw_text("No scores yet", font_medium, WHITE, WIDTH // 2, 250, center=True)

        y = 120

        for i, item in enumerate(leaderboard[:10], start=1):
            text = f"{i}. {item['name']} | {item['score']} | {item['distance']}m"
            draw_text(text, font_small, WHITE, 35, y)
            y += 35

        draw_button(back_btn, "Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return

        pygame.display.update()
        clock.tick(FPS)


def settings_screen():
    settings = load_settings()

    sound_btn = pygame.Rect(80, 180, 240, 45)
    color_btn = pygame.Rect(80, 250, 240, 45)
    difficulty_btn = pygame.Rect(80, 320, 240, 45)
    back_btn = pygame.Rect(110, 500, 180, 45)

    colors = ["blue", "red", "green", "purple"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill(DARK_GRAY)

        draw_text("Settings", font_big, WHITE, WIDTH // 2, 90, center=True)

        draw_button(sound_btn, f"Sound: {'On' if settings['sound'] else 'Off'}")
        draw_button(color_btn, f"Color: {settings['car_color']}")
        draw_button(difficulty_btn, f"Difficulty: {settings['difficulty']}")
        draw_button(back_btn, "Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                elif color_btn.collidepoint(event.pos):
                    index = colors.index(settings["car_color"])
                    settings["car_color"] = colors[(index + 1) % len(colors)]
                    save_settings(settings)

                elif difficulty_btn.collidepoint(event.pos):
                    index = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                    save_settings(settings)

                elif back_btn.collidepoint(event.pos):
                    return

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()