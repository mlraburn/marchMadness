// Function to handle navigation between "pages"
function navigateToPage(page) {
    console.log('Navigating to page:', page);

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

                // Important: Initialize the page based on its type AFTER the content is loaded
                if (page === 'analysis') {
                    attachTableSortListeners();
                } else if (page === 'generate-bracket') {
                    setTimeout(initializeBracket, 100); // Small delay to ensure DOM is updated
                }
            } else {
                console.error('Main content not found in the fetched HTML.');
            }
        })
        .catch(err => console.error('Error loading page:', err));
}

function initializeBracket() {
    console.log('Initializing bracket...');

    // First make sure teams have IDs
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

    // Now attach events to the bracket control buttons - MOVED THIS FROM window.onload
    console.log('Attaching event listeners to bracket buttons');

    // Use direct binding with simpler approach
    document.querySelectorAll('.bracket-controls button').forEach(button => {
        console.log('Found button:', button.id);

        button.addEventListener('click', function(event) {
            console.log('Button clicked:', this.id);

            // Handle specific button actions
            if (this.id === 'simulate-bracket-btn') {
                simulateBracket();
            } else {
                alert(this.textContent + ' feature will be implemented soon!');
            }
        });
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
// Handle page load based on the current URL
window.onload = () => {
    const page = window.location.pathname.replace('/', '') || 'home';
    navigateToPage(page);
};

// Function to attach sort listeners to table headers
function attachTableSortListeners() {
    const headers = document.querySelectorAll('#analysis-table th');
    headers.forEach((header, index) => {
        header.addEventListener('click', () => sortTable(index, header));
    });
}

// Function to handle simulate bracket button click
function simulateBracket() {
    console.log('Debug: simulateBracket function called');

    // Show some visual feedback that simulation is in progress
    const button = document.getElementById('simulate-bracket-btn');

    if (!button) {
        console.error('Error: Could not find simulate-bracket-btn in simulateBracket function');
        alert('Error: Button not found');
        return;
    }

    console.log('Debug: Found button, changing text');
    const originalText = button.textContent;
    button.textContent = 'Simulating...';
    button.disabled = true;

    console.log('Debug: Sending fetch request to /simulate-bracket');
    // Send a POST request to the server
    fetch('/simulate-bracket', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // Empty body for now
        body: JSON.stringify({})
    })
    .then(response => {
        console.log('Debug: Received response', response);
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        // Reset the button text
        button.textContent = originalText;
        button.disabled = false;

        // Display a message to the user
        alert(data.message);

        // Here you would update the bracket with the simulation results
        // For now we'll just log it
        console.log('Would update bracket with simulation results');
    })
    .catch(error => {
        console.error('Error during simulation:', error);
        // Reset the button text
        button.textContent = originalText;
        button.disabled = false;

        // Display error message
        alert('Error simulating bracket: ' + error);
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