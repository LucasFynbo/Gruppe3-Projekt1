// Data til grafen
var data = {
    labels: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"],
    datasets: [{
        label: "Dit data",
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        data: [10, 30, 15, 25,10, 30, 15, 25, 20, 10, 30, 15, 25]
    }]
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
            beginAtZero: true
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

// Simulerer tilføjelse af nyt datapunkt hvert sekund
setInterval(function () {
    // Tilføj et nyt datapunkt
    var newDataPoint = Math.floor(Math.random() * 41); // Genererer et tal mellem 0 og 40
    data.datasets[0].data.push(newDataPoint);

    // Fjern det ældste datapunkt, hvis der er mere end 24 datapunkter
    if (data.datasets[0].data.length > 25) {
        data.datasets[0].data.shift();
    }

    // Opdater grafen
    myLineChart.update();
}, 2000);