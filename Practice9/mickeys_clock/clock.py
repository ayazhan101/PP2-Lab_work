import pygame
import sys
import math
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 1400, 1050
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


import os
base_path = os.path.dirname(__file__)

mickey = pygame.image.load(os.path.join(base_path, "images", "mickey.png"))
right_hand = pygame.image.load(os.path.join(base_path, "images", "right_hand.png"))
left_hand = pygame.image.load(os.path.join(base_path, "images", "left_hand.png"))


center = (WIDTH // 2, HEIGHT // 2)

def rotate_hand(image, angle):
    rotated = pygame.transform.rotate(image, -angle)
    rect = rotated.get_rect(center=center)
    return rotated, rect

running = True
while running:
    clock.tick(60)  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = datetime.now()
    minutes = now.minute
    seconds = now.second


    minute_angle = minutes * 6
    second_angle = seconds * 6


    rotated_right, rect_right = rotate_hand(right_hand, minute_angle)
    rotated_left, rect_left = rotate_hand(left_hand, second_angle)

    screen.fill(WHITE)
    screen.blit(mickey, mickey.get_rect(center=center))
    screen.blit(rotated_right, rect_right)
    screen.blit(rotated_left, rect_left)

    pygame.display.flip()

pygame.quit()
sys.exit()