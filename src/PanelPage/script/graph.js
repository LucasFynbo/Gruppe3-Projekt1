var datasets = [];

// Data til grafen
var data = {
    labels: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"],
    datasets: []  // Initialize without any datasets
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

// Listen for the custom event
document.addEventListener('updateGraph', function (event) {
    // Clear existing datasets
    datasets = [];

    // Update datasets with the received data
    const { deviceId, deviceName } = event.detail;
    datasets.push({
        label: deviceName, // Assuming deviceName is the name you want for the label
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        data: [/* Your data for this device */]  // Add the actual data for this device
    });

    // Set the datasets in the chart data
    myLineChart.data.datasets = datasets;

    // Call update() to refresh the chart
    myLineChart.update();
});
