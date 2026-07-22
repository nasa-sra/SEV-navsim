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
        
        self.throttle = 0
        self.twist = 0
        
        pygame.joystick.init()
        
        self.useJoystick = pygame.joystick.get_count() > 0
        
        if self.useJoystick:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            print("No joystick detected. Please connect your Extreme 3D Pro.")


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
        self.steps = None
        self.coord_font = pygame.font.SysFont(None, 28)
        
        self.gps_latitude = 0
        self.gps_longitude = 0

    def handle_event(self, event):
        if (
            self.useJoystick
            and event.type == pygame.JOYAXISMOTION
        ):
            self.throttle = self.joystick.get_axis(1)
            self.twist = self.joystick.get_axis(2)       
    
    def update(self, dt):
        pass

    def setText(self):
        self.output.setText(str(self.slider.getValue()) + "%")

    def set_waypoints(self, start_waypoint, end_waypoint):
        self.start_waypoint = start_waypoint
        self.end_waypoint = end_waypoint

    def set_route(self, route):
        if route:
            self.route = route.get('geometry')
            self.steps = route.get('steps')
            
    def set_geoposition(self, gps_lat, gps_long):
        self.gps_latitude = gps_lat
        self.gps_longitude = gps_long
        
    def draw_geoposition(self):
        if self.gps_latitude is None or self.gps_longitude is None:
            text = "Vnav Coords -> Waiting for GPS..."
        else:
            text = f"Vnav Coords ->: Lat {self.gps_latitude:.6f}   Lon: {self.gps_longitude:.6f}"

        surface = self.coord_font.render(text, True, (0, 0, 0))
        self.screen.blit(surface, (50, 230))

    def draw(self):

        self.screen.fill((255, 255, 255))
        self.screen.blit(self.joystick_image, (425, 125))

        twist_mag = self.slider.getValue() if not self.useJoystick else self.twist * 100
        throttle_mag = self.slider.getValue() if not self.useJoystick else -self.throttle * 100
        angle = math.pi / 2 - abs((twist_mag / 100) * math.pi / 2)

        pygame.draw.arc(self.screen, colors.RED, (515, 40, 300, 300), angle, math.pi - angle, width=3)

        arc_center = (515 + 150, 40 + 150)
        arc_radius = 150

        def point_on_arc(theta):
            return (
                arc_center[0] + arc_radius * math.cos(theta),
                arc_center[1] - arc_radius * math.sin(theta)
            )

        if twist_mag != 0:
            eps = 0.05  # small step back along the arc, toward its start
            if twist_mag > 0:
                tip = point_on_arc(angle)
                trailing = point_on_arc(angle + eps)
            else:
                tip = point_on_arc(math.pi - angle)
                trailing = point_on_arc(math.pi - angle - eps)

            dx, dy = tip[0] - trailing[0], tip[1] - trailing[1]
            direction_deg = math.degrees(math.atan2(dx, -dy))
            self.draw_arrowhead(tip, direction_deg, colors.RED)

        throttle_origin = (950, 360)
        throttle_length = 3 * abs(throttle_mag)
        throttle_dir_deg = 0 if throttle_mag >= 0 else 180
        throttle_tip = (
            throttle_origin[0],
            throttle_origin[1] - throttle_length if throttle_mag >= 0 else throttle_origin[1] + throttle_length
        )
        pygame.draw.line(self.screen, colors.BLUE, throttle_origin, throttle_tip, width=3)
        self.draw_arrowhead(throttle_tip, throttle_dir_deg, colors.BLUE)

        if self.start_waypoint:
            lat, lon = self.start_waypoint
            text = f"Start -> Lat: {lat:.6f}   Lon: {lon:.6f}"
            surface = self.coord_font.render(text, True, (0, 0, 0))
            self.screen.blit(surface, (50, 170))

        if self.end_waypoint:
            lat, lon = self.end_waypoint
            text = f"End -> Lat: {lat:.6f}   Lon: {lon:.6f}"
            surface = self.coord_font.render(text, True, (0, 0, 0))
            self.screen.blit(surface, (50, 200))

        if self.route or self.steps:
            instructions = self.generate_instructions()
            height = 300
            for index, inst in enumerate(instructions, start=1):
                surface = self.coord_font.render(f"{index}. {inst}", True, (0, 0, 0))
                self.screen.blit(surface, (50, height))
                height += 30

    def draw_arrowhead(self, tip, direction_deg, color, size=14):
        rad = math.radians(direction_deg)
        dx, dy = math.sin(rad), -math.cos(rad)
        px, py = -dy, dx

        base_x = tip[0] - dx * size
        base_y = tip[1] - dy * size

        left = (base_x + px * size * 0.5, base_y + py * size * 0.5)
        right = (base_x - px * size * 0.5, base_y - py * size * 0.5)

        pygame.draw.polygon(self.screen, color, [tip, left, right])

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

        if diff < 20 or diff > 340:
            return "Continue straight"
        if diff < 45:
            return "Slight right"
        if diff < 135:
            return "Turn right"
        if diff < 180:
            return "Sharp right"
        if diff <= 200:
            return "U-turn"
        if diff < 225:
            return "Sharp left"
        if diff < 315:
            return "Turn left"
        return "Slight left"

    def generate_instructions(self):
        if self.steps:
            return self._instructions_from_osrm_steps()
        return self._instructions_from_geometry()

    def _instructions_from_osrm_steps(self):
        instructions = []
        for step in self.steps:
            maneuver = step.get('instruction', '')
            modifier = step.get('modifier')
            name = step.get('name') or ""
            dist = int(step.get('distance_m', 0))

            if maneuver == 'depart':
                text = "Start"
                if name:
                    text += f" on {name}"
                text += f" and continue for {dist} meters"
            elif maneuver == 'arrive':
                text = "You have reached your destination"
            else:
                label = (modifier or maneuver).replace('_', ' ').capitalize()
                text = f"{label}"
                if name:
                    text += f" onto {name}"
                text += f", continue for {dist} meters"

            instructions.append(text)

        return instructions

    def _instructions_from_geometry(self):
        instructions = []
        prev_bearing = None
        last_turn = None
        instruction_distance = 0
        accumulated_distance = 0

        for i in range(len(self.route) - 1):
            a, b = self.route[i], self.route[i + 1]
            dist = self.haversine(a, b)
            brng = self.bearing(a, b)
            accumulated_distance += dist

            if prev_bearing is None:
                instruction_distance = accumulated_distance
                instructions.append(f"Start and continue for {int(instruction_distance)} meters")
                last_turn = "Start"
                accumulated_distance = 0
            else:
                turn = self.turn_direction(prev_bearing, brng)

                if turn == "Continue straight":
                    instruction_distance += accumulated_distance
                    instructions[-1] = f"{last_turn}, continue for {int(instruction_distance)} meters"
                    accumulated_distance = 0
                    prev_bearing = brng
                    continue

                instruction_distance = accumulated_distance
                instructions.append(f"{turn}, continue for {int(instruction_distance)} meters")
                last_turn = turn
                accumulated_distance = 0

            prev_bearing = brng

        instructions.append("You have reached your destination")
        return instructions