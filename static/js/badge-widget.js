/**
 * Badge Widget
 * 
 * This script loads and displays the client's weekly badge status.
 * It communicates with the badge status API endpoint to retrieve
 * compliance data and updates the UI accordingly.
 */

async function loadBadgeStatus(clientId) {
  try {
    // Fetch badge status from the API
    const res = await fetch(`/api/client/${clientId}/badge-status`);
    
    if (!res.ok) {
      throw new Error(`Error fetching badge status: ${res.status}`);
    }
    
    const data = await res.json();

    // Update the badge widget UI
    const statusText = document.getElementById("badge-status-text");
    const badgeIcon = document.getElementById("badge-icon");

    if (data.badge) {
      // User earned the badge
      badgeIcon.textContent = "🎖️";
      statusText.textContent = data.message;
      badgeIcon.className = "text-3xl text-green-500";
      
      // Add animation
      badgeIcon.classList.add("animate-pulse");
      setTimeout(() => badgeIcon.classList.remove("animate-pulse"), 2000);
    } else {
      // User hasn't earned the badge yet
      badgeIcon.textContent = "⏳";
      statusText.textContent = data.message;
      badgeIcon.className = "text-3xl text-yellow-500";
    }
    
    // Add completion statistics if available
    if (data.compliant !== undefined && data.total !== undefined) {
      const statsEl = document.createElement("p");
      statsEl.className = "text-xs text-gray-500 mt-1";
      statsEl.textContent = `${data.compliant}/${data.total} posts this week`;
      statusText.parentNode.insertBefore(statsEl, statusText.nextSibling);
    }
  } catch (error) {
    console.error("Failed to load badge status:", error);
    
    // Show error state
    const statusText = document.getElementById("badge-status-text");
    const badgeIcon = document.getElementById("badge-icon");
    
    statusText.textContent = "Unable to load badge status";
    badgeIcon.textContent = "❌";
    badgeIcon.className = "text-3xl text-gray-400";
  }
}

// Initialize badge widget when the page loads
document.addEventListener("DOMContentLoaded", function() {
  const badgeWidget = document.getElementById("badge-widget");
  
  if (badgeWidget) {
    // Get client ID from data attribute or use a default for testing
    const clientId = badgeWidget.dataset.clientId || "536f7e35-3cca-42ab-8aa3-6d63d68d952e";
    loadBadgeStatus(clientId);
  }
});
