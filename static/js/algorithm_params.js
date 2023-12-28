document.addEventListener('DOMContentLoaded', function() {
    let populationSizeRange = document.querySelector('.population-size.range-input');
    let populationSizeNumber = document.querySelector('.population-size.number-input');

    let selectionSizeRange = document.querySelector('#selection + .input-container .range-input');
    let selectionSizeNumber = document.querySelector('#selection + .input-container .number-input');

    let updateSelectionSizeMax = function() {
        let populationSize = Math.max(populationSizeRange.value, populationSizeNumber.value);
        selectionSizeRange.max = populationSize;
        selectionSizeNumber.max = populationSize;
    };

    populationSizeRange.addEventListener('input', updateSelectionSizeMax);
    populationSizeNumber.addEventListener('input', updateSelectionSizeMax);

    updateSelectionSizeMax();
});



document.addEventListener('DOMContentLoaded', function (){
    let parameterGroups = document.querySelectorAll('.input-container');

    parameterGroups.forEach(function (group) {

        let rangeInput = group.querySelector('.range-input');
        let numberInput = group.querySelector('.number-input');

        let syncValues = function(source) {

            rangeInput.value = source.value;
            numberInput.value = source.value;
        };

        rangeInput.addEventListener('input', function() {
           syncValues(rangeInput);
        });

       numberInput.addEventListener('input', function() {
            syncValues(numberInput);
       });

        numberInput.addEventListener('change', function() {
            syncValues(numberInput);
        });
    });
});