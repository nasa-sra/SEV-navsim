const socket = new WebSocket("ws://localhost:8765");

const map = L.map('map').setView([29.56, -95.08], 17);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

// --- CONFIG: swap this when you self-host OSRM/Valhalla ---
const OSRM_BASE_URL = "https://router.project-osrm.org";
const OSRM_PROFILE = "foot";

let startMarker = null;
let endMarker = null;
let routeLine = null;

function clearRoute() {
    if (routeLine) {
        map.removeLayer(routeLine);
        routeLine = null;
    }
}

function sendWaypoint(label, latlng) {
    socket.send(JSON.stringify({
        type: "waypoint",
        label: label, // "start" or "end"
        lat: latlng.lat,
        lon: latlng.lng
    }));
}

async function fetchRoute(start, end) {
    const url = `${OSRM_BASE_URL}/route/v1/${OSRM_PROFILE}/` +
        `${start.lng},${start.lat};${end.lng},${end.lat}` +
        `?overview=full&geometries=geojson`;

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`OSRM request failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data.routes || data.routes.length === 0) {
        throw new Error("No route found");
    }

    return data.routes[0];
}

async function drawRoute() {
    clearRoute();

    try {
        const route = await fetchRoute(startMarker.getLatLng(), endMarker.getLatLng());

        // GeoJSON coords are [lon, lat] — Leaflet wants [lat, lon]
        const latlngs = route.geometry.coordinates.map(c => [c[1], c[0]]);

        routeLine = L.polyline(latlngs, { color: "blue", weight: 4 }).addTo(map);
        map.fitBounds(routeLine.getBounds(), { padding: [20, 20] });

        // send the route itself to Python too, in case the GUI wants it
        socket.send(JSON.stringify({
            type: "route",
            distance_m: route.distance,
            duration_s: route.duration,
            geometry: route.geometry.coordinates
        }));

    } catch (err) {
        console.error("Routing error:", err);
    }
}

map.on('click', function (e) {

    if (!startMarker) {
        // first click: set start
        startMarker = L.marker(e.latlng, { title: "Start" }).addTo(map);
        sendWaypoint("start", e.latlng);

    } else if (!endMarker) {
        // second click: set end, then route
        endMarker = L.marker(e.latlng, { title: "End" }).addTo(map);
        sendWaypoint("end", e.latlng);
        drawRoute();

    } else {
        // third click: reset everything and start over
        map.removeLayer(startMarker);
        map.removeLayer(endMarker);
        clearRoute();

        startMarker = L.marker(e.latlng, { title: "Start" }).addTo(map);
        endMarker = null;

        sendWaypoint("start", e.latlng);
    }
});