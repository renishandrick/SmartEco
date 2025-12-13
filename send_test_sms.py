"""
Quick test script to send a custom SMS message.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sms_service import send_emergency_sms
from templates import custom_alert

# Send a custom test message
print("=" * 60)
print("Sending test SMS message...")
print("=" * 60)
print()

# Create a friendly test message
message = "Hello! This is a test message from your enhanced SMS service. Everything is working perfectly!"

print(f"Message: {message}")
print(f"Recipient: +919994196997")
print()

# Send the message
result = send_emergency_sms(message)

print()
if result:
    print("SUCCESS! Message sent successfully!")
    print("Check your phone - you should receive the SMS shortly.")
else:
    print("FAILED! Message could not be sent.")

print()
print("=" * 60)
