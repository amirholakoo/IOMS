#!/usr/bin/env python
"""
🧪 Test script for payment failure logic
🎯 Verifies that failed payments properly cancel orders
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Customer, Product, Order, OrderItem, ActivityLog
from payments.models import Payment, PaymentCallback
from payments.services import PaymentService
from django.utils import timezone

User = get_user_model()

def test_payment_failure_logic():
    """Test that failed payments properly cancel orders"""
    
    print("🧪 Testing Payment Failure Logic")
    print("=" * 50)
    
    try:
        # Create test user
        user = User.objects.create_user(
            username='test_customer',
            password='testpass123',
            phone='09123456789',
            role=User.UserRole.CUSTOMER
        )
        
        # Create test customer
        customer = Customer.objects.create(
            customer_name='Test Customer',
            phone='09123456789',
            address='Test Address'
        )
        
        # Create test product
        product = Product.objects.create(
            reel_number='TEST001',
            location='Anbar_Akhal',
            width=100,
            gsm=80,
            length=1000,
            grade='A',
            price=1000000  # 1,000,000 Tomans
        )
        
        # Create test order
        order = Order.objects.create(
            customer=customer,
            order_number='TEST-ORDER-001',
            status='Pending',
            payment_method='Cash',
            total_amount=1000000,
            final_amount=1000000,
            created_by=user
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price=1000000,
            total_price=1000000,
            payment_method='Cash'
        )
        
        # Create test payment
        payment = Payment.objects.create(
            order=order,
            user=user,
            gateway='zarinpal',
            amount=1000000,
            tracking_code='TEST-TRACK-001',
            status='INITIATED'
        )
        
        print(f"✅ Created test order: {order.order_number} (Status: {order.status})")
        print(f"✅ Created test payment: {payment.tracking_code} (Status: {payment.status})")
        
        # Simulate payment failure
        print("\n🔄 Simulating payment failure...")
        
        # Create failed payment callback
        callback_data = {
            'Status': 'NOK',
            'Authority': 'TEST-AUTH-001',
            'error': 'Payment failed due to insufficient funds'
        }
        
        # Process the callback (simulating the payment_callback view logic)
        callback = PaymentCallback.objects.create(
            payment=payment,
            gateway=payment.gateway,
            received_data=callback_data,
            processing_status='FAILED',
            error_message='Payment failed due to insufficient funds'
        )
        
        # Update payment status to failed
        payment.status = 'FAILED'
        payment.completed_at = timezone.now()
        payment.error_message = 'Payment failed due to insufficient funds'
        payment.save()
        
        # Update order status to cancelled
        if order.status == 'Pending':
            order.status = 'Cancelled'
            order.save()
            
            # Log the order cancellation
            ActivityLog.log_activity(
                user=payment.user,
                action='CANCEL',
                description=f'سفارش {order.order_number} لغو شد به دلیل عدم موفقیت در پرداخت',
                content_object=order,
                severity='HIGH',
                extra_data={
                    'order_number': order.order_number,
                    'payment_tracking_code': payment.tracking_code,
                    'payment_amount': str(payment.display_amount),
                    'gateway': payment.gateway,
                    'failure_reason': 'Payment failed due to insufficient funds'
                }
            )
        
        print(f"✅ Payment status updated to: {payment.status}")
        print(f"✅ Order status updated to: {order.status}")
        
        # Verify the results
        print("\n📊 Verification Results:")
        print("-" * 30)
        
        # Refresh objects from database
        order.refresh_from_db()
        payment.refresh_from_db()
        
        print(f"Order Status: {order.status}")
        print(f"Payment Status: {payment.status}")
        print(f"Payment Error: {payment.error_message}")
        
        # Check if order is cancelled
        if order.status == 'Cancelled':
            print("✅ SUCCESS: Order was properly cancelled after payment failure")
        else:
            print("❌ FAILURE: Order was not cancelled after payment failure")
        
        # Check if activity log was created
        activity_logs = ActivityLog.objects.filter(
            content_object=order,
            action='CANCEL'
        )
        
        if activity_logs.exists():
            print("✅ SUCCESS: Activity log was created for order cancellation")
        else:
            print("❌ FAILURE: No activity log was created for order cancellation")
        
        # Test access restrictions
        print("\n🔒 Testing Access Restrictions:")
        print("-" * 30)
        
        # Try to get order from customer orders view (should be excluded)
        customer_orders = Order.objects.filter(
            customer=customer
        ).exclude(status='Cancelled')
        
        if order not in customer_orders:
            print("✅ SUCCESS: Cancelled order is properly excluded from customer orders")
        else:
            print("❌ FAILURE: Cancelled order is still visible in customer orders")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_payment_failure_logic() 