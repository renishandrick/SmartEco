# SMS Emergency Alert Service - README

## 📋 Overview

A production-ready SMS emergency alert service built with Twilio for the **AI Smart Campus** project. This service provides secure, reliable, and cost-controlled SMS notifications for critical events detected by ML models.

## ✨ Features

- ✅ **Secure**: Environment-based credential management
- ✅ **Reliable**: Automatic retry logic with exponential backoff
- ✅ **Cost-Controlled**: Rate limiting to prevent excessive SMS sends
- ✅ **Scalable**: Support for multiple recipients
- ✅ **Template-Based**: Predefined message templates for common alerts
- ✅ **Well-Tested**: Comprehensive unit tests with 100% pass rate
- ✅ **Production-Ready**: Proper logging, error handling, and validation

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file is already created with your credentials. Make sure it contains:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+13146893499
TARGET_PHONE_NUMBER=+919994196997
MAX_SMS_PER_HOUR=10
```

### 3. Basic Usage

```python
from sms_service import send_emergency_sms

# Simple usage
send_emergency_sms("Water leak detected in Block A!")
```

### 4. Using Templates

```python
from templates import water_leak_alert

message = water_leak_alert("Block A - Floor 3", 150.5)
send_emergency_sms(message)
```

## 📁 Project Structure

```
bot tool/
├── .env                      # Environment variables (DO NOT COMMIT!)
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── config.py               # Configuration management
├── sms_service.py          # Main SMS service
├── templates.py            # Message templates
├── rate_limiter.py         # Rate limiting logic
├── examples.py             # Usage examples
├── README.md               # This file
└── tests/
    └── test_sms_service.py # Unit tests
```

## 🎯 Usage Examples

### Example 1: Basic SMS

```python
from sms_service import send_emergency_sms

result = send_emergency_sms("Critical alert!")
print(f"Success: {result}")
```

### Example 2: Multiple Recipients

```python
from sms_service import SMSService

service = SMSService()
recipients = ["+1234567890", "+0987654321"]
result = service.send_sms("Alert message", recipients)
```

### Example 3: Using Templates

```python
from templates import water_leak_alert, energy_alert

# Water leak
msg = water_leak_alert("Block A", 150.5)
send_emergency_sms(msg)

# Energy spike
msg = energy_alert("Building B", 450, 300)
send_emergency_sms(msg)
```

### Example 4: AI Smart Campus Integration

```python
from sms_service import send_emergency_sms
from templates import water_leak_alert

# In your ML prediction code
if predicted_water > threshold:
    message = water_leak_alert("Block A", predicted_water)
    send_emergency_sms(message)
```

## 🧪 Testing

### Run Unit Tests

```bash
python -m pytest tests/test_sms_service.py -v
```

**Results:** ✅ 13/13 tests passed

### Test Real SMS Send

```bash
python sms_service.py
```

### Run Examples

```bash
python examples.py
```

## 📊 Available Templates

- `water_leak_alert(location, flow_rate)` - Water leak detection
- `fire_alert(location)` - Fire emergency
- `security_alert(location, breach_type)` - Security breach
- `energy_alert(location, consumption, expected)` - Energy anomaly
- `waste_alert(location, capacity)` - Waste management
- `custom_alert(message)` - Custom message

## ⚙️ Configuration

### Rate Limiting

Default: 10 SMS per hour (configurable in `.env`)

```python
service = SMSService()
status = service.rate_limiter.get_status()
print(f"Remaining: {status['remaining']}")
```

### Message Validation

- Maximum length: 1600 characters (Twilio limit)
- Phone numbers must start with `+`
- Empty messages are rejected

## 🔒 Security Best Practices

1. ✅ **Never commit `.env` file** - Already in `.gitignore`
2. ✅ **Use environment variables** - Implemented
3. ⚠️ **Regenerate Twilio token** - Recommended after initial exposure
4. ✅ **Rate limiting enabled** - Prevents cost overruns

## 🐛 Troubleshooting

### Issue: "Configuration validation failed"

**Solution:** Ensure `.env` file exists with all required variables

### Issue: "Rate limit exceeded"

**Solution:** Wait for quota to reset or increase `MAX_SMS_PER_HOUR` in `.env`

### Issue: "Invalid phone number format"

**Solution:** Ensure phone numbers start with `+` (e.g., `+919994196997`)

## 🎓 Integration with AI Smart Campus

### Water Leak Detection

```python
# In your water consumption prediction code
if predicted_flow > threshold:
    from templates import water_leak_alert
    message = water_leak_alert("Block A", predicted_flow)
    send_emergency_sms(message)
```

### Energy Anomaly Detection

```python
# In your energy forecasting code
if predicted_energy > expected * 1.5:
    from templates import energy_alert
    message = energy_alert("Building B", predicted_energy, expected)
    send_emergency_sms(message)
```

### Vision AI Security Alerts

```python
# In your YOLOv8 detection code
if detected_class == "unauthorized_person":
    from templates import security_alert
    message = security_alert("Main Entrance", "Unauthorized access")
    send_emergency_sms(message)
```

## 📈 Cost Optimization

- **Rate limiting**: Prevents accidental spam
- **Template reuse**: Consistent, efficient messages
- **Validation**: Rejects invalid messages before sending
- **Retry logic**: Prevents duplicate sends on transient failures

## 🚀 Next Steps

1. **Test with real SMS** - Run `python sms_service.py`
2. **Integrate with ML models** - Add to your prediction pipelines
3. **Add more recipients** - Update for security/maintenance teams
4. **Create dashboard** - Monitor alert history and delivery status
5. **Deploy to production** - Use with your AI Smart Campus system

## 📞 Support

For issues or questions:
- Check `examples.py` for usage patterns
- Review unit tests in `tests/test_sms_service.py`
- Consult Twilio documentation: https://www.twilio.com/docs

## 📝 License

Part of the AI Smart Campus project.
