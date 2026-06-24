import pygame
import colors

size = pygame.Vector2(20, 20)
class Waypoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.x = x
        self.y = y
        
    def getX(self):
        return self.rect.centerx
    
    def getY(self):
        return self.rect.centery
    
    def getCenter(self):
        return pygame.Vector2(self.rect.center)
    
    def getPygameVector(self):
        return pygame.Vector2(self.x, self.y)


waypoints = [
    Waypoint(100, 100),
    Waypoint(200, 200),
    Waypoint(300, 300),
    Waypoint(400, 400),
    Waypoint(500, 500),
    Waypoint(600, 600)
]

def resetWaypoints():
    global waypoints
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
curWaypointIdx = 0

def handle_event(event):
    global dragged_waypoint, offset_x, offset_y, curWaypointIdx

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:

            # Check from last to first so top gets selected
            for i in range(len(waypoints)-1, -1, -1):
                curWaypoint = waypoints[i]
                curWaypointIdx = i
                if curWaypoint.rect.collidepoint(event.pos):
                    dragged_waypoint = curWaypoint.rect

                    mouse_x, mouse_y = event.pos
                    offset_x = curWaypoint.rect.x - mouse_x
                    offset_y = curWaypoint.rect.y - mouse_y
                    break

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            dragged_waypoint = None

    elif event.type == pygame.MOUSEMOTION:
        if dragged_waypoint is not None:
            mouse_x, mouse_y = event.pos

            dragged_waypoint.x = mouse_x + offset_x
            dragged_waypoint.y = mouse_y + offset_y
            
            waypoints[curWaypointIdx] = Waypoint(dragged_waypoint.x, dragged_waypoint.y)

def draw(screen):
    prev = None
    for waypoint in waypoints:

        pygame.draw.rect(screen, "blue", waypoint.rect)

        if prev is not None:
            pygame.draw.line(
                screen,
                colors.RED,
                prev.center,
                waypoint.rect.center,
                3
            )

        prev = waypoint.rect
        
def addWayPoint():
    curNumWaypoints = len(waypoints)
    if(curNumWaypoints < 15):
        waypoints.append(Waypoint(waypoints[curNumWaypoints-1].getX() + 100, 
                                  waypoints[curNumWaypoints-1].getY()))
        
def removeWaypoint():
    curNumWaypoints = len(waypoints)
    if(curNumWaypoints > 2):
        waypoints.pop()
        
def getWaypoints():
    return waypoints