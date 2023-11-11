// const map = L.map('map').setView([52.2297, 21.0122], 6); // Ustawienie mapy na Polskę
//
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//     attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
// }).addTo(map);
//
// let routingControls = [];
//
// function showRoute() {
//     const startCity = document.getElementById('startCity').value;
//     const endCity = document.getElementById('endCity').value;
//
//     fetch(`https://nominatim.openstreetmap.org/search?city=${startCity}&format=json&limit=1`)
//         .then(response => response.json())
//         .then(dataStart => {
//             const startLat = parseFloat(dataStart[0].lat);
//             const startLon = parseFloat(dataStart[0].lon);
//
//             fetch(`https://nominatim.openstreetmap.org/search?city=${endCity}&format=json&limit=1`)
//                 .then(response => response.json())
//                 .then(dataEnd => {
//                     const endLat = parseFloat(dataEnd[0].lat);
//                     const endLon = parseFloat(dataEnd[0].lon);
//
//                     const routingControl = L.Routing.control({
//                         waypoints: [
//                             L.latLng(startLat, startLon),
//                             L.latLng(endLat, endLon)
//                         ],
//                         routeWhileDragging: true
//                     }).addTo(map);
//
//                     routingControl.on('routesfound', function(e) {
//                         const routes = e.routes;
//                         const summary = routes[0].summary;
//                         const distance = (summary.totalDistance / 1000).toFixed(2);
//
//                         // Dodajemy informacje o trasie do listy
//                         const routeInfoItem = document.createElement('li');
//                         routeInfoItem.innerText = `${startCity} do ${endCity}: ${distance} km`;
//                         document.getElementById('route-info-list').appendChild(routeInfoItem);
//                     });
//
//                     routingControls.push(routingControl);
//                 });
//         });
// }
//
// function clearRoutes() {
//     for (let i = 0; i < routingControls.length; i++) {
//         map.removeControl(routingControls[i]);
//     }
//     routingControls = [];
//     document.getElementById('route-info-list').innerHTML = ''; // Czyszczenie listy
// }


function saveRoute() {
    const startCity = document.getElementById('startCity').value;
    const endCity = document.getElementById('endCity').value;

    localStorage.setItem('startCity', startCity);
    localStorage.setItem('endCity', endCity);

    // Przekierowanie do strony z mapą
    window.location.href = 'map.html';
}
