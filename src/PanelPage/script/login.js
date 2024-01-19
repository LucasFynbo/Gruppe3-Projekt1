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
    document.getElementById('submit-arrow').addEventListener('click', sendData);
});

// Sender User/Password via https POST request til serveren
function sendData() {

    // Hent værdierne fra inputfelterne
    var deviceID = document.getElementById('inputbox_deviceid').value;
    var password = document.getElementById('inputbox_password').value;
    
    const responseStatusText = document.querySelector("#response-status");

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
        data: 'login request',
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
        const responseStatusText = document.querySelector("#response-status");

        if (data.status === 'Login: Credentials accepted') {
            console.log('200 OK; login authenticated');
            window.location.href = '/panel_home';
        } else if (data.status === 'Error: Invalid credentials') {
            document.getElementById('inputbox_deviceid').classList.add('error');
            document.getElementById('inputbox_password').classList.add('error');

            responseStatusText.textContent = "You have entered an invalid username or password";

            throw new Error("HTTP error; 401 Unauthorized; Invalid credentials");
        } else {
            console.log('520 Unknown; Unknown error occurred');
            responseStatusText.textContent = "An unknown error occured. Please fill out the 'contact us' form for assistance";
            
            throw new Error("HTTP error; 520 Unknown; Unknown error occurred");
        }
    })
    .catch(error => {
        // Håndterer fejl her
        console.error('Error:', error);
    });
}