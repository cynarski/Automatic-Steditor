const map = L.map('map').setView([52.2297, 21.0122], 6); // Ustawienie mapy na Polskę

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let routingControl;

function showRoute() {
    const startCity = document.getElementById('startCity').value;
    const endCity = document.getElementById('endCity').value;

    if (routingControl) {
        map.removeControl(routingControl);
    }

    fetch(`https://nominatim.openstreetmap.org/search?city=${startCity}&format=json&limit=1`)
        .then(response => response.json())
        .then(dataStart => {
            const startLat = parseFloat(dataStart[0].lat);
            const startLon = parseFloat(dataStart[0].lon);

            fetch(`https://nominatim.openstreetmap.org/search?city=${endCity}&format=json&limit=1`)
                .then(response => response.json())
                .then(dataEnd => {
                    const endLat = parseFloat(dataEnd[0].lat);
                    const endLon = parseFloat(dataEnd[0].lon);

                    routingControl = L.Routing.control({
                        waypoints: [
                            L.latLng(startLat, startLon),
                            L.latLng(endLat, endLon)
                        ],
                        routeWhileDragging: true
                    }).addTo(map);
                });
        });
}
