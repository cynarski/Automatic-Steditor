function getTableData() {
    const table = document.getElementById('infoTable');
    const rows = table.getElementsByTagName('tr');
    let data = [];

    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName('td');
        data.push({
            city: cells[0].textContent,
            products: cells[1].textContent.split(', '),
            weight: cells[2].textContent,
            deadline: cells[3].textContent
        });
    }

    return data;
}