import pygame
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import colors
import math

class GuiScreen:

    def __init__(self, screen):

        self.screen = screen
        self.slider = Slider(screen, 50, 600, 400, 10, min=-100, max=100, step=1)
        self.output = TextBox(screen, 250, 650, 75, 50, fontSize=20)
        self.output.disable()

        self.joystick_image = pygame.image.load("images/logitech.jpg").convert_alpha()

        width = self.joystick_image.get_width()
        height = self.joystick_image.get_height()
        scale = 0.25

        self.joystick_image = pygame.transform.scale(
            self.joystick_image,
            (int(width * scale), int(height * scale))
        )

        self.start_waypoint = None
        self.end_waypoint = None
        self.route = None
        self.coord_font = pygame.font.SysFont(None, 28)

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def setText(self):
        self.output.setText(str(self.slider.getValue()) + "%")

    # NEW: called from main.py each frame with the latest (lat, lon)
    def set_waypoints(self, start_waypoint, end_waypoint):
        self.start_waypoint = start_waypoint
        self.end_waypoint = end_waypoint
        
    def set_route(self, route):
        self.route = route['geometry']

    def draw(self):

        self.screen.fill((255, 255, 255))
        self.screen.blit(self.joystick_image, (425, 125))

        mag = self.slider.getValue()
        angle = math.pi / 2 - abs((mag / 100) * math.pi / 2)

        pygame.draw.arc(self.screen, colors.RED, (525, 40, 300, 300), angle, math.pi - angle, width=3)

        y = 1.5 * abs(self.slider.getValue()) + 360
        pygame.draw.line(self.screen, colors.BLUE, (1000, y), (1000, 720 - y), width=3)


        if self.start_waypoint:
            lat, lon = self.start_waypoint
            text = f"Start -> Lat: {lat:.6f}   Lon: {lon:.6f}"
            surface = self.coord_font.render(text, True, (0, 0, 0))
            self.screen.blit(surface, (75, 170))
            
        if self.end_waypoint:
            lat, lon = self.end_waypoint
            text = f"End -> Lat: {lat:.6f}   Lon: {lon:.6f}"
            surface = self.coord_font.render(text, True, (0, 0, 0))
            self.screen.blit(surface, (75, 200))
            
        if self.route:
            instructions = self.generate_instructions()
            text = ""
            height = 300
            index = 1
            for inst in instructions:
                surface = self.coord_font.render(f"{index}. {inst}", True, (0, 0, 0))
                self.screen.blit(surface, (75, height))
                height += 30
                index += 1
            

    def haversine(self, a, b):
        earth_radius = 6371000  # meters
        lat1, lon1 = math.radians(a[1]), math.radians(a[0])
        lat2, lon2 = math.radians(b[1]), math.radians(b[0])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        return 2 * earth_radius * math.asin(math.sqrt(h))

    def bearing(self, a, b):
        lat1, lon1 = math.radians(a[1]), math.radians(a[0])
        lat2, lon2 = math.radians(b[1]), math.radians(b[0])
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
        brng = math.degrees(math.atan2(x, y))
        return (brng + 360) % 360

    def turn_direction(self, prev, curr):
        diff = (curr - prev + 360) % 360

        if diff < 15 or diff > 345:
            return "Continue straight"
        if diff < 45:
            return "Slight right"
        if diff < 135:
            return "Turn right"
        if diff < 225:
            return "U-turn"
        if diff < 315:
            return "Turn left"
        return "Slight left"

    def generate_instructions(self):
        instructions = []
        prev_bearing = None

        for i in range(len(self.route)-1):
            a, b = self.route[i], self.route[i+1]
            dist = self.haversine(a, b)
            brng = self.bearing(a, b)

            if prev_bearing is None:
                instructions.append(f"Start and continue for {int(dist)} meters")
            else:
                turn = self.turn_direction(prev_bearing, brng)
                instructions.append(f"{turn}, continue for {int(dist)} meters")

            prev_bearing = brng

        instructions.append("You have reached your destination")
        return instructions
