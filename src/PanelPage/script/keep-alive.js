// 30 sekunder
setInterval(keepAlive, 30000);

function keepAlive() {
    var senddata = {
        data: 'session keep-alive',
    };

    fetch('https://waw.sof60.dk/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(senddata),
    }).catch(error => {
        console.error('Error in keep-alive request:', error);
    });
}