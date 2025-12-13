"""
SmartEco+ Digital Twin - Campus Simulation Engine
Simulates virtual sensors across campus locations without any hardware
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Any

class CampusLocation:
    """Represents a physical location on campus with virtual sensors"""
    
    def __init__(self, location_id: str, location_type: str, name: str):
        self.location_id = location_id
        self.location_type = location_type  # hostel, classroom, washroom, lab, canteen
        self.name = name
        
        # Sensor configurations based on location type
        self.sensors = self._initialize_sensors()
        
        # Auto-fix state
        self.auto_fix_active = False
        self.auto_fix_type = None
        self.fix_timestamp = None
        
    def _initialize_sensors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize virtual sensors based on location type"""
        sensors = {}
        
        # All locations have energy sensors
        sensors['energy'] = {
            'type': 'current_sensor',
            'unit': 'W',
            'normal_range': self._get_energy_range(),
            'threshold': self._get_energy_threshold(),
            'current_value': 0,
            'status': 'normal',
            'baseline': 0
        }
        
        # Water sensors for washrooms, canteens, hostels
        if self.location_type in ['washroom', 'canteen', 'hostel']:
            sensors['water'] = {
                'type': 'flow_sensor',
                'unit': 'L/min',
                'normal_range': self._get_water_range(),
                'threshold': self._get_water_threshold(),
                'current_value': 0,
                'status': 'normal',
                'baseline': 0
            }
        
        # Waste sensors for all locations
        sensors['waste'] = {
            'type': 'ultrasonic_sensor',
            'unit': '%',
            'normal_range': (0, 70),
            'threshold': 80,
            'current_value': 0,
            'status': 'normal',
            'baseline': 0
        }
        
        return sensors
    
    def _get_energy_range(self) -> tuple:
        """Get normal energy range based on location type"""
        ranges = {
            'hostel': (100, 300),
            'classroom': (200, 500),
            'washroom': (50, 150),
            'lab': (300, 800),
            'canteen': (400, 1000)
        }
        return ranges.get(self.location_type, (100, 300))
    
    def _get_energy_threshold(self) -> float:
        """Get energy anomaly threshold"""
        base_range = self._get_energy_range()
        return base_range[1] * 1.5  # 150% of max normal
    
    def _get_water_range(self) -> tuple:
        """Get normal water flow range based on location type"""
        ranges = {
            'washroom': (2, 8),
            'canteen': (5, 15),
            'hostel': (3, 10)
        }
        return ranges.get(self.location_type, (2, 8))
    
    def _get_water_threshold(self) -> float:
        """Get water anomaly threshold"""
        base_range = self._get_water_range()
        return base_range[1] * 2  # 200% of max normal (leak detection)
    
    def update_sensors(self, time_of_day: int) -> Dict[str, Any]:
        """
        Update all sensor values with realistic patterns
        time_of_day: 0-23 (hour of day)
        """
        updates = {}
        
        # Time-based activity multiplier (higher during day, lower at night)
        activity_multiplier = self._get_activity_multiplier(time_of_day)
        
        for sensor_name, sensor in self.sensors.items():
            if sensor_name == 'energy':
                updates[sensor_name] = self._update_energy_sensor(sensor, activity_multiplier)
            elif sensor_name == 'water':
                updates[sensor_name] = self._update_water_sensor(sensor, activity_multiplier)
            elif sensor_name == 'waste':
                updates[sensor_name] = self._update_waste_sensor(sensor, activity_multiplier)
        
        return updates
    
    def _get_activity_multiplier(self, hour: int) -> float:
        """Get activity level based on time of day"""
        # Low activity: 11 PM - 6 AM (0.2-0.4)
        # Medium activity: 6 AM - 9 AM, 6 PM - 11 PM (0.6-0.8)
        # High activity: 9 AM - 6 PM (0.8-1.0)
        
        if 23 <= hour or hour < 6:  # Night
            return random.uniform(0.2, 0.4)
        elif 6 <= hour < 9 or 18 <= hour < 23:  # Morning/Evening
            return random.uniform(0.6, 0.8)
        else:  # Day
            return random.uniform(0.8, 1.0)
    
    def _update_energy_sensor(self, sensor: Dict, activity: float) -> Dict[str, Any]:
        """Update energy sensor with realistic patterns"""
        min_val, max_val = sensor['normal_range']
        
        # Base value with activity
        base_value = min_val + (max_val - min_val) * activity
        
        # Add random variation (±15%)
        variation = random.uniform(-0.15, 0.15) * base_value
        new_value = base_value + variation
        
        # Occasionally inject anomalies (5% chance)
        if random.random() < 0.05 and not self.auto_fix_active:
            new_value = sensor['threshold'] * random.uniform(1.1, 1.5)  # Spike!
            sensor['status'] = 'anomaly_detected'
        
        # If auto-fix is active, reduce value
        if self.auto_fix_active and self.auto_fix_type == 'energy':
            new_value = min_val * 0.5  # Circuit isolated
            sensor['status'] = 'auto_fixing'
        
        sensor['current_value'] = round(new_value, 2)
        sensor['baseline'] = round(base_value, 2)
        
        return {
            'value': sensor['current_value'],
            'unit': sensor['unit'],
            'status': sensor['status'],
            'threshold': sensor['threshold']
        }
    
    def _update_water_sensor(self, sensor: Dict, activity: float) -> Dict[str, Any]:
        """Update water flow sensor with realistic patterns"""
        min_val, max_val = sensor['normal_range']
        
        # Base value with activity
        base_value = min_val + (max_val - min_val) * activity
        
        # Add random variation (±20%)
        variation = random.uniform(-0.2, 0.2) * base_value
        new_value = base_value + variation
        
        # Occasionally inject leaks (3% chance)
        if random.random() < 0.03 and not self.auto_fix_active:
            new_value = sensor['threshold'] * random.uniform(1.2, 2.0)  # Leak!
            sensor['status'] = 'leak_detected'
        
        # If auto-fix is active, stop flow
        if self.auto_fix_active and self.auto_fix_type == 'water':
            new_value = 0  # Valve closed
            sensor['status'] = 'auto_fixing'
        
        sensor['current_value'] = round(new_value, 2)
        sensor['baseline'] = round(base_value, 2)
        
        return {
            'value': sensor['current_value'],
            'unit': sensor['unit'],
            'status': sensor['status'],
            'threshold': sensor['threshold']
        }
    
    def _update_waste_sensor(self, sensor: Dict, activity: float) -> Dict[str, Any]:
        """Update waste level sensor (gradually fills up)"""
        # Waste accumulates over time
        increment = activity * random.uniform(0.5, 2.0)  # Fills 0.5-2% per update
        
        new_value = sensor['current_value'] + increment
        
        # Cap at 100%
        if new_value > 100:
            new_value = 100
        
        # Check for overflow
        if new_value >= sensor['threshold'] and not self.auto_fix_active:
            sensor['status'] = 'overflow_warning'
        
        # If auto-fix is active, compress waste
        if self.auto_fix_active and self.auto_fix_type == 'waste':
            new_value = new_value * 0.6  # 40% reduction via compression
            sensor['status'] = 'auto_fixing'
        
        sensor['current_value'] = round(new_value, 2)
        
        return {
            'value': sensor['current_value'],
            'unit': sensor['unit'],
            'status': sensor['status'],
            'threshold': sensor['threshold']
        }
    
    def trigger_auto_fix(self, sensor_type: str):
        """Trigger automated fix for a sensor"""
        self.auto_fix_active = True
        self.auto_fix_type = sensor_type
        self.fix_timestamp = time.time()
        
        if sensor_type in self.sensors:
            self.sensors[sensor_type]['status'] = 'auto_fixing'
    
    def complete_auto_fix(self):
        """Complete the auto-fix and return to normal"""
        if self.auto_fix_active:
            # Reset the sensor that was fixed
            if self.auto_fix_type in self.sensors:
                self.sensors[self.auto_fix_type]['status'] = 'fixed'
            
            self.auto_fix_active = False
            self.auto_fix_type = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary for API response"""
        return {
            'location_id': self.location_id,
            'type': self.location_type,
            'name': self.name,
            'sensors': {
                name: {
                    'type': sensor['type'],
                    'value': sensor['current_value'],
                    'unit': sensor['unit'],
                    'status': sensor['status'],
                    'threshold': sensor['threshold']
                }
                for name, sensor in self.sensors.items()
            },
            'auto_fix_active': self.auto_fix_active,
            'auto_fix_type': self.auto_fix_type
        }


class DigitalTwinEngine:
    """Main simulation engine for the entire campus"""
    
    def __init__(self):
        self.locations: Dict[str, CampusLocation] = {}
        self.metrics = {
            'water_saved_liters': 0,
            'energy_saved_kwh': 0,
            'waste_reduced_percent': 0,
            'total_fixes': 0,
            'uptime_seconds': 0
        }
        self.start_time = time.time()
        self.alerts_history: List[Dict[str, Any]] = []
        
        # Initialize campus locations
        self._initialize_campus()
    
    def _initialize_campus(self):
        """Create all campus locations"""
        campus_layout = [
            ('hostel_1', 'hostel', 'Hostel Block A'),
            ('hostel_2', 'hostel', 'Hostel Block B'),
            ('classroom_1', 'classroom', 'Classroom Building 1'),
            ('classroom_2', 'classroom', 'Classroom Building 2'),
            ('washroom_1', 'washroom', 'Main Washroom Block'),
            ('washroom_2', 'washroom', 'Library Washroom'),
            ('lab_1', 'lab', 'Computer Lab'),
            ('lab_2', 'lab', 'Physics Lab'),
            ('canteen_1', 'canteen', 'Main Canteen'),
        ]
        
        for loc_id, loc_type, name in campus_layout:
            self.locations[loc_id] = CampusLocation(loc_id, loc_type, name)
    
    def update_all_sensors(self):
        """Update all sensors across campus"""
        current_hour = datetime.now().hour
        
        for location in self.locations.values():
            location.update_sensors(current_hour)
        
        # Update uptime
        self.metrics['uptime_seconds'] = int(time.time() - self.start_time)
    
    def get_campus_state(self) -> Dict[str, Any]:
        """Get complete campus state"""
        return {
            'timestamp': datetime.now().isoformat(),
            'locations': {
                loc_id: location.to_dict()
                for loc_id, location in self.locations.items()
            },
            'metrics': self.metrics,
            'total_locations': len(self.locations)
        }
    
    def get_location_data(self, location_id: str) -> Dict[str, Any]:
        """Get data for a specific location"""
        if location_id in self.locations:
            return self.locations[location_id].to_dict()
        return None
    
    def trigger_auto_fix(self, location_id: str, sensor_type: str, reason: str):
        """Trigger automated fix and log alert"""
        if location_id in self.locations:
            location = self.locations[location_id]
            location.trigger_auto_fix(sensor_type)
            
            # Log alert
            alert = {
                'timestamp': datetime.now().isoformat(),
                'location_id': location_id,
                'location_name': location.name,
                'sensor_type': sensor_type,
                'reason': reason,
                'action': f'Auto-fix triggered: {self._get_fix_action(sensor_type)}',
                'status': 'fixing'
            }
            self.alerts_history.append(alert)
            self.metrics['total_fixes'] += 1
            
            return alert
        return None
    
    def complete_auto_fix(self, location_id: str, saved_amount: float):
        """Complete auto-fix and update metrics"""
        if location_id in self.locations:
            location = self.locations[location_id]
            fix_type = location.auto_fix_type
            
            # Update metrics based on fix type
            if fix_type == 'water':
                self.metrics['water_saved_liters'] += saved_amount
            elif fix_type == 'energy':
                self.metrics['energy_saved_kwh'] += saved_amount / 1000  # Convert W to kWh
            elif fix_type == 'waste':
                self.metrics['waste_reduced_percent'] += saved_amount
            
            location.complete_auto_fix()
            
            # Update alert status
            if self.alerts_history:
                self.alerts_history[-1]['status'] = 'completed'
                self.alerts_history[-1]['saved_amount'] = saved_amount
    
    def _get_fix_action(self, sensor_type: str) -> str:
        """Get human-readable fix action"""
        actions = {
            'water': 'Solenoid valve closed',
            'energy': 'Circuit isolated',
            'waste': 'Pneumatic compressor activated'
        }
        return actions.get(sensor_type, 'Auto-fix applied')
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alerts_history[-limit:]
    
    def get_carbon_footprint(self) -> Dict[str, Any]:
        """
        Calculate carbon footprint savings based on resource conservation
        Returns CO2 saved in kg and tree equivalents
        """
        # Water: 0.001 kg CO2 per liter (treatment and pumping)
        water_co2 = self.metrics['water_saved_liters'] * 0.001
        
        # Energy: 0.82 kg CO2 per kWh (India electricity grid average)
        energy_co2 = self.metrics['energy_saved_kwh'] * 0.82
        
        # Waste: 0.5 kg CO2 per kg waste (assuming 1% = 1kg for calculation)
        waste_co2 = self.metrics['waste_reduced_percent'] * 0.5
        
        # Total CO2 saved
        total_co2 = water_co2 + energy_co2 + waste_co2
        
        # Tree equivalent (1 tree absorbs ~21 kg CO2 per year)
        trees_equivalent = total_co2 / 21
        
        return {
            'total_co2_saved_kg': round(total_co2, 2),
            'water_co2_kg': round(water_co2, 2),
            'energy_co2_kg': round(energy_co2, 2),
            'waste_co2_kg': round(waste_co2, 2),
            'trees_equivalent': round(trees_equivalent, 2),
            'calculation_note': '1 tree absorbs ~21 kg CO2/year'
        }
    
    def simulate_anomaly(self, location_id: str, sensor_type: str):
        """Manually trigger an anomaly for testing"""
        if location_id in self.locations:
            location = self.locations[location_id]
            if sensor_type in location.sensors:
                sensor = location.sensors[sensor_type]
                # Force anomaly value
                sensor['current_value'] = sensor['threshold'] * 1.5
                sensor['status'] = 'anomaly_detected'
                return True
        return False


# Global engine instance
campus_engine = DigitalTwinEngine()
