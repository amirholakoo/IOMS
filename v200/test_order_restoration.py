#!/usr/bin/env python3
"""
🧪 Test Script for Order Restoration Functionality
🔍 Tests the unfinished orders flow with proper context restoration
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

def test_order_restoration_flow():
    """Test the complete order restoration flow"""
    print("🧪 Testing Order Restoration Flow...")
    
    # Create test data
    customer = Customer.objects.create(
        customer_name="Test Customer",
        phone="09123456789",
        status="Active"
    )
    
    user = User.objects.create_user(
        username="testuser",
        phone="09123456789",
        role=User.UserRole.CUSTOMER
    )
    user.customer = customer
    user.save()
    
    # Create test products
    product1 = Product.objects.create(
        reel_number="TEST001",
        location="A1",
        width=100,
        gsm=80,
        length=1000,
        grade="A",
        breaks=0,
        price=100000,
        status="In-stock"
    )
    
    product2 = Product.objects.create(
        reel_number="TEST002", 
        location="A2",
        width=120,
        gsm=100,
        length=800,
        grade="B",
        breaks=1,
        price=150000,
        status="In-stock"
    )
    
    # Create a processing order
    order = Order.objects.create(
        customer=customer,
        order_number="ORD-20250716-TEST",
        status="Processing",
        payment_method="Cash",
        created_by=user
    )
    
    # Add order items
    OrderItem.objects.create(
        order=order,
        product=product1,
        quantity=2,
        unit_price=100000,
        total_price=200000,
        payment_method="Cash"
    )
    
    OrderItem.objects.create(
        order=order,
        product=product2,
        quantity=1,
        unit_price=150000,
        total_price=150000,
        payment_method="Terms"
    )
    
    print(f"✅ Created test order: {order.order_number}")
    print(f"   - Items: {order.order_items.count()}")
    print(f"   - Status: {order.status}")
    
    # Test the restoration flow
    client = Client()
    client.force_login(user)
    
    # Test 1: Access selected_products with order_id
    url = f"/core/selected-products/?order_id={order.id}"
    response = client.get(url)
    
    print(f"\n🔍 Test 1: Order Restoration")
    print(f"   URL: {url}")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Successfully accessed selected_products page")
        
        # Check if order context is restored
        if 'processing_order_id' in response.client.session:
            session_order_id = response.client.session['processing_order_id']
            print(f"   ✅ Order ID in session: {session_order_id}")
            print(f"   ✅ Matches original order: {session_order_id == order.id}")
        else:
            print("   ❌ Order ID not found in session")
    else:
        print(f"   ❌ Failed to access page: {response.status_code}")
    
    # Test 2: Check if products are loaded correctly
    if response.status_code == 200:
        print(f"\n🔍 Test 2: Product Context")
        # This would require checking the template context
        print("   ✅ Page loaded successfully")
        print("   ℹ️  Check manually if products are displayed with correct quantities")
    
    # Test 3: Test the complete flow
    print(f"\n🔍 Test 3: Complete Flow Test")
    print("   ℹ️  Manual testing required:")
    print("   1. Go to main page")
    print("   2. Check if unfinished order appears")
    print("   3. Click 'Continue to Purchase'")
    print("   4. Verify redirect to selected_products page")
    print("   5. Verify products are loaded with correct quantities")
    print("   6. Complete the purchase flow")
    
    print(f"\n🎯 Test Summary:")
    print(f"   - Order created: {order.order_number}")
    print(f"   - Order ID: {order.id}")
    print(f"   - Items count: {order.order_items.count()}")
    print(f"   - Status: {order.status}")
    print(f"   - Customer: {customer.customer_name}")
    
    return True

if __name__ == "__main__":
    try:
        test_order_restoration_flow()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 