document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    
    // Al enviar el formulario, asegurarse de mantener el filtro activo
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const currentFilter = new URLSearchParams(window.location.search).get('filter');
            if (currentFilter && !searchForm.querySelector('input[name="filter"]')) {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'filter';
                hiddenInput.value = currentFilter;
                searchForm.appendChild(hiddenInput);
            }
        });
    }
});
