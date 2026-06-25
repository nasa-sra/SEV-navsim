import pygame
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import colors
import math

# pygame.draw.arc(surface, color, rect, start_angle, stop_angle, width=1)

class GuiScreen:
    
    def __init__(self, screen):
        
        self.screen = screen
        self.slider = Slider(screen, 50, 600, 400, 10, min=-100, max=100, step=1)
        self.output = TextBox(screen, 250, 650, 75, 50, fontSize=20)
        self.output.disable()

        self.joystick_image = pygame.image.load(
            "logitech.jpg"
        ).convert_alpha()
        
        width = self.joystick_image.get_width()
        height = self.joystick_image.get_height()

        scale = 0.25

        self.joystick_image = pygame.transform.scale(
            self.joystick_image,
            (int(width * scale), int(height * scale))
        )

    def handle_event(self,event):
        pass

    def update(self,dt):
        pass
    
    def setText(self):
        self.output.setText(str(self.slider.getValue()) + "%")

    def draw(self):

        self.screen.fill((255,255,255))
        
        mag = self.slider.getValue()
        angle = math.pi/2 - abs((mag / 100) * math.pi/2)

        pygame.draw.arc(self.screen, colors.RED, (100, 150, 300, 300), angle, math.pi - angle, width=3)
        
        y = abs(self.slider.getValue()) + 300
        pygame.draw.line(self.screen, colors.BLUE, (1000, y), (1000, 600 - y), width = 3)

        self.screen.blit(
            self.joystick_image,
            (425,125)
        )