// SmartEco+ Digital Twin - Dashboard JavaScript
// Real-time WebSocket connection and UI updates

// WebSocket connection
let socket;
let isConnected = false;

// DOM Elements
const connectionStatus = document.getElementById('connectionStatus');
const waterSaved = document.getElementById('waterSaved');
const energySaved = document.getElementById('energySaved');
const wasteReduced = document.getElementById('wasteReduced');
const totalFixes = document.getElementById('totalFixes');
const carbonSaved = document.getElementById('carbonSaved');
const carbonUnit = document.getElementById('carbonUnit');
const sensorsGrid = document.getElementById('sensorsGrid');
const alertsContainer = document.getElementById('alertsContainer');
const alertModal = document.getElementById('alertModal');
const campusCanvas = document.getElementById('campusMap');
const ctx = campusCanvas.getContext('2d');

// Campus layout for visualization
const campusLayout = {
    'hostel_1': { x: 100, y: 100, color: '#3b82f6', icon: '🏠' },
    'hostel_2': { x: 100, y: 300, color: '#3b82f6', icon: '🏠' },
    'classroom_1': { x: 400, y: 150, color: '#8b5cf6', icon: '📚' },
    'classroom_2': { x: 400, y: 350, color: '#8b5cf6', icon: '📚' },
    'washroom_1': { x: 700, y: 100, color: '#06b6d4', icon: '🚿' },
    'washroom_2': { x: 700, y: 300, color: '#06b6d4', icon: '🚿' },
    'lab_1': { x: 1000, y: 150, color: '#ec4899', icon: '🔬' },
    'lab_2': { x: 1000, y: 350, color: '#ec4899', icon: '🔬' },
    'canteen_1': { x: 550, y: 500, color: '#f59e0b', icon: '🍽️' }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    drawCampusMap();
});

// WebSocket Connection
function initWebSocket() {
    socket = io('http://localhost:5000');

    socket.on('connect', () => {
        isConnected = true;
        updateConnectionStatus(true);
        console.log('✅ Connected to SmartEco+ server');
    });

    socket.on('disconnect', () => {
        isConnected = false;
        updateConnectionStatus(false);
        console.log('❌ Disconnected from server');
    });

    socket.on('connection_established', (data) => {
        console.log('🎉', data.message);
    });

    socket.on('campus_update', (data) => {
        updateDashboard(data);
    });

    socket.on('alert', (alert) => {
        showAlert(alert);
        addAlertToFeed(alert);
    });

    socket.on('fix_completed', (data) => {
        console.log('✅ Fix completed:', data);
    });
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusDot = connectionStatus.querySelector('.status-dot');
    const statusText = connectionStatus.querySelector('.status-text');

    if (connected) {
        statusDot.style.background = '#10b981';
        statusText.textContent = 'Connected';
        connectionStatus.style.background = 'rgba(16, 185, 129, 0.1)';
        connectionStatus.style.borderColor = 'rgba(16, 185, 129, 0.3)';
    } else {
        statusDot.style.background = '#ef4444';
        statusText.textContent = 'Disconnected';
        connectionStatus.style.background = 'rgba(239, 68, 68, 0.1)';
        connectionStatus.style.borderColor = 'rgba(239, 68, 68, 0.3)';
    }
}

// Update entire dashboard
function updateDashboard(data) {
    // Update metrics
    updateMetrics(data.metrics);

    // Update sensors
    updateSensors(data.locations);

    // Update campus map
    updateCampusMap(data.locations);
}

// Update metrics with animation
function updateMetrics(metrics) {
    animateValue(waterSaved, parseFloat(waterSaved.textContent), metrics.water_saved_liters, 1000);
    animateValue(energySaved, parseFloat(energySaved.textContent), metrics.energy_saved_kwh.toFixed(2), 1000);
    animateValue(wasteReduced, parseFloat(wasteReduced.textContent), metrics.waste_reduced_percent.toFixed(1), 1000);
    animateValue(totalFixes, parseInt(totalFixes.textContent), metrics.total_fixes, 500);

    // Fetch and update carbon footprint
    fetch('http://localhost:5000/api/metrics')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data.carbon_footprint) {
                const carbon = data.data.carbon_footprint;
                animateValue(carbonSaved, parseFloat(carbonSaved.textContent), carbon.total_co2_saved_kg, 1000);
                carbonUnit.textContent = `kg (≈ ${carbon.trees_equivalent} trees)`;
            }
        })
        .catch(err => console.error('Carbon footprint fetch error:', err));
}

// Animate number changes
function animateValue(element, start, end, duration) {
    const startNum = parseFloat(start) || 0;
    const endNum = parseFloat(end) || 0;
    const range = endNum - startNum;
    const increment = range / (duration / 16);
    let current = startNum;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= endNum) || (increment < 0 && current <= endNum)) {
            current = endNum;
            clearInterval(timer);
        }
        element.textContent = typeof end === 'string' && end.includes('.')
            ? current.toFixed(end.split('.')[1].length)
            : Math.round(current);
    }, 16);
}

// Update sensors grid
function updateSensors(locations) {
    sensorsGrid.innerHTML = '';

    Object.entries(locations).forEach(([locationId, location]) => {
        const card = createSensorCard(locationId, location);
        sensorsGrid.appendChild(card);
    });
}

// Create sensor card
function createSensorCard(locationId, location) {
    const card = document.createElement('div');
    card.className = 'sensor-card';
    card.id = `sensor-${locationId}`;

    let sensorsHTML = '';
    Object.entries(location.sensors).forEach(([sensorName, sensor]) => {
        const statusClass = getStatusClass(sensor.status);
        sensorsHTML += `
            <div class="sensor-reading">
                <span class="reading-label">${formatSensorName(sensorName)}</span>
                <span class="reading-value">${sensor.value} ${sensor.unit}</span>
            </div>
        `;
    });

    // Determine overall status
    const statuses = Object.values(location.sensors).map(s => s.status);
    let overallStatus = 'normal';
    if (statuses.includes('auto_fixing')) overallStatus = 'fixing';
    else if (statuses.includes('anomaly_detected') || statuses.includes('leak_detected') || statuses.includes('overflow_warning')) overallStatus = 'anomaly';

    card.innerHTML = `
        <div class="sensor-header">
            <div class="sensor-location">${location.name}</div>
            <div class="sensor-type">${location.type}</div>
        </div>
        <div class="sensor-readings">
            ${sensorsHTML}
        </div>
        <div class="sensor-status ${overallStatus}">
            ${formatStatus(overallStatus, location.auto_fix_active)}
        </div>
    `;

    return card;
}

// Format sensor name
function formatSensorName(name) {
    const names = {
        'energy': '⚡ Energy',
        'water': '💧 Water',
        'waste': '🗑️ Waste'
    };
    return names[name] || name;
}

// Get status class
function getStatusClass(status) {
    if (status === 'normal' || status === 'fixed') return 'normal';
    if (status === 'auto_fixing') return 'fixing';
    return 'anomaly';
}

// Format status text
function formatStatus(status, autoFixActive) {
    if (status === 'fixing') return '🤖 AUTO-FIXING...';
    if (status === 'anomaly') return '⚠️ ANOMALY DETECTED';
    if (autoFixActive) return '✅ FIXED';
    return '✓ Normal';
}

// Draw campus map
function drawCampusMap() {
    // Clear canvas
    ctx.clearRect(0, 0, campusCanvas.width, campusCanvas.height);

    // Draw connections (paths)
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.2)';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);

    // Draw some connecting paths
    const connections = [
        ['hostel_1', 'classroom_1'],
        ['hostel_2', 'classroom_2'],
        ['classroom_1', 'washroom_1'],
        ['classroom_2', 'washroom_2'],
        ['classroom_1', 'lab_1'],
        ['classroom_2', 'lab_2'],
        ['classroom_1', 'canteen_1'],
        ['classroom_2', 'canteen_1']
    ];

    connections.forEach(([from, to]) => {
        const fromPos = campusLayout[from];
        const toPos = campusLayout[to];
        ctx.beginPath();
        ctx.moveTo(fromPos.x, fromPos.y);
        ctx.lineTo(toPos.x, toPos.y);
        ctx.stroke();
    });

    ctx.setLineDash([]);

    // Draw locations
    Object.entries(campusLayout).forEach(([id, pos]) => {
        drawLocation(id, pos, 'normal');
    });
}

// Update campus map with live data
function updateCampusMap(locations) {
    drawCampusMap(); // Redraw base map

    // Update each location with current status
    Object.entries(locations).forEach(([locationId, location]) => {
        if (campusLayout[locationId]) {
            const statuses = Object.values(location.sensors).map(s => s.status);
            let status = 'normal';
            if (statuses.includes('auto_fixing')) status = 'fixing';
            else if (statuses.includes('anomaly_detected') || statuses.includes('leak_detected') || statuses.includes('overflow_warning')) status = 'anomaly';

            drawLocation(locationId, campusLayout[locationId], status);
        }
    });
}

// Draw individual location
function drawLocation(id, pos, status) {
    const radius = 40;

    // Status colors
    const colors = {
        'normal': pos.color,
        'anomaly': '#ef4444',
        'fixing': '#6366f1'
    };

    // Glow effect for anomalies
    if (status === 'anomaly' || status === 'fixing') {
        ctx.shadowBlur = 20;
        ctx.shadowColor = colors[status];
    }

    // Draw circle
    ctx.fillStyle = colors[status];
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
    ctx.fill();

    // Reset shadow
    ctx.shadowBlur = 0;

    // Draw icon
    ctx.font = '30px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(pos.icon, pos.x, pos.y);

    // Draw status indicator
    if (status === 'anomaly') {
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(pos.x + 25, pos.y - 25, 8, 0, Math.PI * 2);
        ctx.fill();
    } else if (status === 'fixing') {
        ctx.fillStyle = '#6366f1';
        ctx.beginPath();
        ctx.arc(pos.x + 25, pos.y - 25, 8, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Show alert modal
function showAlert(alert) {
    const modal = document.getElementById('alertModal');
    const title = document.getElementById('alertModalTitle');
    const message = document.getElementById('alertModalMessage');
    const action = document.getElementById('alertModalAction');

    title.textContent = `${alert.location_name} - Alert`;
    message.textContent = alert.reason;
    action.textContent = `🤖 ${alert.action.toUpperCase()}`;

    modal.classList.add('show');

    // Auto-hide after 4 seconds
    setTimeout(() => {
        modal.classList.remove('show');
    }, 4000);
}

// Add alert to feed
function addAlertToFeed(alert) {
    // Remove placeholder
    const placeholder = alertsContainer.querySelector('.alert-placeholder');
    if (placeholder) {
        placeholder.remove();
    }

    const alertItem = document.createElement('div');
    alertItem.className = 'alert-item danger';

    const time = new Date(alert.timestamp).toLocaleTimeString();

    alertItem.innerHTML = `
        <div class="alert-header">
            <div class="alert-title">⚠️ ${alert.location_name}</div>
            <div class="alert-time">${time}</div>
        </div>
        <div class="alert-message">${alert.reason}</div>
        <div class="alert-action">🤖 ${alert.action}</div>
    `;

    // Add to top of feed
    alertsContainer.insertBefore(alertItem, alertsContainer.firstChild);

    // Keep only last 10 alerts
    while (alertsContainer.children.length > 10) {
        alertsContainer.removeChild(alertsContainer.lastChild);
    }
}

// Test function for manual anomaly trigger
function triggerTestAnomaly() {
    fetch('http://localhost:5000/api/simulate/anomaly', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            location_id: 'washroom_2',
            sensor_type: 'water'
        })
    })
        .then(response => response.json())
        .then(data => console.log('Test anomaly triggered:', data))
        .catch(error => console.error('Error:', error));
}

// Expose test function to console
window.triggerTestAnomaly = triggerTestAnomaly;
