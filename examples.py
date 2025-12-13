"""
Example usage of the enhanced SMS service.
Demonstrates various features and integration patterns.
"""

from sms_service import SMSService, send_emergency_sms
from templates import (
    water_leak_alert,
    fire_alert,
    security_alert,
    energy_alert,
    waste_alert,
    custom_alert,
    AlertTemplates
)


def example_1_basic_usage():
    """Example 1: Basic SMS send using backward-compatible function."""
    print("\n" + "="*60)
    print("Example 1: Basic Usage")
    print("="*60)
    
    # Simple usage - sends to default recipient from .env
    result = send_emergency_sms("Test alert message")
    print(f"Success: {result}")


def example_2_using_templates():
    """Example 2: Using predefined templates."""
    print("\n" + "="*60)
    print("Example 2: Using Templates")
    print("="*60)
    
    # Water leak alert
    message = water_leak_alert("Block A - Floor 3", 150.5)
    print(f"Message: {message}")
    result = send_emergency_sms(message)
    print(f"Success: {result}\n")
    
    # Energy alert
    message = energy_alert("Building B", 450.2, 300.0)
    print(f"Message: {message}")
    result = send_emergency_sms(message)
    print(f"Success: {result}")


def example_3_multiple_recipients():
    """Example 3: Sending to multiple recipients."""
    print("\n" + "="*60)
    print("Example 3: Multiple Recipients")
    print("="*60)
    
    service = SMSService()
    
    # Send to multiple phone numbers
    recipients = [
        "+919994196997",  # Your verified number
        # "+1234567890",  # Add more numbers here
    ]
    
    result = service.send_sms(
        "Emergency: Fire alarm triggered in Main Building!",
        recipients=recipients
    )
    
    print(f"Total sent: {result['total_sent']}")
    print(f"Total failed: {result['total_failed']}")
    print(f"Success: {result['success']}")


def example_4_rate_limit_check():
    """Example 4: Checking rate limit status."""
    print("\n" + "="*60)
    print("Example 4: Rate Limit Status")
    print("="*60)
    
    service = SMSService()
    status = service.rate_limiter.get_status()
    
    print(f"Max per hour: {status['max_per_hour']}")
    print(f"Sent this hour: {status['sent_this_hour']}")
    print(f"Remaining: {status['remaining']}")
    print(f"Can send: {status['can_send']}")


def example_5_detailed_results():
    """Example 5: Getting detailed send results."""
    print("\n" + "="*60)
    print("Example 5: Detailed Results")
    print("="*60)
    
    service = SMSService()
    
    result = service.send_sms("Test message with detailed results")
    
    print(f"Overall success: {result['success']}")
    print(f"Total sent: {result['total_sent']}")
    print(f"Total failed: {result['total_failed']}")
    
    print("\nIndividual results:")
    for r in result['results']:
        print(f"  Recipient: {r['recipient']}")
        print(f"  Success: {r['success']}")
        print(f"  Message SID: {r['message_sid']}")
        print(f"  Status: {r['status']}")
        if r['error']:
            print(f"  Error: {r['error']}")


def example_6_ai_smart_campus_integration():
    """Example 6: Integration with AI Smart Campus ML models."""
    print("\n" + "="*60)
    print("Example 6: AI Smart Campus Integration")
    print("="*60)
    
    # Simulating ML model predictions
    predicted_water_consumption = 500  # L/min
    threshold = 200  # L/min
    
    # Check if anomaly detected
    if predicted_water_consumption > threshold:
        print(f"⚠️ Anomaly detected! Water: {predicted_water_consumption} L/min")
        
        # Create alert message
        message = water_leak_alert(
            location="Block A - Floor 3",
            flow_rate=predicted_water_consumption
        )
        
        # Send alert
        print(f"Sending alert: {message}")
        result = send_emergency_sms(message)
        print(f"Alert sent: {result}")
    else:
        print("✅ All systems normal")


def example_7_custom_templates():
    """Example 7: Creating custom alert templates."""
    print("\n" + "="*60)
    print("Example 7: Custom Templates")
    print("="*60)
    
    # Using custom template
    message = custom_alert("Scheduled maintenance tonight at 10 PM")
    print(f"Message: {message}")
    
    # Or format any template with custom data
    message = AlertTemplates.format_alert(
        "environmental",
        location="Campus Center",
        parameter="Temperature",
        value="35°C",
        threshold="30°C"
    )
    print(f"Message: {message}")


def example_8_error_handling():
    """Example 8: Error handling and validation."""
    print("\n" + "="*60)
    print("Example 8: Error Handling")
    print("="*60)
    
    service = SMSService()
    
    # Test 1: Empty message
    print("Test 1: Empty message")
    result = service.send_sms("")
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")
    
    # Test 2: Message too long
    print("Test 2: Message too long")
    long_message = "A" * 2000
    result = service.send_sms(long_message)
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")
    
    # Test 3: Invalid phone number
    print("Test 3: Invalid phone number")
    result = service.send_sms("Test", recipients=["invalid-number"])
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SMS SERVICE - USAGE EXAMPLES")
    print("="*70)
    
    # Run examples (uncomment the ones you want to test)
    
    # example_1_basic_usage()
    # example_2_using_templates()
    # example_3_multiple_recipients()
    example_4_rate_limit_check()
    # example_5_detailed_results()
    example_6_ai_smart_campus_integration()
    example_7_custom_templates()
    # example_8_error_handling()
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\n💡 Tip: Uncomment examples to test them with real SMS sends")
    print("⚠️  Warning: Real SMS sends will cost money and count toward rate limits")
