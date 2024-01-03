// Sender SSID/PASS via http POST request til ESP'en
function sendData() {
    // Change savebtn text
    const changeText = document.querySelector("#savebtn");
    changeText.textContent = "Your configuration has been saved.<br>If misinput, please restart your device and try again.";

    // Send Post request
    var ssid = document.getElementById('inputbox_ssid').value;
    var pass = document.getElementById('inputbox_pass').value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/submit", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var data = "data=" + encodeURIComponent(ssid) + "&pass=" + encodeURIComponent(pass);
    xhr.send(data);
}