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

// Add to group function
function addSensorGroup {
    var deviceID = document.getElementById('inputbox_deviceid').value;
    var password = document.getElementById('inputbox_password').value;

    // Tjek om de er tomme inden vi sender dataen til serveren
    if (deviceID.trim() === '') {
        document.getElementById('inputbox_deviceid').classList.add('error');
        responseStatusText.textContent = "Please fill out 'Device-ID' and 'Password' boxes";

    } else {
        document.getElementById('inputbox_deviceid').classList.remove('error');
        responseStatusText.textContent = "";
    }

    if (password.trim() === '') {
        document.getElementById('inputbox_password').classList.add('error');
        const responseStatusText = document.querySelector("#response-status");
        responseStatusText.textContent = "Please fill out 'Device-ID' and 'Password' boxes";
    } else {
        document.getElementById('inputbox_password').classList.remove('error');
        responseStatusText.textContent = "";
    }

    if (deviceID.trim() === '' || password.trim() === '') {
        console.log('[!] Inputboxes are empty, aborting...');
        return;
    }

    var senddata = {
        data: 'sensor ',
        user: deviceID,
        pass: password
    };
    
}