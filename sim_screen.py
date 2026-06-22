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

        self.cteDisplay = display_text.Text(
            "",
            700,
            250
        )

        self.closestPoint = pygame.Vector2(0, 0)

        self.reset_sim()

    def reset_sim(self):

        self.SEV.heading = 0
        self.SEV.accel = pygame.Vector2(0, 0)
        self.SEV.vel = pygame.Vector2(0, 0)
        self.SEV.pos = pygame.Vector2(200, 200)
        self.SEV.dims = pygame.Vector2(50, 30)

        if hasattr(self.SEV, "speed"):
            self.SEV.speed = 0

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

        waypoints.handle_event(event)

    def update(self, dt):

        keys = pygame.key.get_pressed()

        throttle = 0
        steering = 0

        if keys[pygame.K_w]:
            throttle = 250

        elif keys[pygame.K_s]:
            throttle = -250

        elif self.useJoystick:
            y = 0 if abs(self.yValue) < self.deadband else self.yValue
            throttle = -y * 250

        if keys[pygame.K_a]:
            steering = -80

        elif keys[pygame.K_d]:
            steering = 80

        elif self.useJoystick:
            x = 0 if abs(self.xValue) < self.deadband else self.xValue
            steering = x * 80

        self.SEV.speed += throttle * dt

        drag = 2.0
        self.SEV.speed -= self.SEV.speed * drag * dt

        self.SEV.heading += steering * dt

        heading_rad = math.radians(self.SEV.heading)

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

            cte = round(
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
                f"current CTE: {cte}"
            )

    def draw(self):

        self.screen.fill("black")

        self.reset_button.draw(self.screen)
        self.addWaypoint_button.draw(self.screen)
        self.removeWaypoint_button.draw(self.screen)

        waypoints.draw(self.screen)

        self.vJoystick.draw(self.screen)
        self.stanleyJoystick.draw(self.screen)

        self.steeringDisplay.display(self.screen)
        self.cteDisplay.display(self.screen)

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