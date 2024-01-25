const informationWndContainer = document.getElementById("information-wnd");
const deviceColumnsContainer = document.createElement("div");
deviceColumnsContainer.id = "device-columns-container";
const alarmModal = document.getElementById("alarm-modal");

const styleElement = document.createElement("style");
styleElement.textContent = `
  #device-columns-container {
    display: flex;
    gap: 10px;
  }

  .device-column {
    border: 1px solid #ddd;
    padding: 10px;
    cursor: pointer;
    width: 150px;
    text-align: center;
  }

  .device-column:hover {
    background-color: #f5f5f5;
  }

  .modal {
    display: none;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.4);
    padding-top: 60px;
}

.modal-content {
    background-color: #fefefe;
    margin: 5% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
    max-height: 80%; /* Set a maximum height for the modal content */
    overflow-y: auto; /* Enable vertical scroll if needed */
}

  .close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
  }

  .close:hover,
  .close:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
  }

  .log-entry {
    margin-bottom: 10px;
  }
`;

document.head.appendChild(styleElement);

// Function to close the alarm modal
function closeModal() {
    alarmModal.style.display = "none";
}

// Add a close button at the top
const closeButton = document.createElement("span");
closeButton.className = "close";
closeButton.innerHTML = "&times;";
closeButton.onclick = closeModal;

function createLogColumn(deviceId, logContents) {

    if (logContents && logContents.length > 0) {
        const truncatedEntries = logContents.slice(0, 24);
        const entriesText = truncatedEntries.length === 24 ? "24" : `${truncatedEntries.length}`;
        const columnText = `${deviceId} [${entriesText}]`;

        const deviceColumn = document.createElement("div");
        deviceColumn.className = "device-column";
        deviceColumn.textContent = columnText;

        deviceColumn.addEventListener("click", () => openAlarmModal(deviceId, logContents));

        deviceColumnsContainer.appendChild(deviceColumn);
    }
}

function openAlarmModal(deviceId, logContents) {

    informationWndContainer.innerHTML = "";

    const modalContent = document.createElement("div");

    modalContent.appendChild(closeButton);

    for (const entry of logContents.slice(0, 24)) {
        const entryElement = document.createElement("div");
        entryElement.className = "log-entry";
        entryElement.textContent = entry;
        modalContent.appendChild(entryElement);
    }

    informationWndContainer.appendChild(modalContent);

    alarmModal.style.display = "block";
}

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
        try {
            const correctedTemperatureData = data.temperature_data.replace(/'/g, '"');
            const temperatureData = JSON.parse(correctedTemperatureData);

            const correctedAlarmLogs = data.alarm_logs.replace(/'/g, '"');
            const alarmLogData = JSON.parse(correctedAlarmLogs);

            // 'Panel Home' i URL
            if (window.location.href.indexOf("home") > -1) {
                if (linkedDevices && linkedDeviceNames && linkedDevices.length === linkedDeviceNames.length) {
                    for (let i = 0; i < linkedDevices.length; i++) {
                        const deviceId = linkedDevices[i];
                        const deviceName = linkedDeviceNames[i];
                        
                        const event = new CustomEvent('updateGraph', { detail: { deviceId, deviceName, temperature_data: temperatureData } });
                        document.dispatchEvent(event);

                        // Display de sidste 8 logs
                        createLogColumn(deviceId, alarmLogData[deviceId] || []);
                    }
                } else {
                    console.error('Error: Invalid linked_devices or linked_device_names format');
                }

                informationWndContainer.appendChild(deviceColumnsContainer);

            }

            // 'Panel Log' i URL
            else if (window.location.href.indexOf("log") > -1) {
            }
        } catch (error) {
            console.error('Error parsing temperature_data:', error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

setInterval(getData(), 40000);