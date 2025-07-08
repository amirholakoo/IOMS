#!/usr/bin/env python
"""
🔍 Debug script for SMS login issue
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()

from accounts.models import User

def debug_sms_login():
    """Debug SMS login functionality"""
    print("🔍 DEBUGGING SMS LOGIN ISSUE")
    print("=" * 50)
    
    # Test phone number
    phone = "099378592348"
    print(f"📞 Testing phone: {phone}")
    
    # Check if user exists
    try:
        user = User.objects.get(phone=phone)
        print(f"✅ User found: {user.username}")
        print(f"📊 Role: {user.role}")
        print(f"📊 Status: {user.status}")
        print(f"✅ is_active: {user.is_active}")
        print(f"✅ is_active_user(): {user.is_active_user()}")
        print(f"🔵 is_customer(): {user.is_customer()}")
        
        # Test the exact query from the view
        try:
            customer_user = User.objects.get(phone=phone, role=User.UserRole.CUSTOMER)
            print(f"✅ Customer query successful: {customer_user.username}")
            
            if customer_user.is_active_user():
                print("✅ User is active and can login via SMS")
            else:
                print("❌ User is not active")
                
        except User.DoesNotExist:
            print("❌ Customer query failed - User.DoesNotExist")
            
    except User.DoesNotExist:
        print("❌ User not found with this phone number")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 ALL CUSTOMER USERS:")
    customers = User.objects.filter(role='customer')
    for customer in customers:
        print(f"👤 {customer.username} | 📞 {customer.phone} | 📊 {customer.status} | ✅ {customer.is_active_user()}")

if __name__ == "__main__":
    debug_sms_login() 