# 🌟 SmartEco+ Digital Twin

> **AI-Powered Smart Campus Resource Management System**

A complete digital twin simulation of a smart campus that detects water, energy, and waste anomalies in real-time and automatically fixes them using AI - all without any physical hardware.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 The Concept

**"SmartEco+ is a digital twin of the entire campus that detects water, energy, and waste anomalies in real time and automatically fixes them — saving resources even before humans notice."**

This system simulates:
- 🏫 **9 Campus Locations** (Hostels, Classrooms, Washrooms, Labs, Canteen)
- 📊 **Virtual Sensors** (Water flow, Energy consumption, Waste levels)
- 🤖 **AI Detection** (Isolation Forest for anomalies, Linear Regression for predictions)
- ⚡ **Auto-Fix Actions** (Valve control, Circuit isolation, Waste compression)
- 💰 **Resource Savings** (Track liters, kWh, and waste reduction)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python api_server.py
```

### 3. Open Dashboard

Navigate to: **http://localhost:5000**

That's it! The system is now running and simulating the entire campus.

---

## 📁 Project Structure

```
automation/
├── api_server.py              # Flask API + WebSocket server
├── digital_twin_engine.py     # Simulation engine (sensors, locations)
├── digital_twin.py            # AI detection system (ML models)
├── dashboard.html             # Web dashboard (UI)
├── dashboard.css              # Styling (dark mode, animations)
├── dashboard.js               # Frontend logic (WebSocket, Canvas)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:5000
```

### REST Endpoints

#### Get Campus State
```http
GET /api/campus/state
```
Returns complete campus state with all locations and sensors.

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-12-12T22:00:00",
    "locations": {
      "hostel_1": {
        "location_id": "hostel_1",
        "name": "Hostel Block A",
        "type": "hostel",
        "sensors": {
          "energy": {
            "value": 245.3,
            "unit": "W",
            "status": "normal",
            "threshold": 450
          },
          "water": {...},
          "waste": {...}
        }
      }
    },
    "metrics": {
      "water_saved_liters": 125.5,
      "energy_saved_kwh": 2.3,
      "waste_reduced_percent": 15.2,
      "total_fixes": 8
    }
  }
}
```

#### Get Specific Location
```http
GET /api/location/{location_id}
```

#### Get Metrics
```http
GET /api/metrics
```

#### Get Alerts
```http
GET /api/alerts?limit=10
```

#### Get AI Insights
```http
GET /api/insights/{location_id}/{sensor_type}
```

#### Simulate Anomaly (Testing)
```http
POST /api/simulate/anomaly
Content-Type: application/json

{
  "location_id": "washroom_2",
  "sensor_type": "water"
}
```

#### Get All Locations
```http
GET /api/locations
```

#### Health Check
```http
GET /api/health
```

### WebSocket Events

Connect to: `ws://localhost:5000`

**Events Emitted by Server:**
- `campus_update` - Real-time sensor updates (every 1 second)
- `alert` - Anomaly detected and auto-fix triggered
- `fix_completed` - Auto-fix completed successfully
- `connection_established` - Initial connection confirmation

**Events You Can Emit:**
- `request_campus_state` - Request current campus state

---

## 🎨 Dashboard Features

### 1. **Real-Time Metrics**
- 💧 Water Saved (Liters)
- ⚡ Energy Saved (kWh)
- 🗑️ Waste Reduced (%)
- 🤖 Total Auto-Fixes

### 2. **Interactive Campus Map**
- Visual representation of all locations
- Color-coded status indicators
- Real-time anomaly highlighting
- Auto-fix animations

### 3. **Live Sensor Cards**
- Current readings for all sensors
- Status indicators (Normal/Warning/Fixing)
- Location-specific data

### 4. **Alert Feed**
- Real-time anomaly notifications
- Auto-fix action logs
- Timestamp tracking

### 5. **Alert Modals**
- Prominent anomaly alerts
- Auto-fix trigger notifications
- Visual feedback

---

## 🤖 AI System Explained

### Anomaly Detection (Isolation Forest)
- **What it does**: Learns normal patterns and detects outliers
- **How it works**: Trains on last 100 data points, identifies anomalies with 90% confidence
- **When it triggers**: When current value is statistically abnormal

### Predictive Analytics (Linear Regression)
- **What it does**: Predicts future resource usage
- **How it works**: Analyzes trends to forecast 10 steps ahead
- **When it triggers**: When predicted value will breach threshold

### Auto-Fix Decision Logic
```python
if current_value > threshold:
    → Immediate fix (High urgency)
elif AI_detects_anomaly AND confidence > 70%:
    → Preventive fix (Medium urgency)
elif predicted_value > threshold:
    → Predictive fix (Medium urgency)
```

---

## 🔗 Integration with React Frontend

Your teammates can integrate with this backend easily:

### 1. Install Socket.IO Client
```bash
npm install socket.io-client
```

### 2. Connect to API
```javascript
import io from 'socket.io-client';

// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen for updates
socket.on('campus_update', (data) => {
  // Update React state
  setCampusData(data);
});

socket.on('alert', (alert) => {
  // Show notification
  showNotification(alert);
});

// Fetch initial data
fetch('http://localhost:5000/api/campus/state')
  .then(res => res.json())
  .then(data => setCampusData(data.data));
```

### 3. Use the Data
```javascript
// Example: Display sensor data
{campusData.locations.map(location => (
  <SensorCard 
    key={location.location_id}
    name={location.name}
    sensors={location.sensors}
    status={location.auto_fix_active ? 'fixing' : 'normal'}
  />
))}
```

---

## 🎤 Demo Script for Judges

### Opening (30 seconds)
> "SmartEco+ is a digital twin of our entire campus that uses AI to detect and automatically fix resource wastage in real-time. No hardware needed - everything is simulated."

### Live Demo (2 minutes)

1. **Show Dashboard**
   - "Here's our campus with 9 locations - hostels, classrooms, labs, washrooms, and canteen."
   - "Each location has virtual sensors monitoring water, energy, and waste."

2. **Trigger Anomaly** (in browser console)
   ```javascript
   triggerTestAnomaly()
   ```
   - "Watch this - I'm simulating a water leak in Washroom-2..."
   - **[Alert appears]**
   - "The AI detected the anomaly and automatically closed the solenoid valve!"
   - **[Show metrics increasing]**
   - "And you can see the water saved counter increasing in real-time."

3. **Show AI Intelligence**
   - "The system uses Isolation Forest for anomaly detection and Linear Regression for predictive analytics."
   - "It doesn't just react - it predicts future wastage and prevents it."

### Impact (30 seconds)
> "In a real deployment, this system could save thousands of liters of water, kilowatts of energy, and reduce waste - all automatically, 24/7, without human intervention. It's scalable to any campus, building, or smart city."

---

## 🏆 Why This Wins Hackathons

✅ **Visually Impressive** - Real-time dashboard with animations  
✅ **AI-Powered** - Uses actual ML models (not just thresholds)  
✅ **Complete System** - Backend + Frontend + AI + Visualization  
✅ **Practical Impact** - Solves real sustainability problem  
✅ **Scalable** - Can expand to entire cities  
✅ **No Hardware** - Works on just a laptop  
✅ **Well-Documented** - Easy for judges to understand  

---

## 📊 Technical Highlights

- **Backend**: Flask with REST API + WebSocket
- **AI/ML**: scikit-learn (Isolation Forest, Linear Regression)
- **Frontend**: Vanilla JavaScript with Canvas API
- **Real-time**: Socket.IO for live updates
- **Simulation**: Time-based patterns with realistic variations
- **Auto-Fix**: Simulated hardware control (valves, circuits, compressors)

---

## 🛠️ Customization

### Add New Location
Edit `digital_twin_engine.py`:
```python
campus_layout = [
    # ... existing locations
    ('new_location_id', 'location_type', 'Display Name'),
]
```

### Adjust Thresholds
Modify sensor thresholds in `CampusLocation` class methods.

### Change Update Frequency
In `api_server.py`, modify `time.sleep(1)` in simulation loop.

---

## 📝 License

MIT License - Feel free to use this for your hackathon!

---

## 🙏 Credits

Built for hackathons by students who care about sustainability 🌍

**Made with ❤️ and AI**

---

## 🆘 Troubleshooting

**Port already in use?**
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**WebSocket not connecting?**
- Check if server is running
- Verify no CORS issues
- Try http://localhost:5000 instead of 127.0.0.1

**No alerts showing?**
- Wait 30-60 seconds for AI to collect data
- Or manually trigger: `POST /api/simulate/anomaly`

---

**Good luck with your hackathon! 🚀**
