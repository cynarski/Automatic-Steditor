// Definicja interfejsu dla struktury danych w tabeli
// Definicje interfejsów
interface TableData {
    city: string;
    products: string[];
    weight: string;
    deadline: string;
}

interface SliderData {
    populationSize: number;
    selectionSize: number;
    crossoverRate: number;
    mutationRate: number;
    payRate: number;
    visitedCitiesLimit: number;
}

function sendDataToPython(): void {
    const tableData: TableData[] = getTableData();
    const sliderData: SliderData = getSliderData();

    const payload = {
        tableData,
        sliderData
    };

    fetch('/process-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => console.log('Odpowiedz z pythona', data))
    .catch(error => console.error('Błąd', error));
}

function getTableData(): TableData[] {
    const table: HTMLTableElement = document.getElementById('infoTable') as HTMLTableElement;
    const rows: HTMLCollectionOf<HTMLTableRowElement> = table.getElementsByTagName('tr');
    let data: TableData[] = [];

    for (let i = 1; i < rows.length; i++) {
        const cells: HTMLCollectionOf<HTMLTableCellElement> = rows[i].getElementsByTagName('td');
        data.push({
            city: cells[0].textContent || "",
            products: cells[1].textContent ? cells[1].textContent.split(', ') : [],
            weight: cells[2].textContent || "",
            deadline: cells[3].textContent || ""
        });
    }

    return data;
}

function getSliderData(): SliderData {
    return {
        populationSize: parseInt((document.querySelector('.population-size.number-input') as HTMLInputElement)?.value || '0', 10),
        selectionSize: parseInt((document.querySelector('.selection-size.number-input') as HTMLInputElement)?.value || '0', 10),
        crossoverRate: parseFloat((document.querySelector('.crossover-rate.number-input') as HTMLInputElement)?.value || '0'),
        mutationRate: parseFloat((document.querySelector('.mutation-rate.number-input') as HTMLInputElement)?.value || '0'),
        payRate: parseFloat((document.querySelector('.pay-rate.number-input') as HTMLInputElement)?.value || '0'),
        visitedCitiesLimit: parseInt((document.querySelector('.visited-cities-limit.number-input') as HTMLInputElement)?.value || '0', 10),
    };
}
