#!/usr/bin/env python
"""
🧪 Test script for comprehensive logging functionality
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Customer, Order
from payments.models import Payment
from core.middleware import set_current_user
from django.core.management import call_command

User = get_user_model()

def test_comprehensive_logging():
    """Test comprehensive logging functionality for all models"""
    print("🧪 Testing Comprehensive Logging Functionality")
    print("=" * 60)
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='test_logger',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Logger'
        )
        print(f"✅ Created test user: {user.get_full_name()}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return
    
    try:
        # Set current user for logging
        set_current_user(user)
        
        # Test 1: Create customer with comprehensive logging
        print("\n📝 Test 1: Creating customer with comprehensive logging")
        customer = Customer.objects.create(
            customer_name='Test Customer for Logging',
            phone='09123456789',
            address='Test Address for Comprehensive Logging',
            status='Active'
        )
        print(f"✅ Created customer: {customer.customer_name}")
        print(f"📋 Logs: {customer.logs}")
        
        # Test 2: Update customer
        print("\n📝 Test 2: Updating customer")
        customer.status = 'Inactive'
        customer.customer_name = 'Updated Customer Name'
        customer.save()
        print(f"✅ Updated customer")
        print(f"📋 Logs: {customer.logs}")
        
        # Test 3: Create order with comprehensive logging
        print("\n📝 Test 3: Creating order with comprehensive logging")
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',
            status='Pending',
            total_amount=500000,
            discount_percentage=10,
            final_amount=450000
        )
        print(f"✅ Created order: {order.order_number}")
        print(f"📋 Logs: {order.logs}")
        
        # Test 4: Update order
        print("\n📝 Test 4: Updating order")
        order.status = 'Confirmed'
        order.payment_method = 'Terms'
        order.save()
        print(f"✅ Updated order")
        print(f"📋 Logs: {order.logs}")
        
        # Test 5: Create payment with comprehensive logging
        print("\n📝 Test 5: Creating payment with comprehensive logging")
        payment = Payment.objects.create(
            order=order,
            amount=4500000,  # 450,000 Toman in Rials
            gateway='zarinpal',
            status='INITIATED'
        )
        print(f"✅ Created payment: {payment.tracking_code}")
        print(f"📋 Logs: {payment.logs}")
        
        # Test 6: Update payment
        print("\n📝 Test 6: Updating payment")
        payment.status = 'SUCCESS'
        payment.gateway_transaction_id = 'TEST123456'
        payment.save()
        print(f"✅ Updated payment")
        print(f"📋 Logs: {payment.logs}")
        
        # Test 7: Export all logs to CSV
        print("\n📤 Test 7: Exporting all logs to CSV")
        try:
            call_command('export_logs_to_csv')
            call_command('export_payments_logs_to_csv')
            print("✅ All logs exported to CSV successfully")
        except Exception as e:
            print(f"❌ Error exporting logs: {e}")
        
        # Test 8: Show log format comparison
        print("\n📊 Test 8: Log Format Comparison")
        print("Customer Log Format:")
        print(f"  {customer.logs[:200]}...")
        print("\nOrder Log Format:")
        print(f"  {order.logs[:200]}...")
        print("\nPayment Log Format:")
        print(f"  {payment.logs[:200]}...")
        
        # Cleanup
        print("\n🧹 Cleaning up test data")
        try:
            payment.delete()
            order.delete()
            customer.delete()
            user.delete()
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up: {e}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n✅ Comprehensive logging test completed!")

if __name__ == "__main__":
    test_comprehensive_logging() 