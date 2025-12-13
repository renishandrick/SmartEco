"""
SMS Emergency Alert Service
Secure, production-ready SMS service using Twilio API.
Features: Environment variables, logging, retry logic, rate limiting, templates.
"""

import logging
from typing import List, Dict, Optional, Union
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import Config
from rate_limiter import get_rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SMSService:
    """
    Enhanced SMS service with security, reliability, and cost control features.
    """
    
    def __init__(self):
        """Initialize SMS service with configuration."""
        self.config = Config
        self.rate_limiter = get_rate_limiter(Config.MAX_SMS_PER_HOUR)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twilio client with credentials."""
        try:
            self.client = Client(
                self.config.TWILIO_ACCOUNT_SID,
                self.config.TWILIO_AUTH_TOKEN
            )
            logger.info("✅ Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Twilio client: {e}")
            raise
    
    def _validate_message(self, message_body: str) -> bool:
        """
        Validate message body.
        
        Args:
            message_body: Message to validate
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        if not message_body or not message_body.strip():
            raise ValueError("Message body cannot be empty")
        
        if len(message_body) > self.config.MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Message too long: {len(message_body)} chars "
                f"(max: {self.config.MAX_MESSAGE_LENGTH})"
            )
        
        return True
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        Basic phone number validation.
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid format
        """
        if not phone_number or not phone_number.startswith('+'):
            raise ValueError(f"Invalid phone number format: {phone_number}")
        
        return True
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(TwilioRestException),
        reraise=True
    )
    def _send_single_sms(self, message_body: str, recipient: str) -> Dict:
        """
        Send SMS to a single recipient with retry logic.
        
        Args:
            message_body: Message to send
            recipient: Phone number to send to
            
        Returns:
            Dictionary with send status and details
        """
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.config.TWILIO_PHONE_NUMBER,
                to=recipient
            )
            
            logger.info(f"✅ SMS sent to {recipient}")
            logger.debug(f"Message SID: {message.sid}")
            
            return {
                "success": True,
                "recipient": recipient,
                "message_sid": message.sid,
                "status": message.status,
                "error": None
            }
            
        except TwilioRestException as e:
            logger.error(f"❌ Twilio error sending to {recipient}: {e.msg}")
            return {
                "success": False,
                "recipient": recipient,
                "message_sid": None,
                "status": "failed",
                "error": str(e.msg)
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error sending to {recipient}: {e}")
            return {
                "success": False,
                "recipient": recipient,
                "message_sid": None,
                "status": "failed",
                "error": str(e)
            }
    
    def send_sms(
        self, 
        message_body: str, 
        recipients: Optional[Union[str, List[str]]] = None,
        bypass_rate_limit: bool = False
    ) -> Dict:
        """
        Send SMS to one or more recipients.
        
        Args:
            message_body: Message to send
            recipients: Phone number(s) to send to. If None, uses default from config.
            bypass_rate_limit: If True, skip rate limit check (use with caution!)
            
        Returns:
            Dictionary with overall status and individual results
            
        Example:
            >>> service = SMSService()
            >>> result = service.send_sms("Water leak in Block A!", "+1234567890")
            >>> print(result['success'])
            True
        """
        logger.info(f"📡 Attempting to send SMS: '{message_body[:50]}...'")
        
        # Validate message
        try:
            self._validate_message(message_body)
        except ValueError as e:
            logger.error(f"❌ Message validation failed: {e}")
            return {
                "success": False,
                "total_sent": 0,
                "total_failed": 0,
                "results": [],
                "error": str(e)
            }
        
        # Determine recipients
        if recipients is None:
            recipients = [self.config.TARGET_PHONE_NUMBER]
        elif isinstance(recipients, str):
            recipients = [recipients]
        
        # Validate recipients
        try:
            for recipient in recipients:
                self._validate_phone_number(recipient)
        except ValueError as e:
            logger.error(f"❌ Phone number validation failed: {e}")
            return {
                "success": False,
                "total_sent": 0,
                "total_failed": len(recipients),
                "results": [],
                "error": str(e)
            }
        
        # Check rate limit
        if not bypass_rate_limit:
            quota = self.rate_limiter.get_remaining_quota()
            if quota < len(recipients):
                error_msg = (
                    f"Rate limit would be exceeded. "
                    f"Trying to send {len(recipients)} SMS, "
                    f"but only {quota} remaining in quota."
                )
                logger.warning(f"⚠️ {error_msg}")
                
                time_until = self.rate_limiter.time_until_next_available()
                logger.info(f"Next slot available in: {time_until}")
                
                return {
                    "success": False,
                    "total_sent": 0,
                    "total_failed": len(recipients),
                    "results": [],
                    "error": error_msg,
                    "rate_limit_status": self.rate_limiter.get_status()
                }
        
        # Send to all recipients
        results = []
        for recipient in recipients:
            result = self._send_single_sms(message_body, recipient)
            results.append(result)
            
            # Record successful sends for rate limiting
            if result["success"]:
                self.rate_limiter.record_send()
        
        # Calculate summary
        total_sent = sum(1 for r in results if r["success"])
        total_failed = len(results) - total_sent
        
        overall_success = total_sent > 0
        
        logger.info(
            f"📊 SMS Send Summary: {total_sent} sent, {total_failed} failed "
            f"(out of {len(recipients)} total)"
        )
        
        return {
            "success": overall_success,
            "total_sent": total_sent,
            "total_failed": total_failed,
            "results": results,
            "error": None,
            "rate_limit_status": self.rate_limiter.get_status()
        }


# Convenience function for backward compatibility
def send_emergency_sms(message_body: str, recipients: Optional[Union[str, List[str]]] = None) -> bool:
    """
    Standalone function to send emergency SMS.
    Maintains backward compatibility with original interface.
    
    Args:
        message_body: Message to send
        recipients: Optional phone number(s). Uses default if not provided.
        
    Returns:
        True if at least one SMS was sent successfully, False otherwise
    """
    try:
        service = SMSService()
        result = service.send_sms(message_body, recipients)
        return result["success"]
    except Exception as e:
        logger.error(f"❌ Failed to send SMS: {e}")
        return False


# --- TEST AREA ---
# This block runs ONLY when you run this file directly.
if __name__ == "__main__":
    # Fix Windows console encoding for emojis
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("TESTING ENHANCED SMS SERVICE")
    print("=" * 60)
    print()
    
    # Import templates for testing
    from templates import water_leak_alert, energy_alert, custom_alert
    
    # Test 1: Basic SMS with default recipient
    print("Test 1: Basic SMS Send")
    print("-" * 60)
    test_message = "Critical Water Leak Detected in Block A!"
    result = send_emergency_sms(test_message)
    print(f"Result: {'Success' if result else 'Failed'}")
    print()
    
    # Test 2: Using templates
    print("Test 2: SMS with Template")
    print("-" * 60)
    templated_message = water_leak_alert("Block A - Floor 3", 150.5)
    print(f"Template message: {templated_message}")
    result = send_emergency_sms(templated_message)
    print(f"Result: {'Success' if result else 'Failed'}")
    print()
    
    # Test 3: Multiple recipients (uncomment and add real numbers to test)
    print("Test 3: Multiple Recipients (Demo)")
    print("-" * 60)
    print("To test multiple recipients, uncomment the code below")
    print("and add real phone numbers:")
    print("# recipients = ['+1234567890', '+0987654321']")
    print("# service = SMSService()")
    print("# result = service.send_sms('Test message', recipients)")
    print()
    
    # Test 4: Rate limit status
    print("Test 4: Rate Limit Status")
    print("-" * 60)
    service = SMSService()
    status = service.rate_limiter.get_status()
    print(f"Max SMS per hour: {status['max_per_hour']}")
    print(f"Sent this hour: {status['sent_this_hour']}")
    print(f"Remaining quota: {status['remaining']}")
    print(f"Can send: {'Yes' if status['can_send'] else 'No'}")
    print()
    
    print("=" * 60)
    print("TEST FINISHED")
    print("=" * 60)
