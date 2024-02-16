sendData();

function sendData() {
    var senddata = {
        data: 'session authorization',
    };

    console.log('JSON data to be sent:', JSON.stringify(senddata));

    fetch('https://waw.sof60.dk/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(senddata)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);

        if (data.status === 'Session: Authorization confirmed') {
            console.log('200 OK session authorized.');
            
            // Show the body once the script completes
            document.body.style.display = 'flex';

            const loggedInAs = document.querySelector("#username");
            loggedInAs.textContent = `${data.username}`;
        } else {
            console.error('Error:', data.status);
            window.location.href = '/login';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        window.location.href = '/login';
    });
}