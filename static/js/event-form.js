document.addEventListener("DOMContentLoaded", function() {
    const isOnlineCheckbox = document.getElementById('id_is_online');
    const streamUrlContainer = document.getElementById('id_stream_url');
    
    if (isOnlineCheckbox && streamUrlContainer) {
        const containerRow = streamUrlContainer.closest('.mb-4');
        function toggleStreamUrl() {
            if (isOnlineCheckbox.checked) {
                containerRow.classList.remove('d-none');
            } else {
                containerRow.classList.add('d-none');
            }
        }
        isOnlineCheckbox.addEventListener('change', toggleStreamUrl);
        toggleStreamUrl(); // Initial state
    }
});
