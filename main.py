import pygame
import pygame_widgets
import button
import colors

import threading
import asyncio
import json
import websockets

import webbrowser
import os

from sim_screen import SimScreen
from gui_screen import GuiScreen
 
ws_server = None

clients = set()

start_waypoint = None
end_waypoint = None
latest_route = None

async def handler(websocket):
    global start_waypoint, end_waypoint, latest_route

    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "waypoint":
            if data["label"] == "end": end_waypoint = (data["lat"], data["lon"])
            elif data["label"] == "start": start_waypoint = (data["lat"], data["lon"])

        elif data["type"] == "route":
            latest_route = {
                "distance_m": data["distance_m"],
                "duration_s": data["duration_s"],
                "geometry": data["geometry"],  # list of [lon, lat] pairs
            }
            print(f"Route received: {latest_route['distance_m']:.0f} m, "
                  f"{latest_route['duration_s']:.0f} s")


async def start_server():
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket running on ws://localhost:8765")

    await server.wait_closed()
    
    
def stop_server():
    global ws_server

    if ws_server:
        ws_server.close()
        print("WebSocket server closing...")


def run_ws():
    asyncio.run(start_server())


# PYGAME INIT
 
pygame.init()

screen = pygame.display.set_mode((1180, 780))
clock = pygame.time.Clock()

sim_screen = SimScreen(screen)
gui_screen = GuiScreen(screen)

current_screen = gui_screen


# Give GuiScreen access to waypoints
gui_screen.latest_waypoint = lambda: end_waypoint


# SCREEN SWITCHING
 
def show_sim():
    global current_screen
    current_screen = sim_screen


def show_gui():
    global current_screen
    current_screen = gui_screen

# UI BUTTONS
 
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


# NASA LOGO
 
nasa_logo = pygame.image.load("images/nasa_logo.png").convert_alpha()

nasa_logo = pygame.transform.smoothscale(
    nasa_logo,
    (
        int(nasa_logo.get_width() * 0.1),
        int(nasa_logo.get_height() * 0.1)
    )
)


# START WEBSOCKET THREAD
 
threading.Thread(target=run_ws, daemon=True).start()

webbrowser.open("http://localhost:8000")


# MAIN LOOP

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
    if isinstance(current_screen, GuiScreen):
        current_screen.setText()
        if start_waypoint and end_waypoint:
            current_screen.set_waypoints(start_waypoint, end_waypoint)
            current_screen.set_route(latest_route)
            
        pygame_widgets.update(events)
    screen.blit(nasa_logo, (1025, 25))
    left_button.draw(screen)
    right_button.draw(screen)

    pygame.display.flip()

stop_server()
pygame.quit()