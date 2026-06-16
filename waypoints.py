import pygame

RED = (170, 0, 0)

size = pygame.Vector2(20, 20)

class Waypoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

waypoints = [
    Waypoint(100, 100),
    Waypoint(200, 200),
    Waypoint(300, 300),
    Waypoint(400, 400),
    Waypoint(500, 500),
    Waypoint(600, 600)
]

dragged_waypoint = None
offset_x = 0
offset_y = 0


def handle_event(event):
    global dragged_waypoint, offset_x, offset_y

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:

            # Check from last to first so top gets selected
            for waypoint in reversed(waypoints):
                if waypoint.rect.collidepoint(event.pos):
                    dragged_waypoint = waypoint.rect

                    mouse_x, mouse_y = event.pos
                    offset_x = waypoint.rect.x - mouse_x
                    offset_y = waypoint.rect.y - mouse_y
                    break

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            dragged_waypoint = None

    elif event.type == pygame.MOUSEMOTION:
        if dragged_waypoint is not None:
            mouse_x, mouse_y = event.pos

            dragged_waypoint.x = mouse_x + offset_x
            dragged_waypoint.y = mouse_y + offset_y


def drawWaypoints(screen):
    prev = None
    for waypoint in waypoints:

        pygame.draw.rect(screen, "blue", waypoint.rect)

        if prev is not None:
            pygame.draw.line(
                screen,
                RED,
                prev.center,
                waypoint.rect.center,
                3
            )

        prev = waypoint.rect
        
def addWayPoint():
    curNumWaypoints = len(waypoints)
    if(curNumWaypoints < 10):
        waypoints.append(Waypoint(900, 600))
        
def removeWaypoint():
    global waypoints
    curNumWaypoints = len(waypoints)
    if(curNumWaypoints > 2):
        waypoints = waypoints[:-1]