let selections = []; // Teraz dane są przechowywane w pamięci, a nie w localStorage

function saveCity() {
    const city = document.getElementById('citySelect').value;
    const productSelect = document.getElementById('productSelect');
    const weight = document.getElementById('productWeight').value;
    const deadline = document.getElementById('deliveryDeadline').value;

    if (!city || productSelect.selectedOptions.length === 0 || !weight || !deadline) {
        alert("Proszę wybrać miasto, przynajmniej jeden produkt, wpisać wagę oraz ustawić termin dostawy.");
        return;
    }

    const products = Array.from(productSelect.selectedOptions).map(option => option.value);
    selections.push({ city, products, weight, deadline });
    updateDisplay();

    // Zapisywanie danych w localStorage
    localStorage.setItem('selections', JSON.stringify(selections));
}

function updateDisplay() {
    const tableBody = document.getElementById('infoTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    selections.forEach(selection => {
        let row = tableBody.insertRow();
        let cellCity = row.insertCell(0);
        let cellProduct = row.insertCell(1);
        let cellWeight = row.insertCell(2);
        let cellDeadline = row.insertCell(3);

        cellCity.textContent = selection.city;
        cellProduct.textContent = selection.products.join(', ');
        cellWeight.textContent = selection.weight + ' t';
        cellDeadline.textContent = selection.deadline + ' days';
    });
}

function clearSelection() {
    selections = [];
    updateDisplay();
    document.getElementById('productImage').style.display = 'none';
    if (window.clearMarkers) {
        window.clearMarkers();
    }
}

function clearEverything() {
    clearSelection();
    clearMarkers();
}

document.addEventListener('DOMContentLoaded', function() {
    // Wczytywanie danych z localStorage i aktualizacja wyświetlania tabeli
    const storedSelections = localStorage.getItem('selections');
    if (storedSelections) {
        selections = JSON.parse(storedSelections);
        updateDisplay();
    }
});

// Dodaj tę funkcję do app.js
function saveCitiesToLocalStorage() {
    const selectedCities = selections.map(selection => selection.city);
    localStorage.setItem('selectedCities', JSON.stringify(selectedCities));
}

document.getElementById('goToMapButton').addEventListener('click', function() {
    saveCitiesToLocalStorage();
    window.location.href = '/map';
});
