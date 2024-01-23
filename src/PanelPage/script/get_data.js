setInterval(location.reload(), 40000);

getData()

function getData() {

    var senddata = {
        data: 'session get data',
    };

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

        const linkedDevices = eval(data.linked_devices);
        const linkedDeviceNames = eval(data.linked_device_names);

        // 'Panel Home' i URL
        if (window.location.href.indexOf("panel_home") > -1) {
            // Grab recording data for activity graph
            if (linkedDevices && linkedDeviceNames && linkedDevices.length === linkedDeviceNames.length) {
                for (let i = 0; i < linkedDevices.length; i++) {
                    const deviceId = linkedDevices[i];
                    const deviceName = linkedDeviceNames[i];
                    const event = new CustomEvent('updateGraph', { detail: { deviceId, deviceName } });
                    document.dispatchEvent(event);
                }
            } else {
                console.error('Error: Invalid linked_devices or linked_device_names format');
            }


            // Grab the last 10 information log entries
        }

        // 'Panel Log' i URL
        else if (window.location.href.indexOf("panel_log") > -1) {
            // Grab full list of information log
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}