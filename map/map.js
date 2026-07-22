// Custom style matching tilemaker's default OpenMapTiles schema to integrate w/ protomaps-leaflet layers

const {
    PolygonSymbolizer,
    LineSymbolizer,
    LineLabelSymbolizer,
    CenteredTextSymbolizer,
} = protomapsL;

const paintRules = [
    {
        dataLayer: "landcover",
        symbolizer: new PolygonSymbolizer({ fill: "#e8e4d8" }),
    },
    {
        dataLayer: "landuse",
        symbolizer: new PolygonSymbolizer({ fill: "#e0ddd0", opacity: 0.6 }),
    },
    {
        dataLayer: "park",
        symbolizer: new PolygonSymbolizer({ fill: "#c8dfb8", opacity: 0.7 }),
    },
    {
        dataLayer: "water",
        symbolizer: new PolygonSymbolizer({ fill: "#a3ccff" }),
    },
    {
        dataLayer: "waterway",
        symbolizer: new LineSymbolizer({ color: "#a3ccff", width: 1.2 }),
    },
    // (only show once zoomed in reasonably close)
    {
        dataLayer: "building",
        symbolizer: new PolygonSymbolizer({
            fill: "#d9d0c3",
            stroke: "#b8ab97",
            width: 0.5,
        }),
        minzoom: 13,
    },
    {
        dataLayer: "transportation",
        symbolizer: new LineSymbolizer({
            color: "#fab8b8",
            width: (z) => (z > 12 ? 5 : 3),
        }),
        filter: (z, f) => ["motorway", "trunk"].includes(f.props["class"]),
    },
    {
        dataLayer: "transportation",
        symbolizer: new LineSymbolizer({
            color: "#fcd7a0",
            width: (z) => (z > 12 ? 4 : 2),
        }),
        filter: (z, f) => ["primary", "secondary"].includes(f.props["class"]),
    },
    {
        dataLayer: "transportation",
        symbolizer: new LineSymbolizer({
            color: "#ffffff",
            width: (z) => (z > 14 ? 3 : 1),
            stroke: "#cfcfcf",
        }),
        filter: (z, f) =>
            ["tertiary", "minor", "service"].includes(f.props["class"]),
        minzoom: 12,
    },
    {
        dataLayer: "transportation",
        symbolizer: new LineSymbolizer({ color: "#999999", width: 1 }),
        filter: (z, f) => f.props["class"] === "rail",
        minzoom: 10,
    },
    {
        dataLayer: "boundary",
        symbolizer: new LineSymbolizer({
            color: "#888888",
            width: 0.8,
            dash: [4, 2],
        }),
    },
];

const labelRules = [
    // street names along the road line, only when zoomed in
    {
        dataLayer: "transportation_name",
        symbolizer: new LineLabelSymbolizer({
            fill: "#333333",
            font: "12px sans-serif",
        }),
        minzoom: 14,
    },
    {
        dataLayer: "place",
        symbolizer: new CenteredTextSymbolizer({
            fill: "#222222",
            stroke: "#ffffff",
            width: 2,
            font: (z, f) =>
                ["city", "town"].includes(f.props["class"])
                    ? "bold 14px sans-serif"
                    : "11px sans-serif",
        }),
    },
];

const map = L.map('map').setView([29.56, -95.08], 17);

const layer = protomapsL.leafletLayer({
    url: "texas-latest.pmtiles",
    paintRules: paintRules,
    labelRules: labelRules,
    maxDataZoom: 14,
});
layer.addTo(map);


const socket = new WebSocket("ws://localhost:8765");

const OSRM_BASE_URL = "http://127.0.0.1:5000";
const OSRM_PROFILE = "driving";

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
        `?overview=full&geometries=geojson&steps=true`;

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

        const latlngs = route.geometry.coordinates.map(c => [c[1], c[0]]);

        routeLine = L.polyline(latlngs, { color: "blue", weight: 4 }).addTo(map);
        map.fitBounds(routeLine.getBounds(), { padding: [20, 20] });

        const steps = route.legs[0].steps.map(step => ({
            instruction: step.maneuver.type,
            modifier: step.maneuver.modifier,
            name: step.name,
            distance_m: step.distance,
            duration_s: step.duration
        }));

        socket.send(JSON.stringify({
            type: "route",
            distance_m: route.distance,
            duration_s: route.duration,
            geometry: route.geometry.coordinates,
            steps: steps
        }));

    } catch (err) {
        console.error("Routing error:", err);
    }
}

map.on('click', function (e) {

    if (!startMarker) {
        startMarker = L.marker(e.latlng, { title: "Start" }).addTo(map);
        sendWaypoint("start", e.latlng);

    } else if (!endMarker) {
        endMarker = L.marker(e.latlng, { title: "End" }).addTo(map);
        sendWaypoint("end", e.latlng);
        drawRoute();

    } else {
        map.removeLayer(startMarker);
        map.removeLayer(endMarker);
        clearRoute();

        startMarker = L.marker(e.latlng, { title: "Start" }).addTo(map);
        endMarker = null;

        sendWaypoint("start", e.latlng);
    }
});


/*

The below is an example of valid GeoJSON data:

{
  "type": "Feature",
  "properties": {},
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [-95.08417, 29.56018],
      [-95.08413, 29.56025],
      [-95.08411, 29.56030],
      [-95.08433, 29.56038]
    ]
  }
}

*/
