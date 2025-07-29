#!/usr/bin/env python3
"""
Debug script to check session data and verification process
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from sms.models import SMSVerification
from django.utils import timezone

def debug_verification_process(phone_number, entered_code):
    """Debug the verification process step by step"""
    print(f"🔍 Debugging verification for phone: {phone_number}")
    print(f"🔢 Entered code: {entered_code}")
    print("=" * 60)
    
    # Check all verification codes for this phone
    verifications = SMSVerification.objects.filter(
        phone_number=phone_number
    ).order_by('-created_at')
    
    print(f"📱 Found {verifications.count()} verification codes:")
    print()
    
    for i, verification in enumerate(verifications, 1):
        print(f"🔢 Code #{i}: {verification.verification_code}")
        print(f"   📞 Phone: {verification.phone_number}")
        print(f"   ⏰ Created: {verification.created_at}")
        print(f"   ⏰ Expires: {verification.expires_at}")
        print(f"   ✅ Valid: {verification.is_valid()}")
        print(f"   🔄 Used: {verification.is_used}")
        print(f"   📊 Attempts: {verification.attempts}")
        print(f"   🎯 Matches entered code: {verification.verification_code == entered_code}")
        print()
    
    # Check what the new verification logic would find
    print("🔍 Testing new verification logic:")
    try:
        from sms.services import get_sms_service
        sms_service = get_sms_service()
        success, result = sms_service.verify_code(phone_number, entered_code)
        print(f"✅ SMS Service result: {success}")
        print(f"📝 Result message: {result}")
    except Exception as e:
        print(f"❌ SMS Service error: {e}")
    
    print("=" * 60)

if __name__ == '__main__':
    # Test with your phone number and a code you tried
    phone = "09109462034"
    code = input("Enter the code you tried to verify: ")
    debug_verification_process(phone, code) 