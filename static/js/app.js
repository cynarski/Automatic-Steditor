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



function saveCitiesToLocalStorage() {
    const selectedCities = selections.map(selection => selection.city);
    localStorage.setItem('selectedCities', JSON.stringify(selectedCities));
}



document.getElementById('goToMapButton').addEventListener('click', function() {
    document.getElementById('loadingSpinner').style.display = 'block';

    setTimeout(function() {
        saveCitiesToLocalStorage();
        window.location.href = '/map';
    }, 2500)
    this.disabled = true;
});

