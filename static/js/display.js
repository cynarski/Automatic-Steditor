document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('map').setView([52.237049, 21.017532], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    var routeInfo = []; // Tutaj będziemy przechowywać informacje o trasach
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
                    L.latLng(52.237049, 21.017532), // Warszawa
                    cityLatLng // Miasto docelowe
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
                // Możesz teraz dodać informacje o trasie do tablicy
                routeInfo.push({
                    distance: summary.totalDistance,
                    time: summary.totalTime,
                    name: cityData.city
                });
                // Aktualizacja tabeli z nowymi danymi
                updateRouteTable(routeInfo);
            })
            .addTo(map);
        });
    })
    .catch(error => {
        console.error('Błąd podczas pobierania danych:', error);
    });

    function updateRouteTable(routeInfo) {
        // Pobranie referencji do tabeli
        const table = document.querySelector('.route-info-table');
        table.innerHTML = ''; // Wyczyszczenie tabeli

        // Dodawanie informacji o trasach do tabeli
        routeInfo.forEach(info => {
            let row = table.insertRow();
            row.insertCell(0).textContent = info.name;
            row.insertCell(1).textContent = (info.distance / 1000).toFixed(2) + ' km'; // Konwersja na kilometry
            row.insertCell(2).textContent = (info.time / 3600).toFixed(2) + ' h'; // Konwersja na godziny
        });
    }
});
