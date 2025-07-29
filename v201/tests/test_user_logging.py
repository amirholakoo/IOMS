#!/usr/bin/env python
"""
🧪 Test script for user logging functionality
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
from core.middleware import set_current_user
from django.core.management import call_command

User = get_user_model()

def test_user_logging():
    """Test user logging functionality"""
    print("🧪 Testing User Logging Functionality")
    print("=" * 50)
    
    # Create a test user
    try:
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='admin'
        )
        print(f"✅ Created test user: {user.get_full_name()}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return
    
    # Test 1: Create customer without current user (should show 'system')
    print("\n📝 Test 1: Creating customer without current user")
    try:
        customer = Customer.objects.create(
            customer_name='Test Customer',
            phone='09123456789',
            address='Test Address'
        )
        print(f"✅ Created customer: {customer.customer_name}")
        print(f"📋 Logs: {customer.logs}")
    except Exception as e:
        print(f"❌ Error creating customer: {e}")
    
    # Test 2: Create customer with current user set
    print("\n📝 Test 2: Creating customer with current user")
    try:
        set_current_user(user)
        customer2 = Customer.objects.create(
            customer_name='Test Customer 2',
            phone='09123456788',
            address='Test Address 2'
        )
        print(f"✅ Created customer: {customer2.customer_name}")
        print(f"📋 Logs: {customer2.logs}")
    except Exception as e:
        print(f"❌ Error creating customer: {e}")
    
    # Test 3: Create order with current user
    print("\n📝 Test 3: Creating order with current user")
    try:
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',
            status='Pending',
            total_amount=100000,
            final_amount=100000
        )
        print(f"✅ Created order: {order.order_number}")
        print(f"📋 Logs: {order.logs}")
    except Exception as e:
        print(f"❌ Error creating order: {e}")
    
    # Test 4: Update customer with current user
    print("\n📝 Test 4: Updating customer with current user")
    try:
        customer.status = 'Inactive'
        customer.save()
        print(f"✅ Updated customer status")
        print(f"📋 Logs: {customer.logs}")
    except Exception as e:
        print(f"❌ Error updating customer: {e}")
    
    # Test 5: Export logs to CSV
    print("\n📤 Test 5: Exporting logs to CSV")
    try:
        call_command('export_logs_to_csv')
        print("✅ Logs exported to CSV successfully")
    except Exception as e:
        print(f"❌ Error exporting logs: {e}")
    
    # Cleanup
    print("\n🧹 Cleaning up test data")
    try:
        customer.delete()
        customer2.delete()
        order.delete()
        user.delete()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")
    
    print("\n✅ User logging test completed!")

if __name__ == '__main__':
    test_user_logging() 