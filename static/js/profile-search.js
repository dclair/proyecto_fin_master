document.addEventListener('DOMContentLoaded', function() {
    const searchInputs = document.querySelectorAll('.js-modal-search');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            const targetListId = input.getAttribute('data-target');
            const listItems = document.querySelectorAll(`${targetListId} li.list-group-item`);
            
            listItems.forEach(item => {
                const searchData = item.getAttribute('data-search') || '';
                const searchableString = searchData.toLowerCase();
                
                if (searchableString.includes(searchTerm)) {
                    item.classList.remove('d-none');
                    item.classList.add('d-flex');
                } else {
                    item.classList.remove('d-flex');
                    item.classList.add('d-none');
                }
            });
        });
    });
});
