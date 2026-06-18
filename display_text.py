import pygame
import colors

class Text:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(None, 36)

    def display(self, surface):
        text_surf = self.font.render(self.text, True, colors.WHITE)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)

    def updateText(self, text):
        self.text = text
