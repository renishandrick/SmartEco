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
- 💰 **Resource Savings** (Track liters, kWh, waste reduction, and CO₂)
- 🌍 **Carbon Footprint** (Calculate environmental impact in real-time)

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
├── api_server.py                  # Flask API + WebSocket server
├── digital_twin_engine.py         # Simulation engine (sensors, locations)
├── digital_twin.py                # AI detection system (ML models)
├── dashboard.html                 # Web dashboard (UI)
├── dashboard.css                  # Styling (dark mode, animations)
├── dashboard.js                   # Frontend logic (WebSocket, Canvas)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── QUICK_START.md                 # Fast setup guide
├── AI_MODEL_GUIDE.md              # AI model documentation
├── PRACTICAL_IMPLEMENTATION.md    # Real-world deployment plan
├── CARBON_FOOTPRINT_FEATURE.md    # Carbon footprint documentation
└── FEATURES_TO_ADD.md             # Additional features guide
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

#### Get Metrics (Including Carbon Footprint)
```http
GET /api/metrics
```
Returns campus metrics, AI stats, and carbon footprint data.

**Response:**
```json
{
  "success": true,
  "data": {
    "campus_metrics": {
      "water_saved_liters": 125.5,
      "energy_saved_kwh": 2.3,
      "waste_reduced_percent": 15.2,
      "total_fixes": 8
    },
    "ai_stats": { ... },
    "carbon_footprint": {
      "total_co2_saved_kg": 15.3,
      "trees_equivalent": 0.73
    }
  }
}
```

#### Other Endpoints
- `GET /api/location/{location_id}` - Get specific location
- `GET /api/alerts?limit=10` - Get recent alerts
- `GET /api/locations` - Get all locations
- `GET /api/insights/{location_id}/{sensor_type}` - Get AI insights
- `POST /api/simulate/anomaly` - Trigger test anomaly
- `GET /api/health` - Health check

### WebSocket Events

Connect to: `ws://localhost:5000`

**Events Emitted by Server:**
- `campus_update` - Real-time sensor updates (every 1 second)
- `alert` - Anomaly detected and auto-fix triggered
- `fix_completed` - Auto-fix completed successfully
- `connection_established` - Initial connection confirmation

---

## 🎨 Dashboard Features

### 1. **Real-Time Metrics**
- 💧 Water Saved (Liters)
- ⚡ Energy Saved (kWh)
- 🗑️ Waste Reduced (%)
- 🤖 Total Auto-Fixes
- 🌍 CO₂ Saved (kg & tree equivalents)

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

---

## 🤖 AI System Explained

### Anomaly Detection (Isolation Forest)
- **What it does**: Learns normal patterns and detects outliers
- **How it works**: Trains on last 100 data points, identifies anomalies with confidence scoring
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

## 🌍 Carbon Footprint Feature

The system calculates environmental impact in real-time:

- **Water:** 0.001 kg CO₂ per liter saved
- **Energy:** 0.82 kg CO₂ per kWh saved (India grid)
- **Waste:** 0.5 kg CO₂ per kg waste reduced
- **Trees:** Total CO₂ ÷ 21 (1 tree absorbs ~21 kg/year)

**Example Output:**
```
🌍 CO₂ Saved: 15.3 kg (≈ 0.7 trees)
```

See `CARBON_FOOTPRINT_FEATURE.md` for details.

---

## 🎤 Demo Script for Judges

### Opening (30 seconds)
> "SmartEco+ is a digital twin of our entire campus that uses AI to detect and automatically fix resource wastage in real-time. No hardware needed - everything is simulated."

### Live Demo (2 minutes)

1. **Show Dashboard**
   - "Here's our campus with 9 locations monitoring water, energy, and waste."
   - "Notice the carbon footprint tracker - we're saving CO₂ in real-time."

2. **Trigger Anomaly** (in browser console)
   ```javascript
   triggerTestAnomaly()
   ```
   - "Watch - I'm simulating a water leak..."
   - **[Alert appears]**
   - "The AI detected it and automatically closed the valve!"
   - **[Metrics increase]**

3. **Show AI Intelligence**
   - "We use Isolation Forest and Linear Regression - real machine learning, not just thresholds."
   - "It predicts problems before they happen."

### Impact (30 seconds)
> "In a real deployment, this could save thousands of liters, kilowatts, and reduce carbon emissions - all automatically, 24/7. It's scalable to any campus or smart city."

---

## 🏆 Why This Wins Hackathons

✅ **Visually Impressive** - Real-time dashboard with animations  
✅ **AI-Powered** - Uses actual ML models (Isolation Forest + Linear Regression)  
✅ **Complete System** - Backend + Frontend + AI + Visualization  
✅ **Practical Impact** - Solves real sustainability problem  
✅ **Environmental Focus** - Carbon footprint tracking  
✅ **Scalable** - Can expand to entire cities  
✅ **No Hardware** - Works on just a laptop  
✅ **Well-Documented** - 8+ comprehensive guides  
✅ **Production-Ready** - Detailed implementation plan included

---

## 📊 Technical Highlights

- **Backend**: Flask with REST API + WebSocket
- **AI/ML**: scikit-learn (Isolation Forest, Linear Regression)
- **Frontend**: Vanilla JavaScript with Canvas API
- **Real-time**: Socket.IO for live updates (1-second intervals)
- **Simulation**: Time-based patterns with realistic variations
- **Auto-Fix**: Simulated hardware control (valves, circuits, compressors)
- **Sustainability**: Real-time carbon footprint calculation

---

## 📚 Additional Documentation

- **`QUICK_START.md`** - Get running in 3 minutes
- **`AI_MODEL_GUIDE.md`** - Complete AI model documentation
- **`PRACTICAL_IMPLEMENTATION.md`** - Real-world deployment plan with costs
- **`CARBON_FOOTPRINT_FEATURE.md`** - Environmental impact tracking
- **`REACT_INTEGRATION.md`** - Frontend integration guide
- **`PROJECT_CHECKLIST.md`** - Complete task list
- **`FEATURES_TO_ADD.md`** - Enhancement ideas

---

## 🆘 Troubleshooting

**Port already in use?**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**WebSocket not connecting?**
- Check if server is running
- Use http://localhost:5000 (not 127.0.0.1)
- Clear browser cache

**No alerts showing?**
- Wait 30-60 seconds for AI to collect data
- Or manually trigger: `triggerTestAnomaly()` in console

---

## 📝 License

MIT License - Feel free to use this for your hackathon!

---

## 🙏 Credits

Built for hackathons by students who care about sustainability 🌍

**Made with ❤️ and AI**

---

**Good luck with your hackathon! 🚀**
