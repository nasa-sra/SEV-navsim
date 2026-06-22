import pygame

class GuiScreen:

    def __init__(self, screen):

        self.screen = screen

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

    def draw(self):

        self.screen.fill((255,255,255))

        self.screen.blit(
            self.joystick_image,
            (425,125)
        )