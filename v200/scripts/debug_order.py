#!/usr/bin/env python3
"""
🔍 Debug Script for Order ORD-20250716-XML3
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append('/home/darbandi/Downloads/mori/v200')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()

from core.models import Order, OrderItem, Product, Customer
from payments.models import Payment

def debug_order():
    """Debug the specific order"""
    print("🔍 Debugging Order ORD-20250716-XML3...")
    
    try:
        # Find the order
        order = Order.objects.get(order_number="ORD-20250716-XML3")
        print(f"✅ Found order: {order.order_number}")
        print(f"   - Status: {order.status}")
        print(f"   - Customer: {order.customer.customer_name}")
        print(f"   - Created: {order.created_at}")
        print(f"   - Payment method: {order.payment_method}")
        
        # Check payments
        payments = Payment.objects.filter(order=order)
        print(f"   - Payments count: {payments.count()}")
        
        # Check order items
        items = order.order_items.all()
        print(f"   - Items count: {items.count()}")
        
        if items.count() > 0:
            print("\n📦 Order Items:")
            total = 0
            for i, item in enumerate(items, 1):
                print(f"   {i}. Product: {item.product.reel_number}")
                print(f"      - Quantity: {item.quantity}")
                print(f"      - Unit Price: {item.unit_price}")
                print(f"      - Total Price: {item.total_price}")
                print(f"      - Payment Method: {item.payment_method}")
                
                # Calculate what it should be
                calculated_total = item.unit_price * item.quantity
                print(f"      - Calculated Total: {calculated_total}")
                
                if item.total_price != calculated_total:
                    print(f"      - ⚠️  MISMATCH: total_price ({item.total_price}) != calculated ({calculated_total})")
                
                total += item.total_price
            
            print(f"\n💰 Order Totals:")
            print(f"   - Sum of item totals: {total}")
            print(f"   - Order total_amount: {order.total_amount}")
            print(f"   - Order final_amount: {order.final_amount}")
            
            # Check if we need to fix the totals
            if total == 0 and items.count() > 0:
                print("\n🔧 Fixing order totals...")
                for item in items:
                    if item.total_price == 0:
                        item.total_price = item.unit_price * item.quantity
                        item.save()
                        print(f"   - Fixed item {item.product.reel_number}: {item.total_price}")
                
                # Recalculate order totals
                order.calculate_final_amount()
                order.save()
                print(f"   - Fixed order final_amount: {order.final_amount}")
        else:
            print("   - ❌ No items found in order")
        
    except Order.DoesNotExist:
        print("❌ Order ORD-20250716-XML3 not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_order() 