document.addEventListener('DOMContentLoaded', function() {
    var map = L.map('map').setView([52.237049, 21.017532], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    var selectedCities = JSON.parse(localStorage.getItem('selectedCities')) || [];

    fetch('/filter-cities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cities: selectedCities })
    })
    .then(response => response.json())
    .then(data => {
        data.forEach(city => {
            var latLng = L.latLng(city.lat, city.lon);
            L.Routing.control({
                waypoints: [
                    L.latLng(52.237049, 21.017532), // Warszawa
                    latLng // Miasto docelowe
                ],
                routeWhileDragging: true,
                show: false // Ukrywa panel instrukcji trasy
            }).addTo(map);
        });
    })
    .catch(error => console.error('Błąd:', error));
});
