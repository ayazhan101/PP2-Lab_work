import pygame
import random
import sys
import json
import os

from db import save_game_result, get_top_10, get_personal_best


pygame.init()

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20

COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
YELLOW = (255, 215, 0)
PURPLE = (170, 0, 170)
GRAY = (90, 90, 90)
BLUE = (0, 120, 255)
CYAN = (0, 220, 220)
ORANGE = (255, 140, 0)
BROWN = (130, 70, 30)

FOOD_LIFETIME = 5000
POWERUP_LIFETIME = 8000

BASE_SPEED = 8
LEVEL_FOOD_COUNT = 3

SETTINGS_FILE = "settings.json"


def load_settings():
    default_settings = {
        "snake_color": [0, 180, 0],
        "grid": True,
        "sound": True
    }

    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as file:
            json.dump(default_settings, file, indent=4)
        return default_settings

    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, font):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Snake:
    def __init__(self):
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.grow_by = 0

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction

        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)

        if self.grow_by > 0:
            self.grow_by -= 1
        else:
            self.body.pop()

    def change_direction(self, new_direction):
        current_x, current_y = self.direction
        new_x, new_y = new_direction

        if (current_x + new_x, current_y + new_y) != (0, 0):
            self.direction = new_direction

    def shorten(self, amount):
        for _ in range(amount):
            if len(self.body) > 1:
                self.body.pop()

    def draw(self, screen, snake_color):
        for index, segment in enumerate(self.body):
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            if index == 0:
                pygame.draw.rect(screen, DARK_GREEN, rect)
            else:
                pygame.draw.rect(screen, snake_color, rect)

            pygame.draw.rect(screen, BLACK, rect, 1)


class Food:
    def __init__(self, snake_body, obstacles):
        self.weight = random.choice([1, 2, 3])

        if self.weight == 1:
            self.color = RED
        elif self.weight == 2:
            self.color = YELLOW
        else:
            self.color = PURPLE

        self.position = self.generate_position(snake_body, obstacles)
        self.spawn_time = pygame.time.get_ticks()

    def generate_position(self, snake_body, obstacles):
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)

            if (x, y) not in snake_body and (x, y) not in obstacles:
                return (x, y)

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > FOOD_LIFETIME

    def draw(self, screen, small_font):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

        text = small_font.render(str(self.weight), True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)


class PoisonFood:
    def __init__(self, snake_body, obstacles):
        self.position = self.generate_position(snake_body, obstacles)

    def generate_position(self, snake_body, obstacles):
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)

            if (x, y) not in snake_body and (x, y) not in obstacles:
                return (x, y)

    def draw(self, screen):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        pygame.draw.rect(screen, DARK_RED, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)


class PowerUp:
    TYPES = ["speed", "slow", "shield"]

    def __init__(self, snake_body, obstacles, food_pos, poison_pos):
        self.type = random.choice(self.TYPES)
        self.position = self.generate_position(
            snake_body,
            obstacles,
            food_pos,
            poison_pos
        )
        self.spawn_time = pygame.time.get_ticks()

    def generate_position(self, snake_body, obstacles, food_pos, poison_pos):
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            pos = (x, y)

            if (
                pos not in snake_body
                and pos not in obstacles
                and pos != food_pos
                and pos != poison_pos
            ):
                return pos

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_LIFETIME

    def draw(self, screen, small_font):
        if self.type == "speed":
            color = ORANGE
            label = "S"
        elif self.type == "slow":
            color = CYAN
            label = "L"
        else:
            color = BLUE
            label = "H"

        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

        text = small_font.render(label, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TSIS4 Snake Game")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Verdana", 24)
        self.small_font = pygame.font.SysFont("Verdana", 16)
        self.big_font = pygame.font.SysFont("Verdana", 44)

        self.settings = load_settings()

        self.username = ""
        self.screen_state = "menu"

        self.snake = None
        self.food = None
        self.poison = None
        self.powerup = None

        self.score = 0
        self.level = 1
        self.eaten_count = 0
        self.speed = BASE_SPEED
        self.personal_best = 0

        self.obstacles = []

        self.active_power = None
        self.power_end_time = 0
        self.shield_active = False

        self.result_saved = False

    def run(self):
        while True:
            if self.screen_state == "menu":
                self.main_menu()
            elif self.screen_state == "game":
                self.game_loop()
            elif self.screen_state == "leaderboard":
                self.leaderboard_screen()
            elif self.screen_state == "settings":
                self.settings_screen()
            elif self.screen_state == "game_over":
                self.game_over_screen()

    def reset_game(self):
        self.snake = Snake()
        self.obstacles = []
        self.score = 0
        self.level = 1
        self.eaten_count = 0
        self.speed = BASE_SPEED

        self.active_power = None
        self.power_end_time = 0
        self.shield_active = False

        self.food = Food(self.snake.body, self.obstacles)
        self.poison = PoisonFood(self.snake.body, self.obstacles)
        self.powerup = None

        self.result_saved = False

        if self.username.strip():
            self.personal_best = get_personal_best(self.username)

    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))

        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

    def draw_text_center(self, text, font, color, y):
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(text_surface, rect)

    def main_menu(self):
        play_button = Button(200, 250, 200, 45, "Play")
        leaderboard_button = Button(200, 310, 200, 45, "Leaderboard")
        settings_button = Button(200, 370, 200, 45, "Settings")
        quit_button = Button(200, 430, 200, 45, "Quit")

        while self.screen_state == "menu":
            self.screen.fill(BLACK)

            self.draw_text_center("Snake Game", self.big_font, GREEN, 80)
            self.draw_text_center("Enter username:", self.font, WHITE, 150)

            username_text = self.font.render(self.username, True, YELLOW)
            self.screen.blit(username_text, (WIDTH // 2 - username_text.get_width() // 2, 185))

            play_button.draw(self.screen, self.font)
            leaderboard_button.draw(self.screen, self.font)
            settings_button.draw(self.screen, self.font)
            quit_button.draw(self.screen, self.font)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.username.strip():
                            self.reset_game()
                            self.screen_state = "game"
                    else:
                        if len(self.username) < 15 and event.unicode.isprintable():
                            self.username += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    if play_button.is_clicked(pos):
                        if self.username.strip():
                            self.reset_game()
                            self.screen_state = "game"

                    elif leaderboard_button.is_clicked(pos):
                        self.screen_state = "leaderboard"

                    elif settings_button.is_clicked(pos):
                        self.screen_state = "settings"

                    elif quit_button.is_clicked(pos):
                        pygame.quit()
                        sys.exit()

            self.clock.tick(30)

    def generate_obstacles(self):
        self.obstacles = []

        if self.level < 3:
            return

        obstacle_count = self.level + 2
        snake_head = self.snake.body[0]

        safe_zone = [
            snake_head,
            (snake_head[0] + 1, snake_head[1]),
            (snake_head[0] - 1, snake_head[1]),
            (snake_head[0], snake_head[1] + 1),
            (snake_head[0], snake_head[1] - 1)
        ]

        while len(self.obstacles) < obstacle_count:
            x = random.randint(1, COLS - 2)
            y = random.randint(1, ROWS - 2)
            pos = (x, y)

            if (
                pos not in self.snake.body
                and pos not in safe_zone
                and pos != self.food.position
                and pos != self.poison.position
            ):
                self.obstacles.append(pos)

    def check_collision(self):
        head_x, head_y = self.snake.body[0]
        head = self.snake.body[0]

        wall_collision = (
            head_x < 0 or head_x >= COLS or head_y < 0 or head_y >= ROWS
        )
        self_collision = head in self.snake.body[1:]
        obstacle_collision = head in self.obstacles

        if wall_collision or self_collision:
            if self.shield_active:
                self.shield_active = False
                return False
            return True

        if obstacle_collision:
            return True

        return False

    def activate_powerup(self, power_type):
        current_time = pygame.time.get_ticks()

        if power_type == "speed":
            self.active_power = "speed"
            self.power_end_time = current_time + 5000
            self.speed = BASE_SPEED + self.level * 2 + 5

        elif power_type == "slow":
            self.active_power = "slow"
            self.power_end_time = current_time + 5000
            self.speed = max(4, BASE_SPEED + self.level - 4)

        elif power_type == "shield":
            self.shield_active = True

    def update_powerup_effect(self):
        current_time = pygame.time.get_ticks()

        if self.active_power in ["speed", "slow"]:
            if current_time > self.power_end_time:
                self.active_power = None
                self.speed = BASE_SPEED + self.level

    def maybe_spawn_powerup(self):
        if self.powerup is None:
            chance = random.randint(1, 100)
            if chance <= 2:
                self.powerup = PowerUp(
                    self.snake.body,
                    self.obstacles,
                    self.food.position,
                    self.poison.position
                )

    def draw_obstacles(self):
        for pos in self.obstacles:
            x, y = pos
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, BROWN, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_hud(self):
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        best_text = self.small_font.render(f"Best: {self.personal_best}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 35))
        self.screen.blit(best_text, (10, 60))

        time_left_ms = FOOD_LIFETIME - (pygame.time.get_ticks() - self.food.spawn_time)
        time_left_sec = max(0, time_left_ms // 1000)

        timer_text = self.small_font.render(f"Food timer: {time_left_sec}", True, WHITE)
        self.screen.blit(timer_text, (400, 10))

        shield_text = self.small_font.render(
            f"Shield: {'ON' if self.shield_active else 'OFF'}",
            True,
            WHITE
        )
        self.screen.blit(shield_text, (400, 35))

        if self.active_power:
            power_text = self.small_font.render(f"Power: {self.active_power}", True, WHITE)
            self.screen.blit(power_text, (400, 60))

    def game_loop(self):
        while self.screen_state == "game":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction((1, 0))
                    elif event.key == pygame.K_ESCAPE:
                        self.screen_state = "menu"

            self.snake.move()

            if self.check_collision():
                self.screen_state = "game_over"
                break

            if self.food.is_expired():
                self.food = Food(self.snake.body, self.obstacles)

            if self.snake.body[0] == self.food.position:
                self.score += self.food.weight
                self.snake.grow_by += self.food.weight
                self.eaten_count += 1

                if self.eaten_count % LEVEL_FOOD_COUNT == 0:
                    self.level += 1
                    self.speed = BASE_SPEED + self.level
                    self.generate_obstacles()

                self.food = Food(self.snake.body, self.obstacles)

            if self.snake.body[0] == self.poison.position:
                self.snake.shorten(2)
                self.poison = PoisonFood(self.snake.body, self.obstacles)

                if len(self.snake.body) <= 1:
                    self.screen_state = "game_over"
                    break

            self.maybe_spawn_powerup()

            if self.powerup:
                if self.powerup.is_expired():
                    self.powerup = None
                elif self.snake.body[0] == self.powerup.position:
                    self.activate_powerup(self.powerup.type)
                    self.powerup = None

            self.update_powerup_effect()

            self.screen.fill(BLACK)

            if self.settings["grid"]:
                self.draw_grid()

            self.draw_obstacles()
            self.snake.draw(self.screen, tuple(self.settings["snake_color"]))
            self.food.draw(self.screen, self.small_font)
            self.poison.draw(self.screen)

            if self.powerup:
                self.powerup.draw(self.screen, self.small_font)

            self.draw_hud()

            pygame.display.update()
            self.clock.tick(self.speed)

    def game_over_screen(self):
        if not self.result_saved:
            save_game_result(self.username, self.score, self.level)
            self.personal_best = max(self.personal_best, self.score)
            self.result_saved = True

        retry_button = Button(180, 360, 240, 45, "Retry")
        menu_button = Button(180, 420, 240, 45, "Main Menu")

        while self.screen_state == "game_over":
            self.screen.fill(BLACK)

            self.draw_text_center("Game Over", self.big_font, RED, 120)
            self.draw_text_center(f"Final Score: {self.score}", self.font, WHITE, 200)
            self.draw_text_center(f"Level Reached: {self.level}", self.font, WHITE, 240)
            self.draw_text_center(f"Personal Best: {self.personal_best}", self.font, YELLOW, 280)

            retry_button.draw(self.screen, self.font)
            menu_button.draw(self.screen, self.font)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    if retry_button.is_clicked(pos):
                        self.reset_game()
                        self.screen_state = "game"

                    elif menu_button.is_clicked(pos):
                        self.screen_state = "menu"

            self.clock.tick(30)

    def leaderboard_screen(self):
        back_button = Button(200, 530, 200, 45, "Back")

        try:
            rows = get_top_10()
        except Exception:
            rows = []

        while self.screen_state == "leaderboard":
            self.screen.fill(BLACK)
            self.draw_text_center("Leaderboard", self.big_font, YELLOW, 60)

            headers = self.small_font.render("Rank   Username        Score   Level   Date", True, WHITE)
            self.screen.blit(headers, (40, 120))

            y = 160

            if not rows:
                text = self.font.render("No records or database error", True, RED)
                self.screen.blit(text, (120, 250))
            else:
                for index, row in enumerate(rows, start=1):
                    username, score, level, played_at = row
                    date_text = played_at.strftime("%Y-%m-%d")

                    line = f"{index:<5} {username:<14} {score:<7} {level:<6} {date_text}"
                    text = self.small_font.render(line, True, WHITE)
                    self.screen.blit(text, (40, y))
                    y += 32

            back_button.draw(self.screen, self.font)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.is_clicked(pygame.mouse.get_pos()):
                        self.screen_state = "menu"

            self.clock.tick(30)

    def settings_screen(self):
        grid_button = Button(170, 180, 260, 45, "Toggle Grid")
        sound_button = Button(170, 240, 260, 45, "Toggle Sound")
        color_button = Button(170, 300, 260, 45, "Change Color")
        save_button = Button(170, 430, 260, 45, "Save & Back")

        colors = [
            [0, 180, 0],
            [255, 0, 0],
            [0, 120, 255],
            [255, 215, 0],
            [170, 0, 170]
        ]

        color_index = 0

        while self.screen_state == "settings":
            self.screen.fill(BLACK)

            self.draw_text_center("Settings", self.big_font, WHITE, 70)

            grid_status = "ON" if self.settings["grid"] else "OFF"
            sound_status = "ON" if self.settings["sound"] else "OFF"

            grid_text = self.font.render(f"Grid: {grid_status}", True, WHITE)
            sound_text = self.font.render(f"Sound: {sound_status}", True, WHITE)
            color_text = self.font.render(
                f"Snake Color: {self.settings['snake_color']}",
                True,
                WHITE
            )

            self.screen.blit(grid_text, (190, 130))
            self.screen.blit(sound_text, (190, 150 + 45))
            self.screen.blit(color_text, (120, 360))

            grid_button.draw(self.screen, self.font)
            sound_button.draw(self.screen, self.font)
            color_button.draw(self.screen, self.font)
            save_button.draw(self.screen, self.font)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    if grid_button.is_clicked(pos):
                        self.settings["grid"] = not self.settings["grid"]

                    elif sound_button.is_clicked(pos):
                        self.settings["sound"] = not self.settings["sound"]

                    elif color_button.is_clicked(pos):
                        color_index = (color_index + 1) % len(colors)
                        self.settings["snake_color"] = colors[color_index]

                    elif save_button.is_clicked(pos):
                        save_settings(self.settings)
                        self.screen_state = "menu"

            self.clock.tick(30)