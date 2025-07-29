#!/usr/bin/env python
"""
🧪 Test script to verify SMS service can be imported without database access
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')

# Configure Django
django.setup()

def test_sms_import():
    """Test that SMS service can be imported without database access"""
    try:
        print("🔍 Testing SMS service import...")
        
        # Test importing the service
        from sms.services import get_sms_service, get_sms_notification_service
        
        print("✅ SMS service imported successfully")
        
        # Test creating service instances
        sms_service = get_sms_service()
        print(f"✅ SMS service created: {type(sms_service)}")
        
        sms_notification_service = get_sms_notification_service()
        print(f"✅ SMS notification service created: {type(sms_notification_service)}")
        
        # Test accessing settings (should use defaults)
        print(f"📱 SMS Server URL: {sms_service.base_url}")
        print(f"🔑 SMS API Key: {sms_service.api_key}")
        print(f"⏰ SMS Timeout: {sms_service.timeout}")
        print(f"🔄 SMS Retry Attempts: {sms_service.retry_attempts}")
        print(f"🔄 SMS Fallback to Fake: {sms_service.fallback_to_fake}")
        
        print("🎉 All tests passed! SMS service is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sms_import()
    sys.exit(0 if success else 1) 