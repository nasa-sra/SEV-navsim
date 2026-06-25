import pygame
import pygame_widgets
import button
import colors

from sim_screen import SimScreen
from gui_screen import GuiScreen

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

sim_screen = SimScreen(screen)
gui_screen = GuiScreen(screen)

current_screen = sim_screen

def show_sim():
    global current_screen
    current_screen = sim_screen

def show_gui():
    global current_screen
    current_screen = gui_screen

left_button = button.Button(
    colors.BLUE,
    colors.DARK_BLUE,
    10,
    10,
    50,
    40,
    "<",
    show_sim
)

right_button = button.Button(
    colors.BLUE,
    colors.DARK_BLUE,
    70,
    10,
    50,
    40,
    ">",
    show_gui
)

nasa_logo = pygame.image.load(
    "nasa_logo.png"
).convert_alpha()

nasa_logo = pygame.transform.smoothscale(
    nasa_logo,
    (nasa_logo.get_width() * .1, nasa_logo.get_height() * .1)
)

running = True

while running:

    dt = clock.tick(60) / 1000

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        left_button.handle_event(event)
        right_button.handle_event(event)

        current_screen.handle_event(event)

    current_screen.update(dt)
    current_screen.draw()
    
    if(isinstance(current_screen, GuiScreen)): 
        current_screen.setText()
        pygame_widgets.update(events)
        pygame.display.update()
    
    screen.blit(
        nasa_logo,
        (1125, 25)   # top-right corner
    )

    left_button.draw(screen)
    right_button.draw(screen)

    pygame.display.flip()

pygame.quit()