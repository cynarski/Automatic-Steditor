document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map', {
        center: [52.237049, 20.017532], // Ustawienie centrum mapy na Warszawę
        zoom: 6, // Ustawienie początkowego zoomu mapy
        dragging: false, // Wyłączenie możliwości przeciągania mapy
        touchZoom: false, // Wyłączenie zoomowania dotykiem
        scrollWheelZoom: false, // Wyłączenie zoomowania kółkiem myszy
        doubleClickZoom: false, // Wyłączenie zoomowania podwójnym kliknięciem
        zoomControl: false, // Wyłączenie kontrolek zoomu
        boxZoom: false, // Wyłączenie zoomowania prostokątem wybieranym przez użytkownika
        keyboard: false // Wyłączenie obsługi klawiatury
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let routeInfo = [];
    let selectedCities = JSON.parse(localStorage.getItem('selectedCities')) || [];

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
            let cityLatLng = L.latLng(cityData.lat, cityData.lon);
            L.Routing.control({
                waypoints: [
                    L.latLng(52.237049, 21.017532),
                    cityLatLng
                ],
                routeWhileDragging: false,
                show: false, // Ukrywa panel instrukcji trasy
                createMarker: function (i, waypoint) {
                    return L.marker(waypoint.latLng).bindPopup(cityData.city);
                },
                fitSelectedRoutes: false,
            })
            .on('routesfound', function (e) {
                let routes = e.routes;
                let summary = routes[0].summary;
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
        const tableBody = document.querySelector('#result-table tbody');
        tableBody.innerHTML = ''; // Clear current rows

        routeInfo.forEach(info => {
            let row = tableBody.insertRow();
            let cellCity = row.insertCell(0);
            let cellDistance = row.insertCell(1);
            let cellTime = row.insertCell(2);

            cellCity.textContent = info.name;
            // Convert meters to kilometers and seconds to hours
            cellDistance.textContent = (info.distance / 1000).toFixed(2) + ' km';
            cellTime.textContent = (info.time / 3600).toFixed(2) + ' h';
        });
    }
});
