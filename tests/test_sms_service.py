"""
Unit tests for SMS Service.
Tests core functionality with mocked Twilio client.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sms_service import SMSService, send_emergency_sms
from templates import water_leak_alert, AlertTemplates
from rate_limiter import SMSRateLimiter


class TestSMSService(unittest.TestCase):
    """Test cases for SMSService class."""
    
    @patch('sms_service.Client')
    def test_send_sms_success(self, mock_client):
        """Test successful SMS send."""
        # Setup mock
        mock_instance = MagicMock()
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_message.status = "queued"
        mock_instance.messages.create.return_value = mock_message
        mock_client.return_value = mock_instance
        
        # Send SMS
        service = SMSService()
        result = service.send_sms("Test message")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["total_sent"], 1)
        self.assertEqual(result["total_failed"], 0)
        self.assertEqual(result["results"][0]["message_sid"], "SM123456789")
    
    @patch('sms_service.Client')
    def test_send_sms_failure(self, mock_client):
        """Test SMS send failure."""
        # Setup mock to raise exception
        mock_instance = MagicMock()
        mock_instance.messages.create.side_effect = Exception("Network error")
        mock_client.return_value = mock_instance
        
        # Send SMS
        service = SMSService()
        result = service.send_sms("Test message")
        
        # Assertions
        self.assertFalse(result["success"])
        self.assertEqual(result["total_sent"], 0)
        self.assertEqual(result["total_failed"], 1)
    
    @patch('sms_service.Client')
    def test_empty_message_validation(self, mock_client):
        """Test that empty messages are rejected."""
        service = SMSService()
        result = service.send_sms("")
        
        self.assertFalse(result["success"])
        self.assertIn("empty", result["error"].lower())
    
    @patch('sms_service.Client')
    def test_message_too_long(self, mock_client):
        """Test that overly long messages are rejected."""
        service = SMSService()
        long_message = "A" * 2000  # Exceeds 1600 char limit
        result = service.send_sms(long_message)
        
        self.assertFalse(result["success"])
        self.assertIn("too long", result["error"].lower())
    
    @patch('sms_service.Client')
    def test_multiple_recipients(self, mock_client):
        """Test sending to multiple recipients."""
        # Setup mock
        mock_instance = MagicMock()
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_message.status = "queued"
        mock_instance.messages.create.return_value = mock_message
        mock_client.return_value = mock_instance
        
        # Send to multiple recipients
        service = SMSService()
        recipients = ["+1234567890", "+0987654321"]
        result = service.send_sms("Test message", recipients)
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["total_sent"], 2)
        self.assertEqual(len(result["results"]), 2)
    
    @patch('sms_service.Client')
    def test_backward_compatibility_function(self, mock_client):
        """Test backward compatible send_emergency_sms function."""
        # Setup mock
        mock_instance = MagicMock()
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_message.status = "queued"
        mock_instance.messages.create.return_value = mock_message
        mock_client.return_value = mock_instance
        
        # Use old function
        result = send_emergency_sms("Test message")
        
        # Should return boolean
        self.assertTrue(isinstance(result, bool))
        self.assertTrue(result)


class TestAlertTemplates(unittest.TestCase):
    """Test cases for alert templates."""
    
    def test_water_leak_template(self):
        """Test water leak alert template."""
        message = water_leak_alert("Block A", 150.5)
        
        self.assertIn("Block A", message)
        self.assertIn("150.5", message)
        self.assertIn("WATER LEAK", message.upper())
    
    def test_custom_template(self):
        """Test custom alert template."""
        message = AlertTemplates.format_alert("custom", message="Test alert")
        
        self.assertIn("Test alert", message)
        self.assertIn("ALERT", message.upper())
    
    def test_missing_placeholder(self):
        """Test template with missing placeholder data."""
        # Should not crash, should return fallback message
        message = AlertTemplates.format_alert("water_leak", location="Block A")
        
        self.assertIn("Block A", message)


class TestRateLimiter(unittest.TestCase):
    """Test cases for rate limiter."""
    
    def test_initial_state(self):
        """Test rate limiter initial state."""
        limiter = SMSRateLimiter(max_per_hour=10)
        
        self.assertTrue(limiter.can_send())
        self.assertEqual(limiter.get_remaining_quota(), 10)
    
    def test_record_send(self):
        """Test recording SMS sends."""
        limiter = SMSRateLimiter(max_per_hour=10)
        
        limiter.record_send()
        self.assertEqual(limiter.get_remaining_quota(), 9)
        
        limiter.record_send()
        self.assertEqual(limiter.get_remaining_quota(), 8)
    
    def test_rate_limit_exceeded(self):
        """Test rate limit enforcement."""
        limiter = SMSRateLimiter(max_per_hour=3)
        
        # Send 3 SMS (at limit)
        for _ in range(3):
            self.assertTrue(limiter.can_send())
            limiter.record_send()
        
        # 4th should be blocked
        self.assertFalse(limiter.can_send())
    
    def test_reset(self):
        """Test rate limiter reset."""
        limiter = SMSRateLimiter(max_per_hour=5)
        
        for _ in range(5):
            limiter.record_send()
        
        self.assertFalse(limiter.can_send())
        
        limiter.reset()
        self.assertTrue(limiter.can_send())
        self.assertEqual(limiter.get_remaining_quota(), 5)


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Running SMS Service Unit Tests")
    print("=" * 60)
    print()
    
    # Run tests with verbose output
    unittest.main(verbosity=2)
