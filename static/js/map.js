document.addEventListener('DOMContentLoaded', function() {
    // Inicjalizacja mapy + blokowanie
    var map = L.map('map', {
        center: [52.237049, 19.517532], // Centrum mapy
        zoom: 6, // Poziom przybliżenia
        dragging: false, // Wyłączenie przeciągania
        zoomControl: false, // Wyłączenie kontrolek zoomu
        scrollWheelZoom: false, // Wyłączenie przybliżania kółkiem myszy
        doubleClickZoom: false, // Wyłączenie przybliżania podwójnym kliknięciem
    });
    var markers = [];

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    function addCityMarker(lat, lon) {
        var marker = L.marker([lat, lon]).addTo(map);
        markers.push(marker);

        // Zapisywanie znaczników w localStorage
        saveMarkersToLocalStorage();
    }

    function saveMarkersToLocalStorage() {
        var markersData = markers.map(marker => {
            return { lat: marker.getLatLng().lat, lon: marker.getLatLng().lng };
        });
        localStorage.setItem('markers', JSON.stringify(markersData));
    }

    function loadMarkersFromLocalStorage() {
        var markersData = JSON.parse(localStorage.getItem('markers'));
        if (markersData) {
            markersData.forEach(data => {
                addCityMarker(data.lat, data.lon);
            });
        }
    }

    function findCity(cityName) {
        var encodedCityName = encodeURIComponent(cityName);

        fetch(`https://nominatim.openstreetmap.org/search?city=${encodedCityName}&format=json`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    var info = data[0];
                    var lat = parseFloat(info.lat);
                    var lon = parseFloat(info.lon);
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

        // Czyszczenie znaczników z localStorage
        localStorage.removeItem('markers');
    };

    document.getElementById('saveCityButton').addEventListener('click', function() {
        var cityName = document.getElementById('citySelect').value;
        if (cityName) {
            findCity(cityName);
        }
    });

    // Wczytywanie znaczników z localStorage
    loadMarkersFromLocalStorage();
});
