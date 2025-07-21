#!/usr/bin/env python3
"""
Debug script to check SMS verification codes
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

def check_verification_codes():
    """Check recent verification codes"""
    print("🔍 Checking recent SMS verification codes...")
    print("=" * 50)
    
    # Get recent verification codes
    verifications = SMSVerification.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(hours=1)
    ).order_by('-created_at')
    
    if not verifications.exists():
        print("❌ No verification codes found in the last hour")
        return
    
    print(f"📱 Found {verifications.count()} verification code(s):")
    print()
    
    for i, verification in enumerate(verifications, 1):
        print(f"🔢 Verification #{i}:")
        print(f"   📞 Phone: {verification.phone_number}")
        print(f"   🔐 Code: {verification.verification_code}")
        print(f"   ⏰ Created: {verification.created_at}")
        print(f"   ⏰ Expires: {verification.expires_at}")
        print(f"   ✅ Valid: {verification.is_valid()}")
        print(f"   🔄 Used: {verification.is_used}")
        print(f"   📊 Attempts: {verification.attempts}")
        print()

if __name__ == '__main__':
    check_verification_codes() 