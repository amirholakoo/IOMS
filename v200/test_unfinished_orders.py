#!/usr/bin/env python3
"""
🧪 Test Script for Unfinished Orders Functionality
🔍 Tests the order continuation flow and payment processing
"""

import os
import sys
import django
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/darbandi/Downloads/mori/v200')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Order, OrderItem, Product, Customer
from payments.models import Payment

User = get_user_model()

def test_unfinished_orders_flow():
    """Test the complete unfinished orders flow"""
    print("🧪 Testing Unfinished Orders Flow...")
    
    # Create test data
    print("📝 Creating test data...")
    
    # Create a test customer
    customer = Customer.objects.create(
        customer_name="Test Customer",
        phone="09123456789",
        status="Active"
    )
    
    # Create a test user
    user = User.objects.create_user(
        username="testcustomer",
        first_name="Test",
        last_name="Customer",
        phone="09123456789",
        role=User.UserRole.CUSTOMER
    )
    
    # Create test products
    product1 = Product.objects.create(
        reel_number="TEST001",
        location="Warehouse A",
        width=100,
        gsm=80,
        length=1000,
        grade="A",
        price=100000,
        status="In-stock"
    )
    
    product2 = Product.objects.create(
        reel_number="TEST002",
        location="Warehouse B",
        width=120,
        gsm=100,
        length=800,
        grade="B",
        price=150000,
        status="In-stock"
    )
    
    # Create an unfinished order (Processing status)
    processing_order = Order.objects.create(
        customer=customer,
        payment_method="Cash",
        status="Processing",
        order_number="TEST-001",
        total_amount=250000,
        final_amount=250000,
        created_by=user
    )
    
    # Add items to the processing order
    OrderItem.objects.create(
        order=processing_order,
        product=product1,
        quantity=1,
        unit_price=100000,
        total_price=100000,
        payment_method="Cash"
    )
    
    OrderItem.objects.create(
        order=processing_order,
        product=product2,
        quantity=1,
        unit_price=150000,
        total_price=150000,
        payment_method="Cash"
    )
    
    # Create a pending order (no payment initiated)
    pending_order = Order.objects.create(
        customer=customer,
        payment_method="Cash",
        status="Pending",
        order_number="TEST-002",
        total_amount=100000,
        final_amount=100000,
        created_by=user
    )
    
    OrderItem.objects.create(
        order=pending_order,
        product=product1,
        quantity=1,
        unit_price=100000,
        total_price=100000,
        payment_method="Cash"
    )
    
    print(f"✅ Created test data:")
    print(f"   - Customer: {customer.customer_name}")
    print(f"   - User: {user.username}")
    print(f"   - Processing Order: {processing_order.order_number}")
    print(f"   - Pending Order: {pending_order.order_number}")
    
    # Test the index view (should show unfinished orders)
    print("\n🔍 Testing index view...")
    client = Client()
    client.force_login(user)
    
    response = client.get(reverse('core:products_landing'))
    print(f"   - Status Code: {response.status_code}")
    print(f"   - Template: {response.template_name}")
    
    if response.status_code == 200:
        print("   ✅ Index view loads successfully")
        
        # Check if unpaid orders are in context
        if hasattr(response, 'context') and 'unpaid_orders' in response.context:
            unpaid_orders = response.context['unpaid_orders']
            print(f"   - Unpaid Orders Count: {len(unpaid_orders)}")
            print(f"   - Total Amount: {response.context.get('unpaid_orders_total', 0)}")
            
            for order in unpaid_orders:
                print(f"     * {order.order_number}: {order.status} - {order.incomplete_reason}")
        else:
            print("   ⚠️ No unpaid_orders in context")
    else:
        print("   ❌ Index view failed to load")
    
    # Test the complete processing order endpoint
    print("\n🔄 Testing complete processing order...")
    response = client.post(
        reverse('core:complete_processing_order', kwargs={'order_id': processing_order.id}),
        content_type='application/json'
    )
    
    print(f"   - Status Code: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Complete processing order endpoint works")
    else:
        print("   ❌ Complete processing order endpoint failed")
    
    # Test the process incomplete orders endpoint
    print("\n🔄 Testing process incomplete orders...")
    response = client.post(
        reverse('core:process_incomplete_orders'),
        content_type='application/json'
    )
    
    print(f"   - Status Code: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Process incomplete orders endpoint works")
    else:
        print("   ❌ Process incomplete orders endpoint failed")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    processing_order.delete()
    pending_order.delete()
    product1.delete()
    product2.delete()
    user.delete()
    customer.delete()
    
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    test_unfinished_orders_flow() 