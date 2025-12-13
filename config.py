"""
Configuration management for SMS Service.
Loads and validates environment variables.
"""

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration for SMS service."""
    
    # Twilio credentials
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Default recipient
    TARGET_PHONE_NUMBER = os.getenv("TARGET_PHONE_NUMBER")
    
    # SMS Configuration
    MAX_SMS_PER_HOUR = int(os.getenv("MAX_SMS_PER_HOUR", "10"))
    SMS_RETRY_ATTEMPTS = int(os.getenv("SMS_RETRY_ATTEMPTS", "3"))
    
    # Twilio message limits
    MAX_MESSAGE_LENGTH = 1600  # Twilio's SMS character limit
    
    @classmethod
    def validate(cls):
        """
        Validate that all required configuration is present.
        Raises ValueError if any required config is missing.
        """
        required_vars = {
            "TWILIO_ACCOUNT_SID": cls.TWILIO_ACCOUNT_SID,
            "TWILIO_AUTH_TOKEN": cls.TWILIO_AUTH_TOKEN,
            "TWILIO_PHONE_NUMBER": cls.TWILIO_PHONE_NUMBER,
            "TARGET_PHONE_NUMBER": cls.TARGET_PHONE_NUMBER,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        
        if missing:
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("✅ Configuration validated successfully")
        return True
    
    @classmethod
    def get_summary(cls):
        """Get a safe summary of configuration (without exposing secrets)."""
        return {
            "account_sid": cls.TWILIO_ACCOUNT_SID[:10] + "..." if cls.TWILIO_ACCOUNT_SID else "Not set",
            "phone_number": cls.TWILIO_PHONE_NUMBER,
            "max_sms_per_hour": cls.MAX_SMS_PER_HOUR,
            "retry_attempts": cls.SMS_RETRY_ATTEMPTS,
        }


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    logger.warning(f"Configuration validation failed: {e}")
    logger.warning("Please ensure .env file exists with all required variables")
