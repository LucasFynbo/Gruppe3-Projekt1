document.addEventListener('DOMContentLoaded', function() {
    // How it Works
    const hiwClickable = document.getElementById('hiw_clickable');
    const hiwOpen = document.getElementById('hiw_open');
    const closeBtnHiw = document.getElementById('close_btn_hiw');

    hiwClickable.addEventListener('click', function() {
        hiwOpen.style.display = 'block';
    });

    closeBtnHiw.addEventListener('click', function() {
        hiwOpen.style.display = 'none';
    });

    // Contact Us
    const cuClickable = document.getElementById('cu_clickable');
    const cuOpen = document.getElementById('cu_open');
    const closeBtnCu = document.getElementById('close_btn_cu');

    cuClickable.addEventListener('click', function() {
        cuOpen.style.display = 'block';
    });

    closeBtnCu.addEventListener('click', function() {
        cuOpen.style.display = 'none';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Add a click event listener to the element with ID 'submit-arrow'
    document.getElementById('submit-arrow').addEventListener('click', sendData);
});

// Sender User/Password via https POST request til serveren
function sendData() {

    // Hent værdierne fra inputfelterne
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
        data: 'login request',
        user: deviceID,
        pass: password
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
            throw new Error('[!] Error: Response returned false');
        }
        return response.json();
    })
    .then(responseData => {
        // Håndterer svaret fra serveren her
        console.log(responseData);
    })
    .catch(error => {
        // Håndterer fejl her
        console.error('Fetch error:', error);
    });
}
