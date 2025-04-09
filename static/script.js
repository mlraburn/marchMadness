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

// Function to update the bracket display with the generated bracket data
function updateBracketDisplay(filename) {
    console.log(`Bracket file generated: ${filename}`);

    // Fetch the CSV data
    fetch(`/static/${filename}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load bracket data: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(csvData => {
            // Parse the CSV data
            const bracketData = parseCSV(csvData);

            // Update the UI with the parsed data
            populateBracket(bracketData);
        })
        .catch(error => {
            console.error('Error updating bracket display:', error);
            const statusElement = document.getElementById('bracket-status');
            if (statusElement) {
                statusElement.textContent = `Error updating bracket: ${error.message}`;
                statusElement.style.color = 'red';
            }
        });
}

// Parse CSV data into a structured format
function parseCSV(csvData) {
    // Split into lines and get headers
    const lines = csvData.trim().split('\n');
    const headers = lines[0].split(',');

    // Initialize result array
    const result = [];

    // Process each data row
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        const entry = {};

        // Map values to headers
        for (let j = 0; j < headers.length; j++) {
            entry[headers[j]] = values[j];
        }

        result.push(entry);
    }

    return result;
}

// Function to populate the bracket with team data
function populateBracket(bracketData) {
    // Create a mapping of team positions in the bracket
    const teamMapping = {};

    // Process each team in the data
    bracketData.forEach(team => {
        const teamName = team.TEAM_NAME;
        const region = team.REGION;
        const round = parseInt(team.ROUND);
        const seed = parseInt(team.SEED);
        const orderInRegion = parseInt(team.ORDER_IN_REGION);

        // First round (initial seeding)
        if (round === 1) {
            // Format: region:round:seed
            const cellId = `${region.charAt(0)}:1:${seed}`;
            teamMapping[cellId] = teamName;
        }

        // Handle subsequent rounds within regions (2-5)
        if (round > 1 && round <= 5) {
            // For rounds 2-5, we need to find the corresponding cell ID
            // Based on the region and the position in the round
            const roundPosition = calculateRoundPosition(region, round, orderInRegion);
            const cellId = `${region.charAt(0)}:${round}:${roundPosition}`;
            teamMapping[cellId] = teamName;
        }

        // Handle Final Four (round 6)
        if (round === 6) {
            // Determine which semifinal the team is in based on region
            if (region === 'SOUTH' || region === 'WEST') {
                // South-West semifinal
                if (region === 'SOUTH') {
                    teamMapping['S-W:S'] = teamName;
                } else {
                    teamMapping['S-W:W'] = teamName;
                }
            } else {
                // East-Midwest semifinal
                if (region === 'EAST') {
                    teamMapping['E-M:E'] = teamName;
                } else {
                    teamMapping['E-M:M'] = teamName;
                }
            }
        }

        // Handle Championship (round 7)
        if (round === 7) {
            // Determine which side of the bracket the team came from
            if (region === 'SOUTH' || region === 'WEST') {
                teamMapping['S-W'] = teamName;
            } else {
                teamMapping['E-M'] = teamName;
            }
        }

        // Handle Champion (round 8)
        if (round === 8) {
            // Mark the champion with a special class
            const championId = (region === 'SOUTH' || region === 'WEST') ? 'S-W' : 'E-M';

            setTimeout(() => {
                // Add winner class to the champion
                const championElement = document.getElementById(championId);
                if (championElement) {
                    championElement.classList.add('winner');
                }
            }, 100); // Small delay to ensure the DOM is updated
        }
    });

    // Update the bracket with team names
    for (const [cellId, teamName] of Object.entries(teamMapping)) {
        const cell = document.getElementById(cellId);
        if (cell) {
            const teamNameSpan = cell.querySelector('.team-name');
            if (teamNameSpan) {
                teamNameSpan.textContent = teamName;
            }

            // Add seed to team name
            const teamData = bracketData.find(team => team.TEAM_NAME === teamName);
            if (teamData) {
                const seedSpan = document.createElement('span');
                seedSpan.className = 'team-seed';
                seedSpan.textContent = teamData.SEED;
                seedSpan.style.marginRight = '5px';
                seedSpan.style.fontSize = '10px';
                seedSpan.style.color = '#666';

                // Insert seed before team name
                if (teamNameSpan.parentNode) {
                    teamNameSpan.parentNode.insertBefore(seedSpan, teamNameSpan);
                }
            }
        }
    }
}

// Helper function to calculate position in a round
function calculateRoundPosition(region, round, orderInRegion) {
    // In round 2, teams are numbered 1-8
    // In round 3, teams are numbered 1-4
    // In round 4, teams are numbered 1-2
    // In round 5, there's only one winner per region

    // For simplicity, just return the position as is
    // This will need to be adjusted based on the actual bracket structure
    if (round === 5) return 1; // Only one winner per region

    // For rounds 2-4, the position depends on the orderInRegion
    // This is a simplified approach and might need adjustments
    return Math.ceil(orderInRegion / (2 ** (round - 2)));
}

// Function to generate a new bracket
function generateBracket() {
    const statusElement = document.getElementById('bracket-status');
    const generateButton = document.getElementById('generate-bracket-btn');

    if (statusElement && generateButton) {
        // Disable the button and show loading message
        generateButton.disabled = true;
        statusElement.textContent = 'Generating bracket... This may take a moment.';
        statusElement.style.color = '#003366';

        // Make a POST request to the server to generate a bracket
        // Using the /simulate-bracket endpoint instead of /generate-bracket
        fetch('/simulate-bracket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    statusElement.textContent = `${data.message} File: ${data.filename}`;
                    statusElement.style.color = 'green';

                    // Here we could potentially update the bracket display with the new results
                    // For now, we'll just show the success message
                    updateBracketDisplay(data.filename);

                } else {
                    statusElement.textContent = `Error: ${data.message}`;
                    statusElement.style.color = 'red';
                }
            })
            .catch(error => {
                statusElement.textContent = `Error: ${error.message}`;
                statusElement.style.color = 'red';
            })
            .finally(() => {
                // Re-enable the button
                generateButton.disabled = false;
            });
    }
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