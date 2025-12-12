"""
SmartEco+ Digital Twin - API Server
Flask REST API + WebSocket for real-time campus monitoring
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime

# Import our simulation engine and AI system
from digital_twin_engine import campus_engine
from digital_twin import ai_system

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for React frontend
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
simulation_running = False
simulation_thread = None


# ==================== REST API ENDPOINTS ====================

@app.route('/')
def index():
    """Serve the demo dashboard"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/campus/state', methods=['GET'])
def get_campus_state():
    """
    Get complete campus state
    Returns all locations with sensor data
    """
    state = campus_engine.get_campus_state()
    return jsonify({
        'success': True,
        'data': state
    })

@app.route('/api/location/<location_id>', methods=['GET'])
def get_location(location_id):
    """
    Get specific location data
    """
    location_data = campus_engine.get_location_data(location_id)
    
    if location_data:
        return jsonify({
            'success': True,
            'data': location_data
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Location not found'
        }), 404

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get savings metrics including carbon footprint
    """
    return jsonify({
        'success': True,
        'data': {
            'campus_metrics': campus_engine.metrics,
            'ai_stats': ai_system.get_detection_stats(),
            'carbon_footprint': campus_engine.get_carbon_footprint()
        }
    })


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """
    Get recent alerts
    """
    limit = request.args.get('limit', 10, type=int)
    alerts = campus_engine.get_recent_alerts(limit)
    
    return jsonify({
        'success': True,
        'data': {
            'alerts': alerts,
            'total': len(campus_engine.alerts_history)
        }
    })

@app.route('/api/insights/<location_id>/<sensor_type>', methods=['GET'])
def get_insights(location_id, sensor_type):
    """
    Get AI insights for specific sensor
    """
    insights = ai_system.get_insights(location_id, sensor_type)
    
    return jsonify({
        'success': True,
        'data': insights
    })

@app.route('/api/simulate/anomaly', methods=['POST'])
def simulate_anomaly():
    """
    Manually trigger an anomaly for testing
    Body: {location_id: str, sensor_type: str}
    """
    data = request.get_json()
    location_id = data.get('location_id')
    sensor_type = data.get('sensor_type')
    
    if not location_id or not sensor_type:
        return jsonify({
            'success': False,
            'error': 'Missing location_id or sensor_type'
        }), 400
    
    success = campus_engine.simulate_anomaly(location_id, sensor_type)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'Anomaly triggered for {location_id} - {sensor_type}'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid location or sensor type'
        }), 400

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """
    Get list of all locations
    """
    locations = [
        {
            'id': loc_id,
            'name': loc.name,
            'type': loc.location_type,
            'sensors': list(loc.sensors.keys())
        }
        for loc_id, loc in campus_engine.locations.items()
    ]
    
    return jsonify({
        'success': True,
        'data': {
            'locations': locations,
            'total': len(locations)
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'success': True,
        'status': 'running',
        'uptime_seconds': campus_engine.metrics['uptime_seconds'],
        'simulation_active': simulation_running
    })


# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Client connected to WebSocket"""
    print(f'Client connected: {request.sid}')
    emit('connection_established', {
        'message': 'Connected to SmartEco+ Digital Twin',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected from WebSocket"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('request_campus_state')
def handle_campus_state_request():
    """Client requests current campus state"""
    state = campus_engine.get_campus_state()
    emit('campus_state', state)


# ==================== SIMULATION LOOP ====================

def simulation_loop():
    """
    Main simulation loop - runs in background thread
    Updates sensors and checks for anomalies every second
    """
    global simulation_running
    
    print("[*] Simulation loop started")
    
    while simulation_running:
        try:
            # Update all sensors
            campus_engine.update_all_sensors()
            
            # Run AI detection on all sensors
            for location_id, location in campus_engine.locations.items():
                for sensor_name, sensor in location.sensors.items():
                    current_value = sensor['current_value']
                    threshold = sensor['threshold']
                    
                    # Update AI history
                    ai_system.update_history(location_id, sensor_name, current_value)
                    
                    # Check if auto-fix needed
                    if not location.auto_fix_active:
                        decision = ai_system.should_trigger_auto_fix(
                            location_id, 
                            sensor_name, 
                            current_value, 
                            threshold
                        )
                        
                        if decision['should_fix']:
                            # Trigger auto-fix
                            alert = campus_engine.trigger_auto_fix(
                                location_id,
                                sensor_name,
                                decision['reason']
                            )
                            
                            # Broadcast alert via WebSocket
                            socketio.emit('alert', alert)
                            
                            print(f"[AUTO-FIX] {location.name} - {sensor_name}")
                            print(f"   Reason: {decision['reason']}")
                            print(f"   Urgency: {decision['urgency']}")
                    
                    # Complete auto-fix after 5 seconds
                    elif location.auto_fix_active and location.fix_timestamp:
                        if time.time() - location.fix_timestamp > 5:
                            # Calculate saved amount
                            saved = decision.get('predicted_impact', 10) if 'decision' in locals() else 10
                            campus_engine.complete_auto_fix(location_id, saved)
                            
                            # Broadcast completion
                            socketio.emit('fix_completed', {
                                'location_id': location_id,
                                'sensor_type': sensor_name,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            print(f"[COMPLETED] FIX: {location.name} - {sensor_name}")
            
            # Broadcast updated campus state to all connected clients
            state = campus_engine.get_campus_state()
            socketio.emit('campus_update', state)
            
            # Sleep for 1 second
            time.sleep(1)
            
        except Exception as e:
            print(f"[ERROR] Simulation loop: {e}")
            time.sleep(1)
    
    print("[*] Simulation loop stopped")

def start_simulation():
    """Start the simulation in a background thread"""
    global simulation_running, simulation_thread
    
    if not simulation_running:
        simulation_running = True
        simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
        simulation_thread.start()
        print("[*] Simulation started")

def stop_simulation():
    """Stop the simulation"""
    global simulation_running
    simulation_running = False
    print("[*] Simulation stopped")


# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("SmartEco+ Digital Twin - Starting Server")
    print("=" * 60)
    print()
    print("API Server: http://localhost:5000")
    print("Dashboard: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    print()
    print("REST API Endpoints:")
    print("   GET  /api/campus/state       - Get complete campus state")
    print("   GET  /api/location/<id>      - Get specific location")
    print("   GET  /api/metrics            - Get savings metrics")
    print("   GET  /api/alerts             - Get recent alerts")
    print("   GET  /api/locations          - Get all locations")
    print("   GET  /api/insights/<id>/<sensor> - Get AI insights")
    print("   POST /api/simulate/anomaly   - Trigger test anomaly")
    print("   GET  /api/health             - Health check")
    print()
    print("WebSocket Events:")
    print("   -> campus_update    - Real-time sensor updates (1/sec)")
    print("   -> alert            - Anomaly detected")
    print("   -> fix_completed    - Auto-fix completed")
    print()
    print("=" * 60)
    print()
    
    # Start simulation
    start_simulation()
    
    # Start Flask server with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
