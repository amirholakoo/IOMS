#!/usr/bin/env python
"""
Test script for the new order flow in v1.1
Tests that orders are created when customers visit selected products page
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from core.models import Product, Customer, Order, ActivityLog
from accounts.models import User

def test_new_order_flow():
    """Test the new order flow where orders are created on page visit"""
    print("🧪 Testing new order flow...")
    
    # Get or create a test customer
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='test_customer',
        defaults={
            'email': 'test@example.com',
            'phone': '09123456789',
            'role': 'customer'
        }
    )
    
    if created:
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")
    
    # Get or create customer
    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Test Customer',
            'phone': '09123456789',
            'status': 'active'
        }
    )
    
    if created:
        print(f"✅ Created test customer: {customer.name}")
    else:
        print(f"✅ Using existing test customer: {customer.name}")
    
    # Get some products
    products = Product.objects.filter(is_active=True)[:3]
    if not products.exists():
        print("❌ No active products found. Creating test products...")
        # Create test products
        for i in range(3):
            Product.objects.create(
                reel_number=f'TEST-{i+1:03d}',
                width=1000 + (i * 100),
                gsm=80 + (i * 10),
                length=100 + (i * 50),
                price=50000 + (i * 10000),
                is_active=True
            )
        products = Product.objects.filter(is_active=True)[:3]
    
    print(f"✅ Found {products.count()} products for testing")
    
    # Create client and login
    client = Client()
    
    # Test 1: Visit selected products page without login
    print("\n📋 Test 1: Visit selected products page without login")
    response = client.get(reverse('core:selected_products'))
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Correctly redirected to login (expected)")
    else:
        print("   ❌ Unexpected response")
    
    # Test 2: Login and visit selected products page
    print("\n📋 Test 2: Login and visit selected products page")
    login_response = client.post(reverse('accounts:customer_login'), {
        'phone': '09123456789',
        'password': 'testpass123'
    })
    
    if login_response.status_code == 302:
        print("   ✅ Login successful")
        
        # Check initial order count
        initial_orders = Order.objects.filter(customer=customer).count()
        print(f"   📊 Initial orders count: {initial_orders}")
        
        # Visit selected products page
        response = client.get(reverse('core:selected_products'))
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Successfully accessed selected products page")
            
            # Check if new order was created
            final_orders = Order.objects.filter(customer=customer).count()
            print(f"   📊 Final orders count: {final_orders}")
            
            if final_orders > initial_orders:
                print("   ✅ New order created successfully!")
                
                # Check the latest order
                latest_order = Order.objects.filter(customer=customer).latest('created_at')
                print(f"   📋 Latest order status: {latest_order.status}")
                print(f"   📋 Latest order created: {latest_order.created_at}")
                
                # Check for activity log
                logs = ActivityLog.objects.filter(
                    action='order_created',
                    customer=customer
                ).order_by('-timestamp')
                
                if logs.exists():
                    latest_log = logs.first()
                    print(f"   📝 Activity log created: {latest_log.action}")
                    print(f"   📝 Log timestamp: {latest_log.timestamp}")
                else:
                    print("   ⚠️ No activity log found")
                    
            else:
                print("   ❌ No new order created")
        else:
            print("   ❌ Failed to access selected products page")
    else:
        print("   ❌ Login failed")
    
    # Test 3: Check order processing
    print("\n📋 Test 3: Process order with mixed payment methods")
    
    # Get the latest order
    latest_order = Order.objects.filter(customer=customer).latest('created_at')
    
    # Simulate order processing with mixed payment methods
    order_data = {
        'product_id_1': products[0].id,
        'quantity_1': 2,
        'payment_method_1': 'Cash',
        'product_id_2': products[1].id,
        'quantity_2': 1,
        'payment_method_2': 'Terms',
    }
    
    response = client.post(reverse('core:process_order'), order_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Order processing successful")
        
        # Check updated orders
        updated_orders = Order.objects.filter(customer=customer).order_by('-created_at')
        print(f"   📊 Total orders after processing: {updated_orders.count()}")
        
        for i, order in enumerate(updated_orders[:3]):
            print(f"   📋 Order {i+1}: Status={order.status}, Items={order.items.count()}")
            
    else:
        print("   ❌ Order processing failed")
    
    print("\n🎉 Order flow testing completed!")

if __name__ == '__main__':
    test_new_order_flow() 