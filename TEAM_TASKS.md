# 📋 SmartEco+ - TEAM TASK DISTRIBUTION

> **Quick reference for who does what**

---

## 👥 **BACKEND TEAM TASKS**

### ⚠️ **CRITICAL (Must Do Now)**

#### 1. Install Dependencies
```bash
cd c:\Users\renish\OneDrive\Desktop\automation
pip install -r requirements.txt
```
**Time:** 1 minute  
**Verify:** `python -c "import flask; print('OK!')"`

#### 2. Start Backend Server
```bash
python api_server.py
```
**Time:** 30 seconds  
**Keep running:** Don't close this terminal!  
**Verify:** Should see "Simulation started"

#### 3. Test Endpoints
```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/campus/state
```
**Time:** 1 minute  
**Verify:** Both return JSON data

### 📚 **KNOWLEDGE (Learn This)**
- Read: `README.md` (API section)
- Understand: How simulation works
- Explain: AI/ML models (Isolation Forest, Linear Regression)
- Know: All 8 API endpoints

### 🎤 **DEMO ROLE**
- Monitor backend terminal during demo
- Explain API architecture if asked
- Explain AI detection system
- Be ready to restart server if needed

---

## 🎨 **FRONTEND TEAM TASKS**

### ⚠️ **CRITICAL (Must Do Now)**

#### 1. Read Integration Guide
```bash
# Open this file
REACT_INTEGRATION.md
```
**Time:** 10 minutes  
**Focus on:** WebSocket setup, React hooks, example components

#### 2. Install Dependencies
```bash
npm install socket.io-client axios
```
**Time:** 1 minute  
**For:** React integration

#### 3. Test Demo Dashboard
```
1. Ensure backend is running
2. Open: http://localhost:5000
3. Check: Connection status = "Connected"
4. Watch: Metrics update every second
5. Test: triggerTestAnomaly() in console
```
**Time:** 2 minutes  
**Verify:** Everything works smoothly

### 📚 **KNOWLEDGE (Learn This)**
- Read: `REACT_INTEGRATION.md` (full guide)
- Understand: WebSocket events
- Know: Data structures (Location, Sensor, Alert, Metrics)
- Familiarize: Demo dashboard features

### 🎤 **DEMO ROLE**
- Control the browser during demo
- Trigger test anomaly at right moment
- Explain UI/UX features
- Show real-time updates

---

## 🎯 **EVERYONE'S TASKS**

### ⚠️ **CRITICAL (Must Do Together)**

#### 1. Practice Demo (3 times minimum)
```
Run 1: Get familiar with flow
Run 2: Time it (should be ~3 minutes)
Run 3: Perfect it (smooth and confident)
```
**Time:** 15 minutes total

#### 2. Memorize Demo Script
```
[30s] Introduction
[2m]  Live demonstration
[30s] Impact statement
```
**Time:** 10 minutes

#### 3. Prepare Backup Plan
```
- Take screenshots of working system
- Record video of demo (optional)
- Print key slides (optional)
```
**Time:** 5 minutes

### 📚 **KNOWLEDGE (Everyone Should Know)**
- What problem does SmartEco+ solve?
- How does the AI work? (high-level)
- What makes it different from others?
- What's the real-world impact?

### 🎤 **DEMO COORDINATION**
```
Person 1 (Presenter): Introduces project, coordinates
Person 2 (Backend):   Monitors server, explains tech
Person 3 (Frontend):  Controls browser, triggers demo
```

---

## ⏰ **TIMELINE (Before Demo)**

### **NOW → 30 min before demo:**
```
Backend Team:
  [ ] Install dependencies (1 min)
  [ ] Test backend (2 min)
  [ ] Read API docs (10 min)

Frontend Team:
  [ ] Read React guide (10 min)
  [ ] Test dashboard (2 min)
  [ ] Install npm packages (1 min)

Everyone:
  [ ] Practice demo together (15 min)
  [ ] Assign roles (2 min)
```

### **30 min before demo:**
```
[ ] Start backend server
[ ] Open dashboard in browser
[ ] Verify connection
[ ] Do final practice run
[ ] Prepare backup materials
```

### **5 min before demo:**
```
[ ] Backend running ✓
[ ] Dashboard open ✓
[ ] Console ready ✓
[ ] Team in position ✓
[ ] Ready to impress ✓
```

---

## 🚨 **EMERGENCY CONTACTS**

### **Backend Issues?**
**Problem:** Server won't start  
**Solution:** `pip install --upgrade -r requirements.txt`

**Problem:** Port 5000 busy  
**Solution:** `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`

### **Frontend Issues?**
**Problem:** Can't connect  
**Solution:** Check backend running, use `http://localhost:5000`

**Problem:** No data showing  
**Solution:** Check browser console, verify API with curl

### **Demo Issues?**
**Problem:** System crashes during demo  
**Solution:** Use backup screenshots/video, explain what should happen

---

## ✅ **QUICK VERIFICATION**

### **Backend Team - Check These:**
```bash
# Dependencies installed?
python -c "import flask, sklearn; print('✓')"

# Server running?
curl http://localhost:5000/api/health

# Simulation active?
# Check terminal for "Simulation started"
```

### **Frontend Team - Check These:**
```
# Dashboard loads?
Open: http://localhost:5000

# Connected?
Status indicator: Green "Connected"

# Real-time working?
Metrics changing every second?

# Test works?
triggerTestAnomaly() triggers alert?
```

### **Everyone - Check These:**
```
[ ] Know the problem SmartEco+ solves
[ ] Can explain AI in simple terms
[ ] Understand real-world impact
[ ] Confident with demo flow
[ ] Know your speaking parts
```

---

## 🎯 **SUCCESS = TEAMWORK**

```
Backend Team: Keeps system running
Frontend Team: Makes it look good
Everyone: Tells the story

Together: You win! 🏆
```

---

## 📞 **WHO TO ASK WHAT**

| Question | Ask |
|----------|-----|
| How does the API work? | Backend Team |
| What's the AI doing? | Backend Team |
| How to connect frontend? | Frontend Team |
| How does UI work? | Frontend Team |
| What's our impact? | Everyone should know |
| Why will we win? | Everyone should know |

---

## 🏆 **REMEMBER**

**You have:**
- ✅ Complete working system
- ✅ Real AI/ML (not fake)
- ✅ Beautiful dashboard
- ✅ Professional docs
- ✅ Great teamwork

**You need:**
- ⚠️ Install dependencies (Backend)
- ⚠️ Start server (Backend)
- ⚠️ Test dashboard (Frontend)
- ⚠️ Practice demo (Everyone)

**Total time needed: ~20 minutes**

---

**Let's win this! 🚀**
