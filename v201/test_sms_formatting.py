#!/usr/bin/env python3
"""
SMS Formatting Test Script
Demonstrates beautiful SMS message formatting
"""

from sms.services import SMSService
from datetime import datetime, timedelta
from django.utils import timezone

def test_sms_formatting():
    """
    Test all SMS formatting methods
    """
    print("Testing Beautiful SMS Formatting")
    print("=" * 50)
    
    # Initialize SMS service
    sms_service = SMSService()
    
    # Test data
    phone_number = "+989123456789"
    verification_code = "123456"
    expires_at = timezone.now() + timedelta(minutes=10)
    customer_name = "John Doe"
    order_number = "ORD-20250121-ABC123"
    amount = 1500000  # 1.5M Toman
    
    print("\n1. Verification SMS Messages:")
    print("-" * 30)
    
    # Standard verification
    message1 = sms_service._format_verification_sms_message(phone_number, verification_code, expires_at)
    print("Standard:")
    print(message1)
    
    # Compact verification
    message2 = sms_service._format_verification_sms_compact(phone_number, verification_code, expires_at)
    print("\nCompact:")
    print(message2)
    
    # Detailed verification
    message3 = sms_service._format_verification_sms_detailed(phone_number, verification_code, expires_at)
    print("\nDetailed:")
    print(message3)
    
    print("\n2. Customer Activation Message:")
    print("-" * 30)
    activation_message = sms_service._format_customer_activation_message(customer_name, None)
    print(activation_message)
    
    print("\n3. Order Status Messages:")
    print("-" * 30)
    
    # Different order statuses
    statuses = ['Pending', 'Processing', 'Confirmed', 'Ready', 'Delivered', 'Cancelled']
    for status in statuses:
        status_message = sms_service._format_order_status_message(order_number, status, amount)
        print(f"\n{status}:")
        print(status_message)
    
    print("\n4. Payment Messages:")
    print("-" * 30)
    
    # Payment success
    payment_success = sms_service._format_payment_success_message(order_number, amount)
    print("Payment Success:")
    print(payment_success)
    
    # Payment failed
    payment_failed = sms_service._format_payment_failed_message(order_number)
    print("\nPayment Failed:")
    print(payment_failed)
    
    print("\n5. Welcome Message:")
    print("-" * 30)
    welcome_message = sms_service._format_welcome_message(customer_name)
    print(welcome_message)
    
    print("\n" + "=" * 50)
    print("SMS Formatting Test Complete!")
    print("All messages are beautifully formatted with clean, professional styling.")

if __name__ == "__main__":
    # Set up Django environment
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
    django.setup()
    
    test_sms_formatting() 