import pygame
import colors

class VirtualJoystick:
    def __init__(self, x, y):
        self.outerX = x
        self.outerY = y
        self.knobX = x
        self.knobY = y
    
    def getKnobX(self): 
        return self.knobX
    
    def getKnobY(self): 
        return self.knobY
        
    def draw(self, screen):
        pygame.draw.circle(screen, colors.WHITE, (self.outerX, self.outerY), 80, 4)
        pygame.draw.circle(screen, colors.RED, (self.knobX, self.knobY), 35, 0)
        
    def moveKnob(self, x, y):
        self.knobX = self.outerX + x
        self.knobY = self.outerY + y
        
    