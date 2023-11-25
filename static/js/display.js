document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('map').setView([52.237049, 21.017532], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    var routeInfo = [];
    var selectedCities = JSON.parse(localStorage.getItem('selectedCities')) || [];

    fetch('/filter-cities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cities: selectedCities })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Otrzymane dane:', data);
        data.forEach(cityData => {
            var cityLatLng = L.latLng(cityData.lat, cityData.lon);
            L.Routing.control({
                waypoints: [
                    L.latLng(52.237049, 21.017532),
                    cityLatLng
                ],
                routeWhileDragging: false,
                show: false, // Ukrywa panel instrukcji trasy
                createMarker: function (i, waypoint) {
                    return L.marker(waypoint.latLng).bindPopup(cityData.city);
                }
            })
            .on('routesfound', function (e) {
                var routes = e.routes;
                var summary = routes[0].summary;
                routeInfo.push({
                    distance: summary.totalDistance,
                    time: summary.totalTime,
                    name: cityData.city
                });
                updateRouteTable(routeInfo);
            })
            .addTo(map);
        });
    })
    .catch(error => {
        console.error('Błąd podczas pobierania danych:', error);
    });

    function updateRouteTable(routeInfo) {
        const table = document.querySelector('#result-table');
        table.innerHTML = '';

        routeInfo.forEach(info => {
            let row = table.insertRow();
            row.insertCell(0).textContent = info.name;
            row.insertCell(1).textContent = (info.distance / 1000).toFixed(2) + ' km';
            row.insertCell(2).textContent = (info.time / 3600).toFixed(2) + ' h';
        });
    }
});
