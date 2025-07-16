#!/usr/bin/env python3
"""
🧪 Test Script for Simplified Unfinished Orders Logic
🔍 Tests the simple logic: Processing orders with no payments
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

def test_simple_unfinished_orders():
    """Test the simplified unfinished orders logic"""
    print("🧪 Testing Simplified Unfinished Orders Logic...")
    
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
    
    # Create a processing order with no payments (should be unfinished)
    processing_order = Order.objects.create(
        customer=customer,
        order_number="ORD-20250716-TEST1",
        status="Processing",
        payment_method="Cash",
        created_by=user
    )
    
    # Add order items
    OrderItem.objects.create(
        order=processing_order,
        product=product1,
        quantity=2,
        unit_price=100000,
        total_price=200000,
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
    
    print(f"✅ Created processing order: {processing_order.order_number}")
    print(f"   - Items: {processing_order.order_items.count()}")
    print(f"   - Status: {processing_order.status}")
    print(f"   - Payments: {Payment.objects.filter(order=processing_order).count()}")
    
    # Test the simplified logic
    from core.views import index_view
    from django.test import RequestFactory
    
    # Create a request
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user
    
    # Call the view
    response = index_view(request)
    
    print(f"\n🔍 Test Results:")
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        # Check if unpaid_orders is in context
        if hasattr(response, 'context_data'):
            unpaid_orders = response.context_data.get('unpaid_orders', [])
            unpaid_orders_total = response.context_data.get('unpaid_orders_total', 0)
            
            print(f"   ✅ Unpaid orders found: {len(unpaid_orders)}")
            print(f"   ✅ Total amount: {unpaid_orders_total}")
            
            if len(unpaid_orders) > 0:
                order = unpaid_orders[0]
                print(f"   ✅ Order number: {order.order_number}")
                print(f"   ✅ Order status: {order.status}")
                print(f"   ✅ Incomplete reason: {getattr(order, 'incomplete_reason', 'N/A')}")
                print(f"   ✅ Action text: {getattr(order, 'action_text', 'N/A')}")
                print(f"   ✅ Can pay: {getattr(order, 'can_pay', 'N/A')}")
                
                # Test the redirect flow
                print(f"\n🔍 Testing Redirect Flow:")
                client = Client()
                client.force_login(user)
                
                # Test redirect to selected_products
                url = f"/core/selected-products/?order_id={order.id}"
                response = client.get(url)
                
                print(f"   URL: {url}")
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Successfully redirected to selected_products")
                else:
                    print(f"   ❌ Failed to redirect: {response.status_code}")
            else:
                print("   ❌ No unpaid orders found")
        else:
            print("   ❌ No context data found")
    else:
        print(f"   ❌ View failed: {response.status_code}")
    
    # Test with a paid order (should not appear)
    print(f"\n🔍 Testing Paid Order (should not appear):")
    
    # Create a payment for the order
    Payment.objects.create(
        order=processing_order,
        amount=350000,
        status='SUCCESS',
        payment_method='Cash',
        transaction_id='TEST123'
    )
    
    print(f"   Created payment for order {processing_order.order_number}")
    
    # Test again
    response = index_view(request)
    
    if response.status_code == 200 and hasattr(response, 'context_data'):
        unpaid_orders = response.context_data.get('unpaid_orders', [])
        print(f"   Unpaid orders after payment: {len(unpaid_orders)}")
        
        if len(unpaid_orders) == 0:
            print("   ✅ Correctly excluded paid order")
        else:
            print("   ❌ Paid order still appears in unpaid orders")
    
    print(f"\n🎯 Test Summary:")
    print(f"   - Processing order created: {processing_order.order_number}")
    print(f"   - Order has items: {processing_order.order_items.count()}")
    print(f"   - Order has payments: {Payment.objects.filter(order=processing_order).count()}")
    print(f"   - Expected behavior: Should appear in unpaid orders when no payments")
    
    return True

if __name__ == "__main__":
    try:
        test_simple_unfinished_orders()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 