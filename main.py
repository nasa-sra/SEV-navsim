import pygame
import math
import button
import waypoints
import vehicle

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# to be implemented later:
# max_waypoints = 10
# min_waypoints = 3

SEV = vehicle.Vehicle()

def reset_all():
    SEV.heading = 0
    SEV.accel = pygame.Vector2(0, 0)
    SEV.friction = pygame.Vector2(0, 0)
    SEV.vel = pygame.Vector2(0, 0)
    SEV.pos = pygame.Vector2(200, 200)
    SEV.dims = pygame.Vector2(50, 30)

reset_button = button.Button(button.RED, button.DARK_RED, 900, 50, 150, 50, "RESET", reset_all)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        reset_button.handle_event(event)
        waypoints.handle_event(event)
        
    screen.fill("black")
    reset_button.draw(screen)
    waypoints.drawWaypoints(screen)
    
    vehicle_surface = pygame.Surface(
        (SEV.dims.x, SEV.dims.y),
        pygame.SRCALPHA
    )
    vehicle_surface.fill("white")

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
        throttle = 300

    elif keys[pygame.K_s]:
        throttle = -300

    if keys[pygame.K_a]:
        steering = -120

    elif keys[pygame.K_d]:
        steering = 120
    
    SEV.speed += throttle * dt
    SEV.speed *= 0.98
    
    SEV.heading += steering * dt
    heading_rad = math.radians(SEV.heading)

    forward_x = math.cos(heading_rad)
    forward_y = math.sin(heading_rad)
    
    SEV.pos.x += forward_x * SEV.speed * dt
    SEV.pos.y += forward_y * SEV.speed * dt
    
    pygame.display.flip()

    # 60 FPS, dt is delta time in seconds since last frame (need to standardize across program)
    dt = clock.tick(60) / 1000

pygame.quit()