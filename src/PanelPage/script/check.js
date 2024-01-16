sendData();

function sendData() {
    var senddata = {
        data: 'session authorization',
    };

    console.log('JSON data to be sent:', JSON.stringify(senddata));

    fetch('https://79.171.148.173/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(senddata)

    })
    .then(response => {
        if (!response.ok) { // hvis response return value er false/errored
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text();
    })
    .then(data => {
        // Håndterer svaret fra serveren her
        console.log(data)
    })
    .catch(error => {
        // Håndterer fejl her
        console.error('Error:', error);
    });
}