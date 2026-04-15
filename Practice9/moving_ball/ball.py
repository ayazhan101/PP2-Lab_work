import pygame


class Ball:
    def __init__(self, x, y, radius, screen_width, screen_height):
        self.x = x
        self.y = y
        self.radius = radius

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.color = (255, 0, 0)  
        self.speed = 20  # шаг движения

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move_up(self):
        if self.y - self.radius - self.speed >= 0:
            self.y -= self.speed

    def move_down(self):
        if self.y + self.radius + self.speed <= self.screen_height:
            self.y += self.speed

    def move_left(self):
        if self.x - self.radius - self.speed >= 0:
            self.x -= self.speed

    def move_right(self):
        if self.x + self.radius + self.speed <= self.screen_width:
            self.x += self.speed