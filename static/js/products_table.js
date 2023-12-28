let selections = []; // Dane przechowywane tylko w pamięci

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

// Nie ma potrzeby wczytywać danych z localStorage przy załadowaniu strony,
// ponieważ wszystkie dane są teraz przechowywane w pamięci.
