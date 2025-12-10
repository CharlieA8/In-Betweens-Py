const rowsPerPage = 10;
let currentPage = 1;
const table = document.getElementById('mainTable');
const rows = table.querySelectorAll('tr');
const totalPages = Math.ceil((rows.length - 1) / rowsPerPage);

function showPage(page) {
    const start = (page - 1) * rowsPerPage + 1;
    const end = start + rowsPerPage;
    rows.forEach((row, index) => {
        if (index === 0 || (index >= start && index < end)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
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

document.addEventListener('DOMContentLoaded', () => {
    showPage(currentPage);
});