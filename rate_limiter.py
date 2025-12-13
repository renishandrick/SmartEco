"""
Rate limiter for SMS service to prevent spam and control costs.
Tracks SMS sends over time and enforces hourly limits.
"""

from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)


class SMSRateLimiter:
    """
    Rate limiter to prevent excessive SMS sends.
    Tracks sends per hour and enforces configurable limits.
    """
    
    def __init__(self, max_per_hour: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            max_per_hour: Maximum number of SMS allowed per hour
        """
        self.max_per_hour = max_per_hour
        self.sent_times: List[datetime] = []
        logger.info(f"Rate limiter initialized: {max_per_hour} SMS/hour")
    
    def _clean_old_records(self):
        """Remove records older than 1 hour."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Keep only sends from the last hour
        self.sent_times = [t for t in self.sent_times if t > hour_ago]
    
    def can_send(self) -> bool:
        """
        Check if sending is allowed based on rate limit.
        
        Returns:
            True if sending is allowed, False if rate limit exceeded
        """
        self._clean_old_records()
        
        allowed = len(self.sent_times) < self.max_per_hour
        
        if not allowed:
            logger.warning(
                f"⚠️ Rate limit exceeded! {len(self.sent_times)}/{self.max_per_hour} SMS sent in last hour"
            )
        
        return allowed
    
    def record_send(self):
        """Record that an SMS was sent."""
        self.sent_times.append(datetime.now())
        logger.debug(f"SMS send recorded. Total in last hour: {len(self.sent_times)}")
    
    def get_remaining_quota(self) -> int:
        """
        Get number of SMS remaining in current hour.
        
        Returns:
            Number of SMS that can still be sent this hour
        """
        self._clean_old_records()
        return max(0, self.max_per_hour - len(self.sent_times))
    
    def get_status(self) -> dict:
        """
        Get current rate limiter status.
        
        Returns:
            Dictionary with quota information
        """
        self._clean_old_records()
        
        return {
            "max_per_hour": self.max_per_hour,
            "sent_this_hour": len(self.sent_times),
            "remaining": self.get_remaining_quota(),
            "can_send": self.can_send(),
        }
    
    def reset(self):
        """Reset the rate limiter (clear all records)."""
        self.sent_times = []
        logger.info("Rate limiter reset")
    
    def time_until_next_available(self) -> timedelta:
        """
        Get time until next SMS slot becomes available.
        
        Returns:
            timedelta until oldest send expires (or 0 if quota available)
        """
        if self.can_send():
            return timedelta(0)
        
        self._clean_old_records()
        
        if not self.sent_times:
            return timedelta(0)
        
        # Time until oldest send expires
        oldest_send = min(self.sent_times)
        hour_from_oldest = oldest_send + timedelta(hours=1)
        now = datetime.now()
        
        return max(timedelta(0), hour_from_oldest - now)


# Global rate limiter instance
_global_limiter = None


def get_rate_limiter(max_per_hour: int = 10) -> SMSRateLimiter:
    """
    Get or create global rate limiter instance.
    
    Args:
        max_per_hour: Maximum SMS per hour (only used on first call)
        
    Returns:
        Global SMSRateLimiter instance
    """
    global _global_limiter
    
    if _global_limiter is None:
        _global_limiter = SMSRateLimiter(max_per_hour)
    
    return _global_limiter


if __name__ == "__main__":
    # Test rate limiter
    print("=== Testing Rate Limiter ===\n")
    
    limiter = SMSRateLimiter(max_per_hour=5)
    
    print("Initial status:", limiter.get_status())
    print()
    
    # Simulate sending 5 SMS
    print("Sending 5 SMS...")
    for i in range(5):
        if limiter.can_send():
            limiter.record_send()
            print(f"  SMS {i+1} sent. Remaining: {limiter.get_remaining_quota()}")
        else:
            print(f"  SMS {i+1} blocked by rate limit!")
    
    print()
    print("After 5 sends:", limiter.get_status())
    print()
    
    # Try to send one more (should be blocked)
    print("Trying to send 6th SMS...")
    if limiter.can_send():
        print("  ✅ Allowed")
    else:
        print("  ❌ Blocked by rate limit")
        time_until = limiter.time_until_next_available()
        print(f"  Next slot available in: {time_until}")
    
    print()
    print("Final status:", limiter.get_status())
