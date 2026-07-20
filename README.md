# SEV-simulation
Proof-of-concept simulation for NASA SEV (Space Exploration Vehicle) Rover to navigate to the rockyard semi-autonomously with calculated joystick instructions

## How to self-host OSRM
OSRM (Open Source Routing Machine) is a highly efficient C++ routing engine that can be used on OpenStreetMap data to find the optimal path between two Earth coordinates alongside other useful data. To self-host OSRM on your machine (basically just to run it offline), do the following:

1. Install Docker Desktop
2. Enable WSL in VSCode
3. Run the following commands in the default directory terminal
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

4. Run the algorithm whenever ready!
```bash
 # run the algorithm on port 5000
    docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend \
        osrm-routed --algorithm mld /data/texas-latest.osrm
```


