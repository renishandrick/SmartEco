"""
Message templates for different types of emergency alerts.
Provides consistent formatting and easy customization.
"""

from typing import Dict, Any


class AlertTemplates:
    """Predefined message templates for various alert types."""
    
    # Template definitions with placeholders
    TEMPLATES = {
        "water_leak": "🚨 CRITICAL WATER LEAK detected in {location}! Immediate action required. Flow rate: {flow_rate} L/min",
        
        "fire": "🔥 FIRE EMERGENCY in {location}! Evacuate immediately. Fire department notified.",
        
        "security": "⚠️ SECURITY BREACH in {location}! Unauthorized access detected. Type: {breach_type}",
        
        "energy": "⚡ ENERGY ALERT in {location}! Abnormal consumption: {consumption} kWh (Expected: {expected} kWh)",
        
        "waste": "♻️ WASTE MANAGEMENT ALERT in {location}! Bin capacity: {capacity}% - Immediate collection needed.",
        
        "maintenance": "🔧 MAINTENANCE REQUIRED in {location}! Issue: {issue}. Priority: {priority}",
        
        "environmental": "🌡️ ENVIRONMENTAL ALERT in {location}! {parameter}: {value} (Threshold: {threshold})",
        
        "custom": "🚨 ALERT: {message}",
    }
    
    @classmethod
    def get_template(cls, alert_type: str) -> str:
        """
        Get a template by type.
        
        Args:
            alert_type: Type of alert (water_leak, fire, security, etc.)
            
        Returns:
            Template string with placeholders
        """
        return cls.TEMPLATES.get(alert_type, cls.TEMPLATES["custom"])
    
    @classmethod
    def format_alert(cls, alert_type: str, **kwargs) -> str:
        """
        Format an alert message with provided data.
        
        Args:
            alert_type: Type of alert
            **kwargs: Data to fill template placeholders
            
        Returns:
            Formatted alert message
            
        Example:
            >>> AlertTemplates.format_alert("water_leak", location="Block A", flow_rate=150)
            '🚨 CRITICAL WATER LEAK detected in Block A! Immediate action required. Flow rate: 150 L/min'
        """
        template = cls.get_template(alert_type)
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # If a required placeholder is missing, return a generic message
            return f"🚨 ALERT: {alert_type} in {kwargs.get('location', 'unknown location')}"
    
    @classmethod
    def list_available_templates(cls) -> list:
        """Get list of available template types."""
        return list(cls.TEMPLATES.keys())


# Convenience functions for common alerts

def water_leak_alert(location: str, flow_rate: float) -> str:
    """Create a water leak alert message."""
    return AlertTemplates.format_alert("water_leak", location=location, flow_rate=flow_rate)


def fire_alert(location: str) -> str:
    """Create a fire emergency alert message."""
    return AlertTemplates.format_alert("fire", location=location)


def security_alert(location: str, breach_type: str) -> str:
    """Create a security breach alert message."""
    return AlertTemplates.format_alert("security", location=location, breach_type=breach_type)


def energy_alert(location: str, consumption: float, expected: float) -> str:
    """Create an energy consumption alert message."""
    return AlertTemplates.format_alert(
        "energy", 
        location=location, 
        consumption=consumption, 
        expected=expected
    )


def waste_alert(location: str, capacity: int) -> str:
    """Create a waste management alert message."""
    return AlertTemplates.format_alert("waste", location=location, capacity=capacity)


def custom_alert(message: str) -> str:
    """Create a custom alert message."""
    return AlertTemplates.format_alert("custom", message=message)


if __name__ == "__main__":
    # Test templates
    print("=== Testing Alert Templates ===\n")
    
    print("1. Water Leak Alert:")
    print(water_leak_alert("Block A - Floor 3", 150.5))
    print()
    
    print("2. Fire Alert:")
    print(fire_alert("Main Building - Room 204"))
    print()
    
    print("3. Security Alert:")
    print(security_alert("Main Entrance", "Unauthorized access attempt"))
    print()
    
    print("4. Energy Alert:")
    print(energy_alert("Building B", 450.2, 300.0))
    print()
    
    print("5. Waste Alert:")
    print(waste_alert("Campus Center", 95))
    print()
    
    print("6. Custom Alert:")
    print(custom_alert("System maintenance scheduled for tonight"))
    print()
    
    print("Available templates:", AlertTemplates.list_available_templates())
