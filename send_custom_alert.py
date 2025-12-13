"""
Send custom water leakage alert message.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sms_service import send_emergency_sms
from templates import water_leak_alert

# Send water leakage alert
print("=" * 60)
print("Sending Water Leakage Alert...")
print("=" * 60)
print()

# Option 1: Using the template (recommended)
message_template = water_leak_alert("Block D - 4th Floor", 0)  # 0 as placeholder for flow rate
print(f"Template message: {message_template}")
print()

# Option 2: Custom message as you typed
custom_message = "ALERT: Water leakage in Block D 4th floor"
print(f"Custom message: {custom_message}")
print()

# Send the custom message
print("Sending custom message...")
result = send_emergency_sms(custom_message)

print()
if result:
    print("SUCCESS! Alert sent successfully!")
    print("Check your phone - you should receive the SMS shortly.")
else:
    print("FAILED! Message could not be sent.")

print()
print("=" * 60)
