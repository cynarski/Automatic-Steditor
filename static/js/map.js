document.addEventListener('DOMContentLoaded', function() {
    // Inicjalizacja mapy + blokowanie
    let map = L.map('map', {
        center: [52.237049, 19.517532], // Centrum mapy
        zoom: 6, // Poziom przybliżenia
        dragging: false, // Wyłączenie przeciągania
        zoomControl: false, // Wyłączenie kontrolek zoomu
        scrollWheelZoom: false, // Wyłączenie przybliżania kółkiem myszy
        doubleClickZoom: false, // Wyłączenie przybliżania podwójnym kliknięciem
    });
    let markers = [];

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    function addCityMarker(lat, lon) {
        let marker = L.marker([lat, lon]).addTo(map);
        markers.push(marker);
    }

    function findCity(cityName) {
        let encodedCityName = encodeURIComponent(cityName);

        fetch(`https://nominatim.openstreetmap.org/search?city=${encodedCityName}&format=json`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    let info = data[0];
                    let lat = parseFloat(info.lat);
                    let lon = parseFloat(info.lon);
                    addCityMarker(lat, lon);
                } else {
                    alert("Nie znaleziono miasta.");
                }
            })
            .catch(error => {
                alert("Błąd podczas wyszukiwania miasta.");
                console.error(error);
            });
    }

    window.clearMarkers = function() {
        markers.forEach(function(marker) {
            map.removeLayer(marker);
        });
        markers = [];
    };

    document.getElementById('saveCityButton').addEventListener('click', function() {
        let cityName = document.getElementById('citySelect').value;
        if (cityName) {
            findCity(cityName);
        }
    });
});
