# 🚀 SmartEco+ Quick Start Guide

> **Get your project running in 3 minutes!**

---

## ⚡ **FASTEST PATH TO DEMO**

### **Step 1: Install Dependencies** (30 seconds)
```bash
cd c:\Users\renish\OneDrive\Desktop\automation
pip install -r requirements.txt
```

### **Step 2: Start Backend** (10 seconds)
```bash
python api_server.py
```

### **Step 3: Open Dashboard** (5 seconds)
Open browser: **http://localhost:5000**

### **Step 4: Test Anomaly** (5 seconds)
In browser console, run:
```javascript
triggerTestAnomaly()
```

**🎉 Done! Your system is running!**

---

## 📋 **WHAT EACH TEAM NEEDS TO KNOW**

### **Backend Team - 3 Things**
1. **Start server:** `python api_server.py`
2. **API runs on:** `http://localhost:5000`
3. **WebSocket on:** `ws://localhost:5000`

### **Frontend Team - 3 Things**
1. **Read:** `REACT_INTEGRATION.md`
2. **Install:** `npm install socket.io-client axios`
3. **Connect to:** `http://localhost:5000`

---

## 🎤 **DEMO IN 30 SECONDS**

1. **Show dashboard** - "9 campus locations monitored in real-time"
2. **Trigger anomaly** - `triggerTestAnomaly()` in console
3. **Watch auto-fix** - Alert appears, metrics increase
4. **Explain impact** - "Saves resources automatically, 24/7"

---

## 🆘 **EMERGENCY FIXES**

**Backend won't start?**
```bash
pip install --upgrade flask flask-cors flask-socketio scikit-learn numpy
python api_server.py
```

**Port 5000 busy?**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Frontend can't connect?**
- Ensure backend is running
- Use `http://localhost:5000` (not 127.0.0.1)
- Check browser console for errors

---

## ✅ **PRE-DEMO CHECKLIST** (2 minutes)

- [ ] Backend running: `python api_server.py`
- [ ] Dashboard opens: `http://localhost:5000`
- [ ] Connection shows: "Connected" (green)
- [ ] Metrics updating: Numbers change every second
- [ ] Test ready: `triggerTestAnomaly()` in console

---

## 📞 **QUICK REFERENCE**

| What | Where | How |
|------|-------|-----|
| Start Backend | Terminal | `python api_server.py` |
| View Dashboard | Browser | `http://localhost:5000` |
| Test Anomaly | Console | `triggerTestAnomaly()` |
| API Docs | File | `README.md` |
| React Guide | File | `REACT_INTEGRATION.md` |
| Full Checklist | File | `PROJECT_CHECKLIST.md` |

---

**You're ready! 🚀**
