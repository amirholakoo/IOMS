#!/usr/bin/env python
"""
🧪 تست سیستم پرداخت HomayOMS
📋 این اسکریپت برای تست کامل عملکرد سیستم پرداخت استفاده می‌شود
"""

import os
import sys
import django
from decimal import Decimal

# تنظیم مسیر Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from payments.models import Payment, PaymentCallback, PaymentRefund
from payments.services import PaymentService, ZarinPalGateway, ShaparakGateway
from core.models import Order, OrderItem, Customer, Product
from accounts.models import User


def test_payment_models():
    """🔍 تست مدل‌های پرداخت"""
    print("🔍 Testing Payment Models...")
    
    # تست ایجاد payment
    try:
        # دریافت یک سفارش موجود
        order = Order.objects.first()
        if not order:
            print("❌ No orders found. Please create an order first.")
            return False
        
        # ایجاد پرداخت تست
        payment = Payment.objects.create(
            order=order,
            amount=100000,  # 10,000 تومان = 100,000 ریال
            gateway='zarinpal',
            payer_phone='09123456789',
            description='تست پرداخت'
        )
        
        print(f"✅ Payment created: {payment.tracking_code}")
        print(f"   Amount: {payment.display_amount:,.0f} تومان")
        print(f"   Status: {payment.get_status_display_persian()}")
        
        # تست متدهای payment
        print(f"   Can retry: {payment.can_retry()}")
        print(f"   Is expired: {payment.is_expired()}")
        
        # تست PaymentCallback
        callback = PaymentCallback.objects.create(
            payment=payment,
            callback_type='VERIFY',
            raw_data={'test': 'data'},
            sender_ip='127.0.0.1'
        )
        print(f"✅ PaymentCallback created: {callback}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing payment models: {e}")
        return False


def test_payment_services():
    """🛠️ تست سرویس‌های پرداخت"""
    print("\n🛠️ Testing Payment Services...")
    
    try:
        # تست دریافت gateway
        zarinpal = PaymentService.get_gateway('zarinpal', sandbox=True)
        shaparak = PaymentService.get_gateway('shaparak', sandbox=True)
        
        print(f"✅ ZarinPal gateway: {zarinpal.__class__.__name__}")
        print(f"✅ Shaparak gateway: {shaparak.__class__.__name__}")
        
        # تست محاسبه مبلغ نقدی
        order = Order.objects.first()
        if order:
            cash_amount = PaymentService._calculate_cash_payment_amount(order)
            print(f"✅ Cash amount calculation: {cash_amount:,.0f} تومان")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing payment services: {e}")
        return False


def test_payment_creation():
    """💳 تست ایجاد پرداخت از سفارش"""
    print("\n💳 Testing Payment Creation from Order...")
    
    try:
        # دریافت سفارش با آیتم‌های نقدی
        order = Order.objects.filter(
            order_items__payment_method='Cash'
        ).first()
        
        if not order:
            print("❌ No orders with cash items found.")
            return False
        
        # ایجاد پرداخت
        payment = PaymentService.create_payment_from_order(
            order=order,
            gateway_name='zarinpal',
            user=order.created_by
        )
        
        print(f"✅ Payment created from order: {payment.tracking_code}")
        print(f"   Order: {order.order_number}")
        print(f"   Amount: {payment.display_amount:,.0f} تومان")
        print(f"   Gateway: {payment.get_gateway_display_persian()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating payment from order: {e}")
        return False


def test_gateway_classes():
    """🌐 تست کلاس‌های درگاه"""
    print("\n🌐 Testing Gateway Classes...")
    
    try:
        # تست ZarinPal sandbox
        zarinpal = ZarinPalGateway(sandbox=True)
        print(f"✅ ZarinPal sandbox initialized")
        print(f"   Merchant ID: {zarinpal.merchant_id}")
        print(f"   Base URL: {zarinpal.base_url}")
        
        # تست Shaparak sandbox
        shaparak = ShaparakGateway(sandbox=True)
        print(f"✅ Shaparak sandbox initialized")
        print(f"   Terminal ID: {shaparak.terminal_id}")
        print(f"   Base URL: {shaparak.base_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing gateway classes: {e}")
        return False


def test_csv_export():
    """📊 تست خروجی CSV"""
    print("\n📊 Testing CSV Export...")
    
    try:
        from django.core.management import call_command
        
        # تست خروجی لاگ‌های پرداخت
        call_command('export_payments_logs_to_csv')
        print("✅ Payment logs exported to CSV")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CSV export: {e}")
        return False


def cleanup_test_data():
    """🧹 پاک‌سازی داده‌های تست"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        # حذف پرداخت‌های تست
        test_payments = Payment.objects.filter(description__contains='تست')
        count = test_payments.count()
        test_payments.delete()
        
        print(f"✅ Cleaned up {count} test payments")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up test data: {e}")
        return False


def main():
    """🎯 اجرای تست‌های اصلی"""
    print("🚀 Starting Payment System Tests...")
    print("=" * 50)
    
    tests = [
        test_payment_models,
        test_payment_services, 
        test_payment_creation,
        test_gateway_classes,
        test_csv_export,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Payment system is ready! 🎉")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the errors above.")
    
    # پاک‌سازی
    cleanup_test_data()


if __name__ == '__main__':
    main() 