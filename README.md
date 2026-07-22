# SEV-simulation
Proof-of-concept simulation for NASA SEV Rover and GUI for semi-autonomous navigation to the rockyard with calculated joystick instructions

## How to self-host OSRM
OSRM (Open Source Routing Machine) is a highly efficient C++ routing engine that can be used on OpenStreetMap data to find the optimal path between two Earth coordinates alongside other useful data. To self-host OSRM on your machine (basically just to run it offline), do the following:

#1. Install Docker Desktop \
#2. Enable WSL in VSCode \
#3. Run the following commands in the default terminal
```bash
# downloads the desired region-based map data from the web (Texas in this case)
wget https://download.geofabrik.de/north-america/us/texas-latest.osm.pbf

# extracts the map data and produces .osrm files
docker run -t -v "${PWD}:/data" osrm/osrm-backend \
    osrm-extract -p /opt/car.lua /data/texas-latest.osm.pbf

# partitions the map data for MLD (Multi-Level Djikstra)
docker run -t -v "${PWD}:/data" osrm/osrm-backend \
    osrm-partition /data/texas-latest.osrm

# customize data (MLD path; different from contract)
docker run -t -v "${PWD}:/data" osrm/osrm-backend \
    osrm-customize /data/texas-latest.osrm
```

#4. Run the algorithm whenever ready!
```bash
# run the algorithm on port 5000
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend \
    osrm-routed --algorithm mld /data/texas-latest.osrm
```
## Running the SEV-navsim Map and GUI

#1. Open SEV-navsim in VSCode and start the python range_server on port 8000 (in the map folder)

Note: This app serves its files over a local HTTP server (range_server.py) rather than opening index.html directly, because the offline map tiles (.pmtiles) are read via HTTP range requests (partial byte-range fetches that only work over http://, not file://). Python's built-in http.server doesn't correctly support range requests, so a small custom server is used instead to ensure the map tiles load correctly.

```bash
cd map
python range_server.py 8000
```

#2. Run the main Python file! (SEV-navsim base directory; opens GUI and map in default browser)
```bash
python main.py
```