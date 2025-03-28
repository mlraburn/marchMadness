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

    // Load the page content dynamically (simulate client-side navigation)
    loadPageContent(page);
}

// Function to select a button
function selectButton(button) {
    const selectionBorder = document.getElementById('selection-border');
    const buttonWidth = button.offsetWidth;
    const buttonHeight = button.offsetHeight;
    const buttonLeft = button.offsetLeft;

    const computedStyle = getComputedStyle(button);
    const paddingLeft = parseFloat(computedStyle.paddingLeft);
    const paddingRight = parseFloat(computedStyle.paddingRight);

    selectionBorder.style.width = `${buttonWidth + paddingLeft + paddingRight}px`;

    // Update the selection border's dimensions and position
    selectionBorder.style.height = `${buttonHeight}px`;
    selectionBorder.style.left = `${buttonLeft}px`;
}

// Function to load dynamic content for each "page"
function loadPageContent(page) {
    const content = document.getElementById('content');
    switch (page) {
        case 'home':
            content.innerHTML = `
                <h2>Welcome to Matt's March Madness!</h2>
                <p>This is the main page. Use the buttons above to explore other sections!</p>`;
            break;
        case 'generate-bracket':
            content.innerHTML = `
                <h2>Generate Bracket</h2>
                <p>Create your bracket here by clicking the options above.</p>`;
            break;
        case 'score-bracket':
            content.innerHTML = `
                <h2>Score Bracket</h2>
                <p>Check the scores and analyze your bracket performance.</p>`;
            break;
        case 'analysis':
            content.innerHTML = `
                <h2>Analysis</h2>
                <p>Detailed analysis of the tournament and statistics.</p>`;
            break;
        case 'help':
            content.innerHTML = `
                <h2>Help</h2>
                <p>Need assistance? Click the buttons above to learn more.</p>`;
            break;
        default:
            content.innerHTML = `
                <h2>Page Not Found</h2>
                <p>The page you are looking for does not exist.</p>`;
    }
}

// Handle page load based on the current URL
window.onload = () => {
    const page = window.location.pathname.replace('/', '') || 'home';
    navigateToPage(page);
};
