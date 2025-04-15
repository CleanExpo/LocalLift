/**
 * Admin Crm Manager JavaScript
 * JavaScript for admin CRM interface with search and filtering
 * 
 * Generated on 2025-04-14 23:54:45
 */

// Initialize the module when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Crm Manager module initialized');
    
    // Get the content container
    const contentElement = document.getElementById('admin-crm-manager-content');
    
    if (contentElement) {
        loadData();
    }
});

/**
 * Load data for the admin_crm_manager module
 */
async function loadData() {
    try {
        const response = await fetch('/admin-crm-manager/api/data');
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
    const contentElement = document.getElementById('admin-crm-manager-content');
    
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
    const contentElement = document.getElementById('admin-crm-manager-content');
    
    if (!contentElement) return;
    
    contentElement.innerHTML = `
        <div class="bg-red-50 text-red-800 rounded-xl p-4 border border-red-200">
            <h3 class="text-lg font-semibold mb-2">Error</h3>
            <p>${message}</p>
        </div>
    `;
}
