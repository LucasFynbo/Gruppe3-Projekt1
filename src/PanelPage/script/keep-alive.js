// 30 sekunder
setInterval(keepAlive, 30000);

function keepAlive() {
    var senddata = {
        data: 'session keep-alive',
    };

    fetch('https://79.171.148.173/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(senddata),
    }).then(response => {
        if (!response.ok) {
            console.error('Failed to send keep-alive request:', response.status, response.statusText);
        }
    }).catch(error => {
        console.error('Error in keep-alive request:', error);
    });
}