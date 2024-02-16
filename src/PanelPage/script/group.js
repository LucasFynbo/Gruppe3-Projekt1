document.addEventListener('DOMContentLoaded', function() {
    // Add sensor to group
    const addsensorClickable = document.getElementById('sb-addsensor-group-btn');
    const addsensorOpen = document.getElementById('addsensor-menu_open');
    const closeBtnAddsensor = document.getElementById('close_btn_add-sensor-menu');

    addsensorClickable.addEventListener('click', function() {
        addsensorOpen.style.display = 'block';
    });

    closeBtnAddsensor.addEventListener('click', function() {
        addsensorOpen.style.display = 'none';
    });

    // Settings
    const SettingsClickable = document.getElementById('sb-settings-btn');
    const settingsOpen = document.getElementById('settingsmenu_open');
    const closeBtnSettings = document.getElementById('close_btn_settings-menu');

    SettingsClickable.addEventListener('click', function() {
        settingsOpen.style.display = 'block';
    });

    closeBtnSettings.addEventListener('click', function() {
        settingsOpen.style.display = 'none';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('submit-btn').addEventListener('click', addSensorGroup);
});

// Add sensor to group funktion
function addSensorGroup() {
    var deviceID = document.getElementById('inputbox_deviceid').value;
    var password = document.getElementById('inputbox_password').value;

    // Tjek om de er tomme inden vi sender dataen til serveren
    if (deviceID.trim() === '') {
        document.getElementById('inputbox_deviceid').classList.add('error');

    } else {
        document.getElementById('inputbox_deviceid').classList.remove('error');
    }

    if (password.trim() === '') {
        document.getElementById('inputbox_password').classList.add('error');
    } else {
        document.getElementById('inputbox_password').classList.remove('error');
    }

    if (deviceID.trim() === '' || password.trim() === '') {
        console.log('[!] Inputboxes are empty, aborting...');
        return;
    }

    var senddata = {
        data: 'add sensor request',
        user: deviceID,
        pass: password
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
        return response.json();
    })
    .then(data => {
        if (data.status === 'Sensor: Add request succeeded') {
            console.log('200 OK; login authenticated');
            window.location.href = '/panel_home';

        } else if (data.status === 'Sensor: Invalid credentials') {
            document.getElementById('inputbox_deviceid').classList.add('error');
            document.getElementById('inputbox_password').classList.add('error');

            throw new Error("HTTP error; 401 Unauthorized; Invalid credentials");
        } else {
            console.log('520 Unknown; Unknown error occurred');
            
            throw new Error("HTTP error; 520 Unknown; Unknown error occurred");
        }
    })
    .catch(error => {
        // Håndterer fejl her
        console.error('Error:', error);
    });
    
}