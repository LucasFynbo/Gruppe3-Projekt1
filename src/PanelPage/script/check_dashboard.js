sendData();

function createDeviceColumn(deviceId, deviceName) {
    const mainContainer = document.getElementById("group-wnd");

    // Lav device column
    const deviceColumn = document.createElement("div");
    deviceColumn.id = `device-full-group-${deviceId}`;
    deviceColumn.className = "full-group-line";

    const row1 = document.createElement("div");
    row1.id = `line-${deviceId}-group-row1`;
    row1.className = "row1-group-line";

    const definedName = document.createElement("h3");
    definedName.id = `defined-name-${deviceId}`;
    definedName.textContent = deviceName;
    row1.appendChild(definedName);

    const optionButtons = document.createElement("div");
    optionButtons.id = `line-${deviceId}-option-btn`;
    optionButtons.className = "group-option-btn";

    // Rename btn
    const renameButton = document.createElement("img");
    renameButton.id = `rename-btn-${deviceId}`;
    renameButton.src = "images/rename.png";
    optionButtons.appendChild(renameButton);

    // Delete btn
    const deleteButton = document.createElement("img");
    deleteButton.id = `delete-btn-${deviceId}`;
    deleteButton.src = "images/delete.png";
    optionButtons.appendChild(deleteButton);

    row1.appendChild(optionButtons);
    deviceColumn.appendChild(row1);

    const row2 = document.createElement("div");
    row2.id = `line-${deviceId}-group-row2`;
    row2.className = "row2-group-line";

    const deviceIdText = document.createElement("p");
    deviceIdText.className = "device-id-group-txt";
    deviceIdText.textContent = `Device ID: ${deviceId}`;

    row2.appendChild(deviceIdText);
    deviceColumn.appendChild(row2);

    mainContainer.appendChild(deviceColumn);
}


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
            
            // Hvis body når session er authorized 
            document.body.style.display = 'flex';

            const loggedInAs = document.querySelector("#username");
            loggedInAs.textContent = `${data.username}`;

            const linkedDevices = eval(data.linked_devices);
            const linkedDeviceNames = eval(data.linked_device_names);

            if (linkedDevices && linkedDeviceNames && linkedDevices.length === linkedDeviceNames.length) {
                for (let i = 0; i < linkedDevices.length; i++) {
                    const deviceId = linkedDevices[i];
                    const deviceName = linkedDeviceNames[i];
                    createDeviceColumn(deviceId, deviceName);
                }
            } else {
                console.error('Error: Invalid linked_devices or linked_device_names format');
            }
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