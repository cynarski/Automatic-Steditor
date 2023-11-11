window.onload = function() {
    const startCity = localStorage.getItem('startCity');
    const endCity = localStorage.getItem('endCity');

    if (startCity && endCity) {
        const map = L.map('map').setView([52.2297, 21.0122], 6);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Tutaj możesz dodać logikę do wyświetlenia trasy na mapie
        // na podstawie danych z localStorage
        // Na razie tylko wyświetlamy nazwy miast
        L.marker([52.2297, 21.0122]).addTo(map)
            .bindPopup(startCity)
            .openPopup();

        L.marker([50.0647, 19.9450]).addTo(map)
            .bindPopup(endCity)
            .openPopup();
    }
};
