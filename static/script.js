// Function to handle navigation between "pages"
function navigateToPage(page) {
    const selectionBorder = document.getElementById('selection-border');
    const buttons = document.querySelectorAll('.banner button');
    const selectedButton = Array.from(buttons).find(button =>
        button.textContent.toLowerCase().includes(page.replace('-', ' '))
    );

    // Update the border to the selected button
    selectButton(selectedButton);

    // Update the URL without refreshing
    history.pushState({ page }, '', `/${page}`);

    // Fetch the page content dynamically
    fetch(`/${page}`)
        .then(response => response.text())
        .then(html => {
            // Create a temporary DOM parser to extract the `<main>` content
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            const mainContent = tempDiv.querySelector('main'); // Extract only the main content
            if (mainContent) {
                document.getElementById('content').innerHTML = mainContent.innerHTML;

                // If we navigated to the analysis page, attach the table sorting listeners
                if (page === 'analysis') {
                    attachTableSortListeners();
                }
            } else {
                console.error('Main content not found in the fetched HTML.');
            }
        })
        .catch(err => console.error('Error loading page:', err));

    // If we navigated to the generate-bracket page, initialize the bracket
    if (page === 'generate-bracket') {
        initializeBracket();
    }
}

function initializeBracket() {
    console.log('Initializing bracket...');
    // This function will be expanded later to load teams, handle simulations, etc.

    // For now, just make sure the IDs are properly set on all cells
    const teams = document.querySelectorAll('.team');
    teams.forEach(team => {
        const teamId = team.id;
        if (teamId) {
            const teamNameSpan = team.querySelector('.team-name');
            if (teamNameSpan) {
                teamNameSpan.textContent = teamId;
            }
        }
    });
}

// Function to select a button
function selectButton(button) {
    const selectionBorder = document.getElementById('selection-border');

    // Get button's dimensions and position
    const buttonWidth = button.offsetWidth;
    const buttonHeight = button.offsetHeight;
    const buttonLeft = button.offsetLeft;
    const buttonTop = button.offsetTop;

    // Set selection border dimensions slightly larger than the button
    selectionBorder.style.width = `${buttonWidth + 10}px`; // 10px wider
    selectionBorder.style.height = `${buttonHeight + 6}px`; // 6px taller
    selectionBorder.style.left = `${buttonLeft - 5}px`; // Move 5px left
    selectionBorder.style.top = `${buttonTop - 3}px`; // Move 3px up
}

// Function to sort table
function sortTable(columnIndex, headerElement) {
    const table = document.querySelector('.table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    // Check if header already has a sorting class
    const isAscending = headerElement.classList.contains('ascending');

    // Remove sorting classes from all headers
    document.querySelectorAll('th').forEach(th => {
        th.classList.remove('ascending', 'descending');
    });

    // Add appropriate class to clicked header
    headerElement.classList.add(isAscending ? 'descending' : 'ascending');

    // Sort the rows
    rows.sort((rowA, rowB) => {
        const cellA = rowA.querySelectorAll('td')[columnIndex].textContent;
        const cellB = rowB.querySelectorAll('td')[columnIndex].textContent;

        // Check if the content is numeric
        const numA = parseFloat(cellA);
        const numB = parseFloat(cellB);

        if (!isNaN(numA) && !isNaN(numB)) {
            // Numeric sorting
            return isAscending ? numB - numA : numA - numB;
        } else {
            // String sorting
            return isAscending ?
                cellB.localeCompare(cellA) :
                cellA.localeCompare(cellB);
        }
    });

    // Remove all rows
    rows.forEach(row => tbody.removeChild(row));

    // Add rows back in sorted order
    rows.forEach(row => tbody.appendChild(row));
}

// Handle page load based on the current URL
window.onload = () => {
    const page = window.location.pathname.replace('/', '') || 'home';
    navigateToPage(page);

    // Add click event listeners to table headers if we're on the analysis page
    if (page === 'analysis') {
        attachTableSortListeners();
    }

    // Initialize bracket if we're on the generate-bracket page
    if (page === 'generate-bracket') {
        initializeBracket();
    }

};

// Function to attach sort listeners to table headers
function attachTableSortListeners() {
    const headers = document.querySelectorAll('#analysis-table th');
    headers.forEach((header, index) => {
        header.addEventListener('click', () => sortTable(index, header));
    });
}


// Handle page resizing to ensure the border aligns with the buttons
window.onresize = () => {
    const currentPage = window.location.pathname.replace('/', '') || 'home';
    const buttons = document.querySelectorAll('.banner button');
    const selectedButton = Array.from(buttons).find(button =>
        button.textContent.toLowerCase().includes(currentPage.replace('-', ' '))
    );

    // Realign the border with the selected button
    if (selectedButton) {
        selectButton(selectedButton);
    }
};
