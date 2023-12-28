"use strict";
function sendDataToPython() {
    var tableData = getTableData();
    var sliderData = getSliderData();
    var payload = {
        tableData: tableData,
        sliderData: sliderData
    };
    fetch('/process-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
        .then(function (response) { return response.json(); })
        .then(function (data) { return console.log('Odpowiedz z pythona', data); })
        .catch(function (error) { return console.error('Błąd', error); });
}
function getTableData() {
    var table = document.getElementById('infoTable');
    var rows = table.getElementsByTagName('tr');
    var data = [];
    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');
        data.push({
            city: cells[0].textContent || "",
            products: cells[1].textContent ? cells[1].textContent.split(', ') : [],
            weight: cells[2].textContent || "",
            deadline: cells[3].textContent || ""
        });
    }
    return data;
}
function getSliderData() {
    var _a, _b, _c, _d, _e, _f;
    return {
        populationSize: parseInt(((_a = document.querySelector('.population-size.number-input')) === null || _a === void 0 ? void 0 : _a.value) || '0', 10),
        selectionSize: parseInt(((_b = document.querySelector('.selection-size.number-input')) === null || _b === void 0 ? void 0 : _b.value) || '0', 10),
        crossoverRate: parseFloat(((_c = document.querySelector('.crossover-rate.number-input')) === null || _c === void 0 ? void 0 : _c.value) || '0'),
        mutationRate: parseFloat(((_d = document.querySelector('.mutation-rate.number-input')) === null || _d === void 0 ? void 0 : _d.value) || '0'),
        payRate: parseFloat(((_e = document.querySelector('.pay-rate.number-input')) === null || _e === void 0 ? void 0 : _e.value) || '0'),
        visitedCitiesLimit: parseInt(((_f = document.querySelector('.visited-cities-limit.number-input')) === null || _f === void 0 ? void 0 : _f.value) || '0', 10),
    };
}
