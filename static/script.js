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

// In script.js, modify the simulateBracket function:
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

        // Call updateBracketDisplay with the filename from the response
        if (data.status === 'success' && data.filename) {
            updateBracketDisplay(data.filename);
        }
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

    // Extract just the filename portion if it includes a path
    const filenameOnly = filename.split('/').pop();

    // Fetch the CSV data
    fetch(`/static/${filenameOnly}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load bracket data: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(csvData => {
    console.log('Raw CSV data:', csvData.substring(0, 500) + '...'); // Show first 500 chars of CSV

    // Parse the CSV data
    const bracketData = parseCSV(csvData);
    console.log('Parsed bracket data (first 5 entries):', bracketData.slice(0, 5));

    // Check if we have the expected data structure
    if (bracketData.length > 0) {
        const firstEntry = bracketData[0];
        if (!firstEntry.TEAM_NAME || !firstEntry.REGION || !firstEntry.ROUND) {
            console.error('CSV data structure is unexpected:', firstEntry);
            alert('Error: Bracket data format is not as expected');
            return;
        }
    } else {
        console.error('No data found in CSV');
        alert('Error: No data found in bracket file');
        return;
    }

    // Update the UI with the parsed data
    populateBracket(bracketData);
})
        .catch(error => {
            console.error('Error updating bracket display:', error);
            alert(`Error updating bracket: ${error.message}`);
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
        // Handle possible quoted fields with commas inside them
        let values = [];
        let currentValue = '';
        let inQuotes = false;

        // Simple CSV parsing
        const row = lines[i];
        for (let j = 0; j < row.length; j++) {
            const char = row[j];

            if (char === '"' && (j === 0 || row[j-1] !== '\\')) {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(currentValue);
                currentValue = '';
            } else {
                currentValue += char;
            }
        }
        // Add the last value
        values.push(currentValue);

        // Map values to headers
        const entry = {};
        for (let j = 0; j < headers.length; j++) {
            // Remove quotes if present
            let value = values[j] || '';
            if (value.startsWith('"') && value.endsWith('"')) {
                value = value.substring(1, value.length - 1);
            }
            entry[headers[j]] = value;
        }

        result.push(entry);
    }

    return result;
}

// Function to populate the bracket with team data
function populateBracket(bracketData) {
    console.log('Starting to populate bracket with data:', bracketData);

    // Create a mapping of team positions in the bracket
    const teamMapping = {};

    // Process each team in the data
    bracketData.forEach(team => {
        console.log('Processing team entry:', team);

        // Extract values, ensure they're properly converted from strings
        const teamName = team.TEAM_NAME;
        const region = team.REGION;
        const round = parseInt(team.ROUND);
        const seed = parseInt(team.SEED);
        const orderInRegion = parseInt(team.ORDER_IN_REGION);

        console.log(`Team: ${teamName}, Region: ${region}, Round: ${round}, Seed: ${seed}, Order: ${orderInRegion}`);

        // First round (initial seeding)
        if (round === 1) {
            // Format: region:round:seed
            const cellId = `${region.charAt(0)}:1:${seed}`;
            console.log(`Round 1: Mapping ${cellId} to ${teamName}`);
            teamMapping[cellId] = teamName;
        }

        // Update the relevant part of the populateBracket function:

        // Handle subsequent rounds (2-5)
        else if (round > 1 && round <= 5) {
            // For rounds 2-5, we need a smarter approach to determine position
            // Each round has fewer spots (8, 4, 2, 1)
            const positionInRound = Math.ceil(orderInRegion / (2 ** (round - 1)));
            const cellId = `${region.charAt(0)}:${round}:${positionInRound}`;
            console.log(`Round ${round}: Mapping ${cellId} to ${teamName} (order: ${orderInRegion}, position: ${positionInRound})`);
            teamMapping[cellId] = teamName;
        }

        // Handle Final Four (round 6)
        else if (round === 6) {
            // Determine semifinal position based on region
            if (region === 'SOUTH') {
                teamMapping['S-W:S'] = teamName;
                console.log(`Final Four: Mapping S-W:S to ${teamName} (South)`);
            }
            else if (region === 'WEST') {
                teamMapping['S-W:W'] = teamName;
                console.log(`Final Four: Mapping S-W:W to ${teamName} (West)`);
            }
            else if (region === 'EAST') {
                teamMapping['E-M:E'] = teamName;
                console.log(`Final Four: Mapping E-M:E to ${teamName} (East)`);
            }
            else if (region === 'MIDWEST') {
                teamMapping['E-M:M'] = teamName;
                console.log(`Final Four: Mapping E-M:M to ${teamName} (Midwest)`);
            }
        }

        // Handle Championship (round 7)
        else if (round === 7) {
            // Map to championship game position
            if (region === 'SOUTH' || region === 'WEST') {
                teamMapping['S-W'] = teamName;
                console.log(`Championship: Mapping S-W to ${teamName}`);
            } else {
                teamMapping['E-M'] = teamName;
                console.log(`Championship: Mapping E-M to ${teamName}`);
            }
        }

        // Handle Champion (round 8)
        else if (round === 8) {
            const championId = (region === 'SOUTH' || region === 'WEST') ? 'S-W' : 'E-M';
            console.log(`Champion: ${teamName} (${region}) - Adding winner class to ${championId}`);

            // Mark as winner with a small delay
            setTimeout(() => {
                const championElement = document.getElementById(championId);
                if (championElement) {
                    championElement.classList.add('winner');
                    console.log(`Added winner class to ${championId}`);
                } else {
                    console.error(`Could not find champion element with ID ${championId}`);
                }
            }, 100);
        }
    });

    console.log('Final team mapping:', teamMapping);

    // Update the bracket with team names
    for (const [cellId, teamName] of Object.entries(teamMapping)) {
        const cell = document.getElementById(cellId);
        if (cell) {
            const teamNameSpan = cell.querySelector('.team-name');
            if (teamNameSpan) {
                console.log(`Setting ${cellId} team name to ${teamName}`);
                teamNameSpan.textContent = teamName;
            } else {
                console.error(`Could not find .team-name span in cell ${cellId}`);
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
                if (teamNameSpan && teamNameSpan.parentNode) {
                    teamNameSpan.parentNode.insertBefore(seedSpan, teamNameSpan);
                    console.log(`Added seed ${teamData.SEED} to ${cellId}`);
                }
            }
        } else {
            console.error(`Could not find cell with ID ${cellId}`);
        }
    }
}

// Replace the calculateRoundPosition function with this simpler approach:
function calculateRoundPosition(round, orderInRegion) {
    // In the current bracket structure, positions in each round follow a pattern:
    // Round 1: 16 teams (positions 1-16)
    // Round 2: 8 teams (positions 1-8)
    // Round 3: 4 teams (positions 1-4)
    // Round 4: 2 teams (positions 1-2)
    // Round 5: 1 team (position 1)

    // For rounds 2-5, we'll map orderInRegion to the appropriate position
    const totalPositionsInRound = 16 / (2 ** (round - 1));

    // Make sure we don't exceed the number of positions in this round
    return Math.min(orderInRegion, totalPositionsInRound);
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