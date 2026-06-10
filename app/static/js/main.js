document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('catalogSearch');
    const statusFilter = document.getElementById('statusFilter');
    const bookRows = document.querySelectorAll('.book-row');

    if (searchInput && statusFilter) {
        function filterTable() {
            const searchQuery = searchInput.value.toLowerCase().trim();
            const selectedStatus = statusFilter.value.toLowerCase().trim();

            bookRows.forEach(row => {
                const idText = row.querySelector('.search-id').textContent.toLowerCase();
                const titleText = row.querySelector('.search-title').textContent.toLowerCase();
                const authorText = row.querySelector('.search-author').textContent.toLowerCase();
                const borrowerCell = row.querySelector('.search-borrower');
                const borrowerText = borrowerCell ? borrowerCell.textContent.toLowerCase() : '';
                const rowStatus = row.querySelector('.search-status').getAttribute('data-status');

                // Include borrowerText inside the matchesSearch logical chain evaluation
                const matchesSearch = idText.includes(searchQuery) || 
                                      titleText.includes(searchQuery) || 
                                      authorText.includes(searchQuery) ||
                                      borrowerText.includes(searchQuery);
                                      
                const matchesStatus = selectedStatus === "" || rowStatus === selectedStatus;

                if (matchesSearch && matchesStatus) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        // Attach listening triggers to input selectors
        searchInput.addEventListener('input', filterTable);
        statusFilter.addEventListener('change', filterTable);
    }
});