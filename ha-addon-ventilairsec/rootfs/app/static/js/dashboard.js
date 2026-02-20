/**
 * Dashboard Module - Handle dashboard functionality
 */

let allDevices = [];
let historyChart = null;

/**
 * Load and display device cards
 */
async function loadDevices() {
    try {
        const devicesContainer = document.getElementById('devicesContainer');
        const current = await API.getCurrent();

        if (Object.keys(current).length === 0) {
            devicesContainer.innerHTML = `
                <div class="loading">
                    Aucun appareil détecté. Vérifiez la connexion EnOcean.
                </div>
            `;
            return;
        }

        let html = '';
        for (const [deviceId, data] of Object.entries(current)) {
            html += createDeviceCard(deviceId, data);
        }
        devicesContainer.innerHTML = html;

        // Update device select
        updateDeviceSelect(current);

    } catch (error) {
        console.error('Error loading devices:', error);
    }
}

/**
 * Create HTML for a device card
 */
function createDeviceCard(deviceId, data) {
    const { name, type, last_update, metrics } = data;
    let metricsHtml = '';

    for (const [key, value] of Object.entries(metrics)) {
        const displayKey = key.replace(/_/g, ' ');
        let displayValue = value;

        // Format value with appropriate unit
        if (displayKey.includes('temperature')) {
            displayValue = `${value.toFixed(1)}°C`;
        } else if (displayKey.includes('humidity')) {
            displayValue = `${value.toFixed(1)}%`;
        } else if (displayKey.includes('co2')) {
            displayValue = `${Math.round(value)} ppm`;
        } else if (displayKey.includes('power') || displayKey.includes('percent')) {
            displayValue = `${Math.round(value)}%`;
        } else if (displayKey.includes('flow')) {
            displayValue = `${Math.round(value)} m³/h`;
        }

        metricsHtml += `
            <div class="metric-item">
                <span class="metric-label">${displayKey}</span>
                <span class="metric-value">${displayValue}</span>
            </div>
        `;
    }

    const lastUpdate = new Date(last_update).toLocaleTimeString('fr-FR');

    return `
        <div class="device-card">
            <h3>${name}</h3>
            <div class="type">${type}</div>
            <div class="last-update">Mise à jour: ${lastUpdate}</div>
            <div class="metrics-list">
                ${metricsHtml}
            </div>
        </div>
    `;
}

/**
 * Update device selector
 */
function updateDeviceSelect(current) {
    const select = document.getElementById('deviceSelect');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Sélectionner un appareil</option>';

    for (const [deviceId, data] of Object.entries(current)) {
        const option = document.createElement('option');
        option.value = deviceId;
        option.textContent = data.name;
        select.appendChild(option);
    }

    if (currentValue) {
        select.value = currentValue;
    }

    updateMetricSelect();
}

/**
 * Update metric selector based on selected device
 */
async function updateMetricSelect() {
    const metricSelect = document.getElementById('metricSelect');
    const deviceSelect = document.getElementById('deviceSelect');
    const currentValue = metricSelect.value;

    const current = await API.getCurrent();
    const deviceId = deviceSelect.value;

    metricSelect.innerHTML = '<option value="">Sélectionner une métrique</option>';

    if (deviceId && current[deviceId]) {
        const metrics = current[deviceId].metrics;
        for (const metric of Object.keys(metrics)) {
            const option = document.createElement('option');
            option.value = metric;
            option.textContent = metric.replace(/_/g, ' ');
            metricSelect.appendChild(option);
        }
    }

    if (currentValue) {
        metricSelect.value = currentValue;
    }
}

/**
 * Load device history
 */
async function loadDeviceHistory() {
    const deviceSelect = document.getElementById('deviceSelect');
    const metricSelect = document.getElementById('metricSelect');

    const deviceId = deviceSelect.value;
    const metric = metricSelect.value;

    if (!deviceId || !metric) {
        return;
    }

    try {
        const history = await API.getMetricHistory(deviceId, metric, 24);
        displayHistory(history, metric);
        loadStatistics(deviceId, metric);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

/**
 * Display history chart
 */
function displayHistory(data, metricName) {
    const ctx = document.getElementById('historyChart').getContext('2d');

    const labels = data.map(point => {
        const date = new Date(point.timestamp);
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    });

    const values = data.map(point => point.value);

    if (historyChart) {
        historyChart.destroy();
    }

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: metricName.replace(/_/g, ' '),
                data: values,
                borderColor: '#0ea5e9',
                backgroundColor: 'rgba(14, 165, 233, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#0ea5e9',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#f1f5f9',
                        font: { size: 12 }
                    }
                },
                title: {
                    display: true,
                    text: `Historique - ${metricName.replace(/_/g, ' ')} (24h)`,
                    color: '#f1f5f9',
                    font: { size: 14 }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(71, 85, 105, 0.2)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        font: { size: 10 }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(71, 85, 105, 0.2)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#cbd5e1',
                        font: { size: 10 }
                    }
                }
            }
        }
    });
}

/**
 * Load and display statistics
 */
async function loadStatistics(deviceId, metric) {
    try {
        const history = await API.getMetricHistory(deviceId, metric, 24);

        if (history.length === 0) {
            document.getElementById('statsContainer').innerHTML = 
                '<p>Aucune donnée disponible</p>';
            return;
        }

        const values = history.map(h => h.value);
        const min = Math.min(...values);
        const max = Math.max(...values);
        const avg = values.reduce((a, b) => a + b, 0) / values.length;

        const statsHtml = `
            <div class="stat-card">
                <span>Minimum</span>
                <strong>${min.toFixed(2)}</strong>
            </div>
            <div class="stat-card">
                <span>Maximum</span>
                <strong>${max.toFixed(2)}</strong>
            </div>
            <div class="stat-card">
                <span>Moyenne</span>
                <strong>${avg.toFixed(2)}</strong>
            </div>
            <div class="stat-card">
                <span>Échantillons</span>
                <strong>${values.length}</strong>
            </div>
        `;

        document.getElementById('statsContainer').innerHTML = statsHtml;

    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

/**
 * Refresh history
 */
function refreshHistory() {
    loadDeviceHistory();
}

/**
 * Cleanup old data
 */
async function cleanupOldData() {
    if (confirm('Êtes-vous sûr de vouloir supprimer les données de plus de 30 jours ?')) {
        try {
            const response = await fetch('/api/cleanup', { method: 'POST' });
            if (response.ok) {
                alert('Données nettoyées avec succès');
            }
        } catch (error) {
            console.error('Error cleaning up data:', error);
            alert('Erreur lors du nettoyage des données');
        }
    }
}

// Export functions
window.loadDevices = loadDevices;
window.updateMetricSelect = updateMetricSelect;
window.loadDeviceHistory = loadDeviceHistory;
window.refreshHistory = refreshHistory;
window.cleanupOldData = cleanupOldData;
