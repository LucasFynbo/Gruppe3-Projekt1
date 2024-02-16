// Data til grafen
var data = {
    labels: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"],
    datasets: [] 
};

// Indstillinger for grafen
var options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: {
            title: {
                display: true,
                text: 'Timer'
            },
            beginAtZero: true
        },
        y: {
            title: {
                display: true,
                text: 'Temperaturforskel'
            },
            beginAtZero: true,
            max: 5.0,
            min: 0.0
        }
    }
};

// Hent canvas og opret grafen
var ctx = document.getElementById('activity-chart').getContext('2d');
var myLineChart = new Chart(ctx, {
    type: 'line',
    data: data,
    options: options
});

// Random int generator vi bruger til RGB randomizer
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

document.addEventListener('updateGraph', function (event) {

    var datasets = myLineChart.data.datasets || [];

    // Opdater dataset med det modtaget info
    const { deviceId, deviceName, temperature_data } = event.detail;
    
    const randomRed = getRandomInt(0, 255);
    const randomGreen = getRandomInt(0, 255);
    const randomBlue = getRandomInt(0, 255);

    const recentTemperatures = temperature_data[deviceId].slice(-24);

    datasets.push({
        label: deviceName,
        fill: false,
        borderColor: `rgb(${randomRed}, ${randomGreen}, ${randomBlue})`,
        data: recentTemperatures || []
    });

    myLineChart.data.datasets = datasets;

    myLineChart.update();
});
