#!/usr/bin/env python
"""
Test script to verify complete_processing_order_view functionality
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/home/darbandi/Downloads/mori/v200')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mori.settings')
django.setup()

from core.models import Order, OrderItem, Product, Customer
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()

def test_processing_orders():
    """Test the processing orders functionality"""
    
    print("🔍 Testing Processing Orders...")
    
    # Find all Processing orders
    processing_orders = Order.objects.filter(status='Processing')
    print(f"Found {processing_orders.count()} Processing orders")
    
    for order in processing_orders:
        print(f"\n📋 Order {order.order_number}:")
        print(f"   - Customer: {order.customer.customer_name}")
        print(f"   - Items count: {order.order_items.count()}")
        print(f"   - Total amount: {order.total_amount}")
        print(f"   - Final amount: {order.final_amount}")
        
        # Check OrderItems
        for item in order.order_items.all():
            print(f"   - Item: {item.product.reel_number} - Qty: {item.quantity} - Price: {item.total_price} - Payment: {item.payment_method}")
        
        # Check if order has zero total
        if order.total_amount == 0:
            print(f"   ⚠️  WARNING: Order has zero total amount!")
            
            # Calculate from OrderItems
            calculated_total = order.order_items.aggregate(
                total=Sum('total_price')
            )['total'] or 0
            print(f"   📊 Calculated total from items: {calculated_total}")
            
            if calculated_total > 0:
                print(f"   🔧 Order needs recalculation!")

def test_complete_processing_logic():
    """Test the logic that would be used in complete_processing_order_view"""
    
    print("\n🧪 Testing Complete Processing Logic...")
    
    # Find a Processing order with items
    processing_order = Order.objects.filter(
        status='Processing',
        order_items__isnull=False
    ).first()
    
    if not processing_order:
        print("❌ No Processing orders with items found")
        return
    
    print(f"📋 Testing with Order {processing_order.order_number}")
    
    # Simulate the completion logic
    from django.db import transaction
    
    with transaction.atomic():
        # Update all OrderItems to Cash
        processing_order.order_items.update(payment_method='Cash')
        
        # Recalculate totals
        for item in processing_order.order_items.all():
            item.save()
        
        # Update order
        processing_order.payment_method = 'Cash'
        processing_order.status = 'Pending'
        processing_order.save()
        
        print(f"✅ Order updated:")
        print(f"   - Status: {processing_order.status}")
        print(f"   - Payment method: {processing_order.payment_method}")
        print(f"   - Total amount: {processing_order.total_amount}")
        print(f"   - Final amount: {processing_order.final_amount}")
        
        # Check OrderItems
        for item in processing_order.order_items.all():
            print(f"   - Item payment method: {item.payment_method}")

if __name__ == "__main__":
    test_processing_orders()
    test_complete_processing_logic() 