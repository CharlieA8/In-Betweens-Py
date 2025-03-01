const levelsPerPage = 16;
let currentPage = 1;

document.addEventListener('DOMContentLoaded', () => {
    const levelGrid = document.querySelector('.levelGrid');
    const levels = Array.from(levelGrid.getElementsByClassName('level'));
    const totalPages = Math.ceil(levels.length / levelsPerPage);

    function showPage(page) {
        const start = (page - 1) * levelsPerPage;
        const end = start + levelsPerPage;
        levels.forEach((level, index) => {
            level.style.display = index >= start && index < end ? '' : 'none';
        });

        // Update button visibility
        document.getElementById('prevPageButton').disabled = (page === 1);
        document.getElementById('nextPageButton').disabled = (page === totalPages);
    }

    function prevPage() {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    }

    function nextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    }

    // Add event listeners to buttons
    document.getElementById('prevPageButton').addEventListener('click', prevPage);
    document.getElementById('nextPageButton').addEventListener('click', nextPage);

    // Initialize first page
    showPage(currentPage);
});
