import pygame
import math
import button
import waypoints
import vehicle
import virtual_joystick
import colors
import stanley_controller

pygame.init()

pygame.joystick.init()
useJoystick = pygame.joystick.get_count() > 0

if useJoystick:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

else:
    print("No controller detected. Use WASD keys")



screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
deadband = 0.1
xValue = 0
yValue = 0

SEV = vehicle.Vehicle()

def reset_sim():
    SEV.heading = 0
    SEV.accel = pygame.Vector2(0, 0)
    SEV.vel = pygame.Vector2(0, 0)
    SEV.pos = pygame.Vector2(200, 200)
    SEV.dims = pygame.Vector2(50, 30)
    waypoints.resetWaypoints()

reset_button = button.Button(colors.RED, colors.DARK_RED, 900, 50, 150, 50, "RESET", reset_sim)
addWaypoint_button = button.Button(colors.BLUE, colors.DARK_BLUE, 900, 100, 75, 50, "+WP", waypoints.addWayPoint)
removeWaypoint_button = button.Button(colors.BLUE, colors.DARK_BLUE, 975, 100, 75, 50, "-WP", waypoints.removeWaypoint)
vJoystick = virtual_joystick.VirtualJoystick(900, 500)
stanleyJoystick = virtual_joystick.VirtualJoystick(1100, 500)
stanleyController = stanley_controller.StanleyController()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if useJoystick and event.type == pygame.JOYAXISMOTION:
            xValue = joystick.get_axis(0)
            yValue = joystick.get_axis(1)
            vJoystick.moveKnob(xValue * 25, yValue * 25)
        reset_button.handle_event(event)
        addWaypoint_button.handle_event(event)
        removeWaypoint_button.handle_event(event)
        waypoints.handle_event(event)
        
    screen.fill("black")
    reset_button.draw(screen)
    addWaypoint_button.draw(screen)
    removeWaypoint_button.draw(screen)
    waypoints.draw(screen)
    vJoystick.draw(screen)
    stanleyJoystick.draw(screen)
    
    vehicle_surface = pygame.Surface(
        (SEV.dims.x, SEV.dims.y),
        pygame.SRCALPHA
    )
    vehicle_surface.fill("white")

    # nose on SEV rectangle
    pygame.draw.polygon(
        vehicle_surface,
        "red",
        [
            (SEV.dims.x, SEV.dims.y / 2),
            (SEV.dims.x - 12, 5),
            (SEV.dims.x - 12, SEV.dims.y - 5)
        ]
    )

    rotated_vehicle = pygame.transform.rotate(
        vehicle_surface,
        -SEV.heading
    )

    rect = rotated_vehicle.get_rect(
        center=SEV.pos
    )

    screen.blit(rotated_vehicle, rect)

    keys = pygame.key.get_pressed()
    
    throttle = 0
    steering = 0

    if keys[pygame.K_w]:
        throttle = 250

    elif keys[pygame.K_s]:
        throttle = -250
        
    elif useJoystick:
        yValue = 0 if abs(yValue) < deadband else yValue 
        throttle = -yValue * 250

    if keys[pygame.K_a]:
        steering = -80

    elif keys[pygame.K_d]:
        steering = 80
        
    elif useJoystick:
        xValue = 0 if abs(xValue) < deadband else xValue 
        steering = xValue * 80
    
    SEV.speed += throttle * dt

    drag = 2.0
    SEV.speed -= SEV.speed * drag * dt


    SEV.heading += steering * dt
    heading_rad = math.radians(SEV.heading)

    forward_x = math.cos(heading_rad)
    forward_y = math.sin(heading_rad)
    
    SEV.pos.x += forward_x * SEV.speed * dt
    SEV.pos.y += forward_y * SEV.speed * dt
    
    wps = waypoints.getWaypoints()
    closestPoint = pygame.Vector2(10000, 10000)
    for i in range(len(wps)-1):
        curPoint = stanleyController.closest_point_on_segment(SEV.pos, wps[i].getCenter(), wps[i+1].getCenter())
        if(closestPoint.distance_to(SEV.pos) > curPoint.distance_to(SEV.pos)) : closestPoint = curPoint
        
    pygame.draw.line(screen, colors.WHITE, closestPoint, SEV.pos, 1)
        
    pygame.display.flip()

    # 60 FPS, dt is delta time in seconds since last frame (need to standardize across program)
    dt = clock.tick(60) / 1000

pygame.quit()