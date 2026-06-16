import pygame

class Vehicle:
    def __init__(self):
        self.pos = pygame.Vector2(200, 200)
        self.dims = pygame.Vector2(50, 30)
        self.heading = 0
        self.speed = 0