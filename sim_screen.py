import pygame
import math
import button
import waypoints
import vehicle
import virtual_joystick
import colors
import stanley_controller
import display_text


class SimScreen:

    def __init__(self, screen):

        self.screen = screen

        pygame.joystick.init()

        self.useJoystick = pygame.joystick.get_count() > 0

        self.deadband = 0.1
        self.xValue = 0
        self.yValue = 0
        self.cte = 0

        self.autoMode = False
        self.targetSpeed = 150

        if self.useJoystick:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.SEV = vehicle.Vehicle()

        self.reset_button = button.Button(
            colors.RED,
            colors.DARK_RED,
            900,
            50,
            150,
            50,
            "RESET",
            self.reset_sim
        )

        self.addWaypoint_button = button.Button(
            colors.BLUE,
            colors.DARK_BLUE,
            900,
            100,
            75,
            50,
            "+WP",
            waypoints.addWayPoint
        )

        self.removeWaypoint_button = button.Button(
            colors.BLUE,
            colors.DARK_BLUE,
            975,
            100,
            75,
            50,
            "-WP",
            waypoints.removeWaypoint
        )

        self.start_button = button.Button(
            colors.GREEN,
            (0, 150, 0),
            900,
            160,
            75,
            50,
            "START",
            self.start_autonomous
        )

        self.stop_button = button.Button(
            colors.RED,
            colors.DARK_RED,
            975,
            160,
            75,
            50,
            "STOP",
            self.stop_autonomous
        )

        self.vJoystick = virtual_joystick.VirtualJoystick(
            900,
            500
        )

        self.stanleyJoystick = virtual_joystick.VirtualJoystick(
            1100,
            500
        )

        self.stanleyController = (
            stanley_controller.StanleyController()
        )

        self.steeringDisplay = display_text.Text(
            "",
            700,
            150
        )
        
        self.headingDisplay = display_text.Text(
            "",
            700,
            200
        )

        self.cteDisplay = display_text.Text(
            "",
            700,
            250
        )

        self.closestPoint = pygame.Vector2(0, 0)

        self.reset_sim()

    def start_autonomous(self):
        self.autoMode = True

    def stop_autonomous(self):
        self.autoMode = False

    def reset_sim(self):

        self.SEV.heading = 0
        self.SEV.accel = pygame.Vector2(0, 0)
        self.SEV.vel = pygame.Vector2(0, 0)
        self.SEV.pos = pygame.Vector2(200, 200)
        self.SEV.dims = pygame.Vector2(50, 30)

        if hasattr(self.SEV, "speed"):
            self.SEV.speed = 0

        self.autoMode = False

        waypoints.resetWaypoints()

    def handle_event(self, event):

        if (
            self.useJoystick
            and event.type == pygame.JOYAXISMOTION
        ):
            self.xValue = self.joystick.get_axis(0)
            self.yValue = self.joystick.get_axis(1)

            self.vJoystick.moveKnob(
                self.xValue * 25,
                self.yValue * 25
            )

        self.reset_button.handle_event(event)
        self.addWaypoint_button.handle_event(event)
        self.removeWaypoint_button.handle_event(event)

        self.start_button.handle_event(event)
        self.stop_button.handle_event(event)

        waypoints.handle_event(event)

    def follow_waypoints(self, dt):

        wps = waypoints.getWaypoints()
        
        last_wp_coords = wps[-1].getCenter()
        
        if(self.closestPoint == last_wp_coords and self.SEV.pos.distance_to(last_wp_coords) < 150):
            self.autoMode = False
            return

        if len(wps) < 2:
            return

        wpIndex = 0

        self.closestPoint = pygame.Vector2(
            10000,
            10000
        )

        for i in range(len(wps) - 1):

            curPoint = (
                self.stanleyController
                .closest_point_on_segment(
                    self.SEV.pos,
                    wps[i].getCenter(),
                    wps[i + 1].getCenter()
                )
            )

            if (
                self.closestPoint.distance_to(self.SEV.pos)
                >
                curPoint.distance_to(self.SEV.pos)
            ):
                self.closestPoint = curPoint
                wpIndex = i

        steering = self.stanleyController.steering(
            self.SEV.pos,
            self.SEV.heading,
            self.SEV.speed,
            wps[wpIndex],
            wps[wpIndex + 1]
        )

        steering = max(
            -100,
            min(100, steering)
        )

        speedError = (
            self.targetSpeed
            - self.SEV.speed
        )

        throttle = speedError * 3

        throttle = max(
            -250,
            min(250, throttle)
        )

        self.SEV.speed += throttle * dt

        drag = 2.0
        self.SEV.speed -= (
            self.SEV.speed * drag * dt
        )

        self.SEV.heading += steering * 0.4 * dt

        heading_rad = math.radians(
            self.SEV.heading
        )

        self.SEV.pos.x += (
            math.cos(heading_rad)
            * self.SEV.speed
            * dt
        )

        self.SEV.pos.y += (
            math.sin(heading_rad)
            * self.SEV.speed
            * dt
        )

    def update(self, dt):

        if self.autoMode:
            self.follow_waypoints(dt)
        else:

            keys = pygame.key.get_pressed()

            throttle = 0
            steering = 0

            if keys[pygame.K_w]:
                throttle = 250

            elif keys[pygame.K_s]:
                throttle = -250

            elif self.useJoystick:
                y = (
                    0
                    if abs(self.yValue)
                    < self.deadband
                    else self.yValue
                )

                throttle = -y * 250

            if keys[pygame.K_a]:
                steering = -100

            elif keys[pygame.K_d]:
                steering = 100

            elif self.useJoystick:
                x = (
                    0
                    if abs(self.xValue)
                    < self.deadband
                    else self.xValue
                )

                steering = x * 100

            self.SEV.speed += throttle * dt

            drag = 2.0
            self.SEV.speed -= (
                self.SEV.speed * drag * dt
            )

            self.SEV.heading += steering * dt

            heading_rad = math.radians(
                self.SEV.heading
            )

            self.SEV.pos.x += (
                math.cos(heading_rad)
                * self.SEV.speed
                * dt
            )

            self.SEV.pos.y += (
                math.sin(heading_rad)
                * self.SEV.speed
                * dt
            )

        wps = waypoints.getWaypoints()

        if len(wps) >= 2:

            wpIndex = 0

            self.closestPoint = pygame.Vector2(
                10000,
                10000
            )

            for i in range(len(wps) - 1):

                curPoint = (
                    self.stanleyController
                    .closest_point_on_segment(
                        self.SEV.pos,
                        wps[i].getCenter(),
                        wps[i + 1].getCenter()
                    )
                )

                if (
                    self.closestPoint.distance_to(self.SEV.pos)
                    >
                    curPoint.distance_to(self.SEV.pos)
                ):
                    self.closestPoint = curPoint
                    wpIndex = i

            desired = round(
                self.stanleyController.steering(
                    self.SEV.pos,
                    self.SEV.heading,
                    self.SEV.speed,
                    wps[wpIndex],
                    wps[wpIndex + 1]
                ),
                2
            )

            self.cte = round(
                self.stanleyController.compute_cte(
                    self.SEV.pos,
                    wps[wpIndex].getCenter(),
                    wps[wpIndex + 1].getCenter()
                ),
                2
            )

            self.steeringDisplay.updateText(
                f"desired steering: {desired}"
            )

            self.cteDisplay.updateText(
                f"current CTE: {self.cte}"
            )
            
            self.headingDisplay.updateText(
                f"current heading: {round(self.SEV.heading, 2)}"
            )

    def draw(self):

        self.screen.fill("black")

        self.reset_button.draw(self.screen)
        self.addWaypoint_button.draw(self.screen)
        self.removeWaypoint_button.draw(self.screen)

        self.start_button.draw(self.screen)
        self.stop_button.draw(self.screen)

        waypoints.draw(self.screen)

        self.vJoystick.draw(self.screen)
        self.stanleyJoystick.draw(self.screen)

        self.steeringDisplay.display(self.screen)
        self.cteDisplay.display(self.screen)
        self.headingDisplay.display(self.screen)

        vehicle_surface = pygame.Surface(
            (
                self.SEV.dims.x,
                self.SEV.dims.y
            ),
            pygame.SRCALPHA
        )

        vehicle_surface.fill("white")

        pygame.draw.polygon(
            vehicle_surface,
            "red",
            [
                (self.SEV.dims.x,
                 self.SEV.dims.y / 2),

                (self.SEV.dims.x - 12,
                 5),

                (self.SEV.dims.x - 12,
                 self.SEV.dims.y - 5)
            ]
        )

        rotated_vehicle = pygame.transform.rotate(
            vehicle_surface,
            -self.SEV.heading
        )

        rect = rotated_vehicle.get_rect(
            center=self.SEV.pos
        )

        self.screen.blit(
            rotated_vehicle,
            rect
        )

        pygame.draw.line(
            self.screen,
            colors.WHITE,
            self.closestPoint,
            self.SEV.pos,
            1
        )