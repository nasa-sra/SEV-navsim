import pygame
import colors

class VirtualJoystick:
    def __init__(self, x, y):
        self.outerX = x
        self.outerY = y
        self.knobX = x
        self.knobY = y
    
    def getX(self): 
        return self.outerX
    
    def getY(self): 
        return self.outerY
        
    def draw(self, screen):
        pygame.draw.circle(screen, colors.WHITE, (self.outerX, self.outerY), 80, 4)
        pygame.draw.circle(screen, colors.RED, (self.knobX, self.knobY), 35, 0)
        
    def moveKnob(self, x, y):
        self.knobX = self.outerX + x
        self.knobY = self.outerY + y
        
    