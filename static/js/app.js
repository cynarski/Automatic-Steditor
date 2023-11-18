function saveCity() {
    const city = document.getElementById('citySelect').value;
    const productSelect = document.getElementById('productSelect');
    const weight = document.getElementById('productWeight').value;

    if (!city || productSelect.selectedOptions.length === 0 || !weight) {
        alert("Proszę wybrać miasto, przynajmniej jeden produkt i wpisać wagę.");
        return;
    }

    const products = Array.from(productSelect.selectedOptions).map(option => option.value);

    let selections = JSON.parse(localStorage.getItem('selections')) || [];
    selections.push({ city, products, weight });
    localStorage.setItem('selections', JSON.stringify(selections));

    updateDisplay();
}


function updateDisplay() {
    const selections = JSON.parse(localStorage.getItem('selections')) || [];
    const tableBody = document.getElementById('infoTable').getElementsByTagName('tbody')[0];

    tableBody.innerHTML = '';

    selections.forEach(selection => {
        let row = tableBody.insertRow();
        let cellCity = row.insertCell(0);
        let cellProduct = row.insertCell(1);
        let cellWeight = row.insertCell(2);

        cellCity.textContent = selection.city;
        cellProduct.textContent = selection.products.join(', '); // Łączenie produktów w jeden ciąg tekstowy
        cellWeight.textContent = selection.weight + ' t';
    });
}

function clearSelection() {
    localStorage.removeItem('selections');
    updateDisplay();
    document.getElementById('productImage').style.display = 'none';
    if (window.clearMarkers)
    {
        window.clearMarkers();
    }

}
function clearEverything() {
    clearSelection();
    clearMarkers();
}

// updateDisplay();

