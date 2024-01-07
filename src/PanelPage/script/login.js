document.addEventListener('DOMContentLoaded', function() {
    const hiwClickable = document.getElementById('hiw_clickable');
    const hiwOpen = document.getElementById('hiw_open');
    const closeBtn = document.getElementById('close_btn_hiw');

    hiwClickable.addEventListener('click', function() {
        hiwOpen.style.display = 'block';
    });

    closeBtn.addEventListener('click', function() {
        hiwOpen.style.display = 'none';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const hiwClickable = document.getElementById('cu_clickable');
    const hiwOpen = document.getElementById('cu_open');
    const closeBtn = document.getElementById('close_btn_cu');

    hiwClickable.addEventListener('click', function() {
        hiwOpen.style.display = 'block';
    });

    closeBtn.addEventListener('click', function() {
        hiwOpen.style.display = 'none';
    });
});