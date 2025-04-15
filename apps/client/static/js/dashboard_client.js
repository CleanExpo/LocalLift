/**
 * Client Dashboard JavaScript
 * JavaScript for client dashboard interactive elements
 * 
 * Generated on 2025-04-14 23:54:28
 */

// Initialize the module when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Client Dashboard module initialized');
    
    // Get the content container
    const contentElement = document.getElementById('client-dashboard-content');
    
    if (contentElement) {
        loadData();
    }
});

/**
 * Load data for the client_dashboard module
 */
async function loadData() {
    try {
        const response = await fetch('/client-dashboard/api/data');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateUI(data.data);
        } else {
            showError('Failed to load data: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showError('An error occurred while loading data');
    }
}

/**
 * Update the UI with the loaded data
 * 
 * @param {Object} data - The data to display
 */
function updateUI(data) {
    const contentElement = document.getElementById('client-dashboard-content');
    
    if (!contentElement) return;
    
    // Replace the loading placeholder with actual content
    contentElement.innerHTML = `
        <div class="bg-white rounded-xl p-4 border border-gray-200">
            <h3 class="text-lg font-semibold mb-2">Your Data</h3>
            <div class="space-y-2">
                <p>Sample data would be displayed here.</p>
            </div>
        </div>
    `;
}

/**
 * Show an error message
 * 
 * @param {string} message - The error message to display
 */
function showError(message) {
    const contentElement = document.getElementById('client-dashboard-content');
    
    if (!contentElement) return;
    
    contentElement.innerHTML = `
        <div class="bg-red-50 text-red-800 rounded-xl p-4 border border-red-200">
            <h3 class="text-lg font-semibold mb-2">Error</h3>
            <p>${message}</p>
        </div>
    `;
}
