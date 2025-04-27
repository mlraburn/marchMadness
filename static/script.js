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
    console.log('Using filename:', filenameOnly);

    // Fetch the CSV data
    fetch(`/static/${filenameOnly}`)
        .then(response => {
            console.log('CSV fetch response:', response);
            if (!response.ok) {
                throw new Error(`Failed to load bracket data: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(csvData => {
            console.log('CSV data length:', csvData.length);
            console.log('CSV data preview:', csvData.substring(0, 300) + '...');

            // Parse the CSV data
            const bracketData = parseCSV(csvData);

            // Validate the parsed data
            if (!bracketData || bracketData.length === 0) {
                throw new Error('No valid entries found in bracket data');
            }

            // Check if we have the expected data structure
            const sampleEntry = bracketData[0];
            const requiredFields = ['TEAM_NAME', 'REGION', 'ROUND', 'SEED', 'ORDER_IN_REGION'];
            const missingFields = requiredFields.filter(field =>
                !sampleEntry.hasOwnProperty(field) || sampleEntry[field] === undefined
            );

            if (missingFields.length > 0) {
                throw new Error('Bracket data format is not as expected. Missing fields: ' + missingFields.join(', '));
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
    console.log('Starting CSV parsing...');

    // Split into lines and get headers
    const lines = csvData.trim().split('\n');
    console.log('CSV headers line:', lines[0]);

    // Check if we have data
    if (lines.length <= 1) {
        console.error('CSV has no data rows');
        return [];
    }

    // Parse headers - trim whitespace
    const headers = lines[0].split(',').map(header => header.trim());
    console.log('Parsed headers:', headers);

    // Check if expected headers exist
    const requiredHeaders = ['TEAM_NAME', 'REGION', 'ROUND', 'SEED', 'ORDER_IN_REGION'];
    const missingHeaders = requiredHeaders.filter(h => !headers.includes(h));
    if (missingHeaders.length > 0) {
        console.error('Missing required headers:', missingHeaders);
        // Try to find similar headers
        console.log('Available headers:', headers);
    }

    // Initialize result array
    const result = [];

    // Process each data row
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue; // Skip empty lines

        // Split the line by commas, but handle quoted values
        const values = [];
        let inQuotes = false;
        let currentValue = '';

        for (let j = 0; j < lines[i].length; j++) {
            const char = lines[i][j];

            if (char === '"' && (j === 0 || lines[i][j-1] !== '\\')) {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(currentValue.trim());
                currentValue = '';
            } else {
                currentValue += char;
            }
        }

        // Add the last value
        values.push(currentValue.trim());

        // Check if we have the right number of values
        if (values.length !== headers.length) {
            console.error(`Row ${i} has ${values.length} values but expected ${headers.length}`);
            console.log('Row content:', lines[i]);
            console.log('Parsed values:', values);
        }

        // Create entry object with headers as keys
        const entry = {};
        for (let j = 0; j < headers.length; j++) {
            // Get the value (or empty string if index is out of bounds)
            let value = j < values.length ? values[j] : '';

            // Remove quotes if present
            if (value.startsWith('"') && value.endsWith('"')) {
                value = value.substring(1, value.length - 1);
            }

            // Store in the entry
            entry[headers[j]] = value;
        }

        // Only add entry if it has the required fields
        if (entry.TEAM_NAME && entry.REGION && entry.ROUND) {
            result.push(entry);
        } else {
            console.warn('Skipping incomplete entry:', entry);
        }
    }

    console.log(`Parsed ${result.length} valid entries from CSV`);
    if (result.length > 0) {
        console.log('First entry:', result[0]);
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

        // Handle rounds 2-4 (tournament progression)
        else if (round > 1 && round <= 4) {
            // For second round
            if (round === 2) {
                // In NCAA brackets, the second round positions are fixed based on the matchups:
                // Position 1: winner of 1 vs 16
                // Position 2: winner of 8 vs 9
                // Position 3: winner of 5 vs 12
                // Position 4: winner of 4 vs 13
                // Position 5: winner of 6 vs 11
                // Position 6: winner of 3 vs 14
                // Position 7: winner of 7 vs 10
                // Position 8: winner of 2 vs 15

                // Let's use the seed to determine the position in round 2
                let position;

                // Check if the team came from a specific matchup
                if (seed === 1 || seed === 16) {
                    position = 1;
                } else if (seed === 8 || seed === 9) {
                    position = 8;
                } else if (seed === 5 || seed === 12) {
                    position = 5;
                } else if (seed === 4 || seed === 13) {
                    position = 4;
                } else if (seed === 6 || seed === 11) {
                    position = 6;
                } else if (seed === 3 || seed === 14) {
                    position = 3;
                } else if (seed === 7 || seed === 10) {
                    position = 7;
                } else if (seed === 2 || seed === 15) {
                    position = 2;
                } else {
                    // Fallback - use orderInRegion with a minimum of 1
                    position = Math.max(1, orderInRegion);
                }

                const cellId = `${region.charAt(0)}:2:${position}`;
                console.log(`Round 2: Mapping ${cellId} to ${teamName} (seed: ${seed}, position: ${position})`);
                teamMapping[cellId] = teamName;
            }
            // For round 3 (Sweet 16), use a similar explicit mapping
            else if (round === 3) {
                // In Sweet 16, positions should correspond to specific regions of the bracket
                // Position 1: Winner of the 1/16 vs 8/9 game
                // Position 4: Winner of the 5/12 vs 4/13 game
                // Position 3: Winner of the 6/11 vs 3/14 game
                // Position 2: Winner of the 7/10 vs 2/15 game

                let position;

                // Map based on seed and region pattern
                if (seed === 1 || seed === 8 || seed === 9 || seed === 16) {
                    position = 1;
                } else if (seed === 4 || seed === 5 || seed === 12 || seed === 13) {
                    position = 4;
                } else if (seed === 3 || seed === 6 || seed === 11 || seed === 14) {
                    position = 3;
                } else if (seed === 2 || seed === 7 || seed === 10 || seed === 15) {
                    position = 2;
                } else {
                    // Fallback to order in region
                    position = Math.max(1, Math.min(orderInRegion, 4));
                }

                const cellId = `${region.charAt(0)}:3:${position}`;
                console.log(`Round 3: Mapping ${cellId} to ${teamName} (seed: ${seed}, position: ${position})`);
                teamMapping[cellId] = teamName;
            }
            // For round 4 (Elite 8), map explicitly
            else if (round === 4) {
                // In Elite 8, there are only 2 positions per region
                // Position 1: Winner of positions 1 vs 4 from Sweet 16
                // Position 2: Winner of positions 3 vs 2 from Sweet 16

                let position;

                // Map based on seed
                // Top half of bracket - seeds 1,16,8,9,4,13,5,12
                if (seed === 1 || seed === 16 || seed === 8 || seed === 9 ||
                    seed === 4 || seed === 13 || seed === 5 || seed === 12) {
                    position = 1;
                }
                // Bottom half of bracket - seeds 6,11,3,14,7,10,2,15
                else if (seed === 6 || seed === 11 || seed === 3 || seed === 14 ||
                         seed === 7 || seed === 10 || seed === 2 || seed === 15) {
                    position = 2;
                }
                // Fallback to using orderInRegion if seed logic fails
                else {
                    position = Math.max(1, Math.min(orderInRegion, 2));
                }

                const cellId = `${region.charAt(0)}:4:${position}`;
                console.log(`Round 4: Mapping ${cellId} to ${teamName} (seed: ${seed}, position: ${position})`);
                teamMapping[cellId] = teamName;
            }
        }

        // Handle Final Four (round 5)
        else if (round === 5) {
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

        // Handle Championship (round 6)
        else if (round === 6) {
            // Map to championship game position
            if (region === 'SOUTH' || region === 'WEST') {
                teamMapping['S-W'] = teamName;
                console.log(`Championship: Mapping S-W to ${teamName}`);
            } else {
                teamMapping['E-M'] = teamName;
                console.log(`Championship: Mapping E-M to ${teamName}`);
            }
        }

        // Handle Champion (round 7)
        else if (round === 7) {
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
            // First, clear any existing team-seed spans to prevent duplicates
            const existingSeedSpans = cell.querySelectorAll('.team-seed');
            existingSeedSpans.forEach(span => span.remove());

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