/**
 * API Module - Handle API calls to backend
 */

const API_BASE = '/api';

class API {
    /**
     * Get health status
     */
    static async getHealth() {
        try {
            const response = await fetch(`${API_BASE}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            return null;
        }
    }

    /**
     * Get list of devices
     */
    static async getDevices() {
        try {
            const response = await fetch(`${API_BASE}/devices`);
            return await response.json();
        } catch (error) {
            console.error('Get devices error:', error);
            return [];
        }
    }

    /**
     * Get current readings for all devices
     */
    static async getCurrent() {
        try {
            const response = await fetch(`${API_BASE}/current`);
            return await response.json();
        } catch (error) {
            console.error('Get current readings error:', error);
            return {};
        }
    }

    /**
     * Get historical readings for a device
     * @param {string} deviceId - Device identifier
     * @param {number} hours - Number of hours to retrieve
     */
    static async getHistory(deviceId, hours = 24) {
        try {
            const response = await fetch(
                `${API_BASE}/history/${deviceId}?hours=${hours}`
            );
            return await response.json();
        } catch (error) {
            console.error('Get history error:', error);
            return [];
        }
    }

    /**
     * Get metric history
     * @param {string} deviceId - Device identifier
     * @param {string} metric - Metric name
     * @param {number} hours - Number of hours
     */
    static async getMetricHistory(deviceId, metric, hours = 24) {
        try {
            const response = await fetch(
                `${API_BASE}/reading/${deviceId}/${metric}?hours=${hours}`
            );
            return await response.json();
        } catch (error) {
            console.error('Get metric history error:', error);
            return [];
        }
    }
}

// Export for use in other modules
window.API = API;
