function sendDataToPython() {
    const tableData = getTableData();

    fetch('/process-data', {
        method: 'POST',
        headers : {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tableData)
    })
        .then(response => response.json())
        .then(data => console.log('Odpowiedz z pythona', data))
        .catch(error => console.error('Błąd', error));
}


function getTableData() {
    const table = document.getElementById('infoTable');
    const rows = table.getElementsByTagName('tr');
    let data = [];

    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName('td');
        data.push({
            city: cells[0].textContent,
            products: cells[1].textContent.split(', '),
            weight: cells[2].textContent
        });
    }

    return data;
}