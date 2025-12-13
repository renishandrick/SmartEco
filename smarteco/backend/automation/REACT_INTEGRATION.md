# 🎯 React Integration Guide for SmartEco+ Digital Twin

This guide shows your React frontend team how to integrate with the SmartEco+ backend.

---

## 📦 Installation

```bash
npm install socket.io-client axios
```

---

## 🔌 Setup WebSocket Connection

Create a service file: `src/services/campusService.js`

```javascript
import io from 'socket.io-client';

const BACKEND_URL = 'http://localhost:5000';

class CampusService {
  constructor() {
    this.socket = null;
    this.listeners = {};
  }

  // Connect to WebSocket
  connect() {
    this.socket = io(BACKEND_URL);
    
    this.socket.on('connect', () => {
      console.log('✅ Connected to SmartEco+ backend');
    });
    
    this.socket.on('disconnect', () => {
      console.log('❌ Disconnected from backend');
    });
    
    // Forward events to registered listeners
    this.socket.on('campus_update', (data) => {
      this.emit('campus_update', data);
    });
    
    this.socket.on('alert', (alert) => {
      this.emit('alert', alert);
    });
    
    this.socket.on('fix_completed', (data) => {
      this.emit('fix_completed', data);
    });
  }

  // Disconnect
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  // Register event listener
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  // Remove event listener
  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  // Emit to listeners
  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  // Fetch campus state (REST API)
  async getCampusState() {
    const response = await fetch(`${BACKEND_URL}/api/campus/state`);
    const data = await response.json();
    return data.data;
  }

  // Fetch specific location
  async getLocation(locationId) {
    const response = await fetch(`${BACKEND_URL}/api/location/${locationId}`);
    const data = await response.json();
    return data.data;
  }

  // Fetch metrics
  async getMetrics() {
    const response = await fetch(`${BACKEND_URL}/api/metrics`);
    const data = await response.json();
    return data.data;
  }

  // Fetch alerts
  async getAlerts(limit = 10) {
    const response = await fetch(`${BACKEND_URL}/api/alerts?limit=${limit}`);
    const data = await response.json();
    return data.data;
  }

  // Trigger test anomaly
  async simulateAnomaly(locationId, sensorType) {
    const response = await fetch(`${BACKEND_URL}/api/simulate/anomaly`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        location_id: locationId,
        sensor_type: sensorType
      })
    });
    return await response.json();
  }
}

export default new CampusService();
```

---

## 🎣 React Hook for Campus Data

Create: `src/hooks/useCampusData.js`

```javascript
import { useState, useEffect } from 'react';
import campusService from '../services/campusService';

export function useCampusData() {
  const [campusData, setCampusData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Connect to WebSocket
    campusService.connect();

    // Fetch initial data
    loadInitialData();

    // Listen for real-time updates
    campusService.on('campus_update', handleCampusUpdate);
    campusService.on('alert', handleAlert);

    // Cleanup
    return () => {
      campusService.off('campus_update', handleCampusUpdate);
      campusService.off('alert', handleAlert);
      campusService.disconnect();
    };
  }, []);

  const loadInitialData = async () => {
    try {
      const [campus, metricsData, alertsData] = await Promise.all([
        campusService.getCampusState(),
        campusService.getMetrics(),
        campusService.getAlerts(10)
      ]);
      
      setCampusData(campus);
      setMetrics(metricsData);
      setAlerts(alertsData.alerts);
      setIsConnected(true);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load initial data:', error);
      setLoading(false);
    }
  };

  const handleCampusUpdate = (data) => {
    setCampusData(data);
    setMetrics(data.metrics);
  };

  const handleAlert = (alert) => {
    setAlerts(prev => [alert, ...prev].slice(0, 10));
  };

  return {
    campusData,
    metrics,
    alerts,
    isConnected,
    loading,
    simulateAnomaly: campusService.simulateAnomaly.bind(campusService)
  };
}
```

---

## 📊 Example Components

### 1. Metrics Dashboard Component

```javascript
import React from 'react';
import { useCampusData } from '../hooks/useCampusData';

function MetricsDashboard() {
  const { metrics, loading } = useCampusData();

  if (loading) return <div>Loading...</div>;

  return (
    <div className="metrics-grid">
      <MetricCard
        icon="💧"
        label="Water Saved"
        value={metrics?.campus_metrics.water_saved_liters || 0}
        unit="Liters"
        color="blue"
      />
      <MetricCard
        icon="⚡"
        label="Energy Saved"
        value={metrics?.campus_metrics.energy_saved_kwh.toFixed(2) || 0}
        unit="kWh"
        color="yellow"
      />
      <MetricCard
        icon="🗑️"
        label="Waste Reduced"
        value={metrics?.campus_metrics.waste_reduced_percent.toFixed(1) || 0}
        unit="%"
        color="green"
      />
      <MetricCard
        icon="🤖"
        label="Auto-Fixes"
        value={metrics?.campus_metrics.total_fixes || 0}
        unit="Actions"
        color="purple"
      />
    </div>
  );
}

function MetricCard({ icon, label, value, unit, color }) {
  return (
    <div className={`metric-card metric-${color}`}>
      <div className="metric-icon">{icon}</div>
      <div className="metric-content">
        <div className="metric-label">{label}</div>
        <div className="metric-value">{value}</div>
        <div className="metric-unit">{unit}</div>
      </div>
    </div>
  );
}

export default MetricsDashboard;
```

### 2. Location Sensors Component

```javascript
import React from 'react';
import { useCampusData } from '../hooks/useCampusData';

function LocationSensors() {
  const { campusData, loading } = useCampusData();

  if (loading) return <div>Loading...</div>;

  const locations = campusData?.locations || {};

  return (
    <div className="sensors-grid">
      {Object.entries(locations).map(([locationId, location]) => (
        <SensorCard key={locationId} location={location} />
      ))}
    </div>
  );
}

function SensorCard({ location }) {
  const getStatusClass = (status) => {
    if (status === 'auto_fixing') return 'fixing';
    if (status.includes('detected') || status.includes('warning')) return 'anomaly';
    return 'normal';
  };

  const overallStatus = Object.values(location.sensors)
    .map(s => getStatusClass(s.status))
    .includes('anomaly') ? 'anomaly' : 
    location.auto_fix_active ? 'fixing' : 'normal';

  return (
    <div className={`sensor-card status-${overallStatus}`}>
      <div className="sensor-header">
        <h3>{location.name}</h3>
        <span className="sensor-type">{location.type}</span>
      </div>
      
      <div className="sensor-readings">
        {Object.entries(location.sensors).map(([sensorName, sensor]) => (
          <div key={sensorName} className="sensor-reading">
            <span className="reading-label">
              {sensorName === 'energy' && '⚡ Energy'}
              {sensorName === 'water' && '💧 Water'}
              {sensorName === 'waste' && '🗑️ Waste'}
            </span>
            <span className="reading-value">
              {sensor.value} {sensor.unit}
            </span>
          </div>
        ))}
      </div>
      
      <div className={`sensor-status status-${overallStatus}`}>
        {overallStatus === 'fixing' && '🤖 AUTO-FIXING...'}
        {overallStatus === 'anomaly' && '⚠️ ANOMALY DETECTED'}
        {overallStatus === 'normal' && '✓ Normal'}
      </div>
    </div>
  );
}

export default LocationSensors;
```

### 3. Alerts Feed Component

```javascript
import React from 'react';
import { useCampusData } from '../hooks/useCampusData';

function AlertsFeed() {
  const { alerts } = useCampusData();

  return (
    <div className="alerts-container">
      <h2>🚨 Real-Time Alerts</h2>
      {alerts.length === 0 ? (
        <div className="alert-placeholder">No alerts yet...</div>
      ) : (
        alerts.map((alert, index) => (
          <AlertItem key={index} alert={alert} />
        ))
      )}
    </div>
  );
}

function AlertItem({ alert }) {
  const time = new Date(alert.timestamp).toLocaleTimeString();
  
  return (
    <div className="alert-item">
      <div className="alert-header">
        <div className="alert-title">⚠️ {alert.location_name}</div>
        <div className="alert-time">{time}</div>
      </div>
      <div className="alert-message">{alert.reason}</div>
      <div className="alert-action">🤖 {alert.action}</div>
    </div>
  );
}

export default AlertsFeed;
```

---

## 🎨 Example App.js

```javascript
import React from 'react';
import MetricsDashboard from './components/MetricsDashboard';
import LocationSensors from './components/LocationSensors';
import AlertsFeed from './components/AlertsFeed';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🌟 SmartEco+ Digital Twin</h1>
        <p>AI-Powered Smart Campus Resource Management</p>
      </header>

      <main className="app-main">
        <section className="metrics-section">
          <h2>💧 Resource Savings</h2>
          <MetricsDashboard />
        </section>

        <section className="sensors-section">
          <h2>📊 Live Sensor Data</h2>
          <LocationSensors />
        </section>

        <section className="alerts-section">
          <AlertsFeed />
        </section>
      </main>
    </div>
  );
}

export default App;
```

---

## 🎯 Data Structure Reference

### Campus State Object
```typescript
{
  timestamp: string;
  locations: {
    [locationId: string]: {
      location_id: string;
      name: string;
      type: 'hostel' | 'classroom' | 'washroom' | 'lab' | 'canteen';
      sensors: {
        energy?: {
          type: string;
          value: number;
          unit: 'W';
          status: string;
          threshold: number;
        };
        water?: {
          type: string;
          value: number;
          unit: 'L/min';
          status: string;
          threshold: number;
        };
        waste: {
          type: string;
          value: number;
          unit: '%';
          status: string;
          threshold: number;
        };
      };
      auto_fix_active: boolean;
      auto_fix_type: string | null;
    };
  };
  metrics: {
    water_saved_liters: number;
    energy_saved_kwh: number;
    waste_reduced_percent: number;
    total_fixes: number;
    uptime_seconds: number;
  };
}
```

### Alert Object
```typescript
{
  timestamp: string;
  location_id: string;
  location_name: string;
  sensor_type: 'water' | 'energy' | 'waste';
  reason: string;
  action: string;
  status: 'fixing' | 'completed';
}
```

---

## ✅ Testing Checklist

- [ ] WebSocket connects successfully
- [ ] Real-time updates appear (every 1 second)
- [ ] Metrics animate smoothly
- [ ] Alerts appear when anomalies detected
- [ ] Can trigger test anomaly via API
- [ ] All sensor data displays correctly
- [ ] Status indicators update in real-time

---

## 🆘 Common Issues

**CORS errors?**
- Backend already has CORS enabled
- Make sure you're using `http://localhost:5000` not `127.0.0.1`

**WebSocket not connecting?**
- Check if backend is running: `python api_server.py`
- Verify port 5000 is not blocked

**No data showing?**
- Check browser console for errors
- Verify API responses with: `curl http://localhost:5000/api/campus/state`

---

**Happy coding! 🚀**
