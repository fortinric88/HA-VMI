/**
 * Main Module - Initialize and manage application
 */

let statusCheckInterval;

/**
 * Initialize the application
 */
async function initApp() {
    console.log('Initializing Ventilairsec VMI Monitor...');

    // Load devices on startup
    await loadDevices();

    // Set up status check
    startStatusCheck();

    // Set up auto-refresh
    setInterval(loadDevices, 30000); // Refresh every 30 seconds

    // Load settings
    loadSettings();
}

/**
 * Show tab by ID
 */
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');

    // Load specific tab data
    if (tabName === 'history') {
        setTimeout(() => {
            updateMetricSelect();
        }, 100);
    }
}

/**
 * Start status check
 */
function startStatusCheck() {
    statusCheckInterval = setInterval(async () => {
        try {
            const health = await API.getHealth();
            updateStatusIndicator(health);
        } catch (error) {
            console.error('Status check error:', error);
            updateStatusIndicator(null);
        }
    }, 5000); // Check every 5 seconds
}

/**
 * Update status indicator
 */
function updateStatusIndicator(health) {
    const statusDot = document.getElementById('status');
    const statusText = document.getElementById('status-text');

    if (health && health.enocean_connected) {
        statusDot.classList.remove('offline');
        statusText.textContent = 'Connecté';
        statusText.style.color = '#10b981';
    } else {
        statusDot.classList.add('offline');
        statusText.textContent = 'Déconnecté';
        statusText.style.color = '#ef4444';
    }
}

/**
 * Load and display settings
 */
async function loadSettings() {
    try {
        const devices = await API.getDevices();

        // Display device list
        const devicesList = document.getElementById('devicesList');
        if (devicesList) {
            let devicesHtml = '';
            for (const device of devices) {
                devicesHtml += `
                    <li>
                        <strong>${device.name}</strong>
                        <br>
                        <small>Type: ${device.type}</small>
                        <br>
                        <small style="color: #cbd5e1;">ID: ${device.id}</small>
                    </li>
                `;
            }
            devicesList.innerHTML = devicesHtml;
        }

    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

/**
 * Format date time
 */
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('fr-FR');
}

/**
 * Format time only
 */
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString('fr-FR');
}

/**
 * Sleep function for delays
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Handle page visibility
 */
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        clearInterval(statusCheckInterval);
    } else {
        startStatusCheck();
    }
});

/**
 * Clean up on page unload
 */
window.addEventListener('beforeunload', () => {
    clearInterval(statusCheckInterval);
});

/**
 * Start application
 */
document.addEventListener('DOMContentLoaded', initApp);

// Make functions available globally
window.showTab = showTab;
window.formatDateTime = formatDateTime;
window.formatTime = formatTime;
