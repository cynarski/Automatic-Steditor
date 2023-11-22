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

    // Funkcja dodająca marker na mapie
    function addCityMarker(lat, lon) {
        var marker = L.marker([lat, lon]).addTo(map);
        markers.push(marker); // Dodaj marker do tablicy
    }

    // Funkcja do wyszukiwania miasta i dodawania markera
    function findCity(cityName) {
        var encodedCityName = encodeURIComponent(cityName);

        fetch(`https://nominatim.openstreetmap.org/search?city=${encodedCityName}&format=json`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    var info = data[0];
                    var lat = parseFloat(info.lat);
                    var lon = parseFloat(info.lon);
                    addCityMarker(lat, lon); // Dodaj marker bez zmiany zoomu lub centrowania
                } else {
                    alert("Nie znaleziono miasta.");
                }
            })
            .catch(error => {
                alert("Błąd podczas wyszukiwania miasta.");
                console.error(error);
            });
    }

    // Funkcja do czyszczenia wszystkich markerów z mapy
    window.clearMarkers = function() {
        markers.forEach(function(marker) {
            map.removeLayer(marker);
        });
        markers = []; // Resetowanie tablicy markerów
    };

    // Nasłuchiwacz zdarzeń dla przycisku "Zapisz miasto"
    document.getElementById('saveCityButton').addEventListener('click', function() {
        var cityName = document.getElementById('citySelect').value;
        if (cityName) {
            findCity(cityName);
        }
    });
});
