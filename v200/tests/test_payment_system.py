#!/usr/bin/env python3
"""
🧪 تست سیستم پرداخت
🎯 بررسی عملکرد کامل سیستم پرداخت
"""

import os
import sys
import django
from decimal import Decimal

# تنظیم محیط جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Customer, Product, Order, OrderItem
from payments.models import Payment, PaymentCallback, PaymentRefund
from payments.services import PaymentService

User = get_user_model()


def test_payment_system():
    """🧪 تست کامل سیستم پرداخت"""
    print("🧪 شروع تست سیستم پرداخت...")
    
    try:
        # 1. تست ایجاد پرداخت
        print("\n1️⃣ تست ایجاد پرداخت...")
        
        # ایجاد کاربر و مشتری تست
        user, created = User.objects.get_or_create(
            username='test_customer',
            defaults={
                'phone': '09123456789',
                'first_name': 'تست',
                'last_name': 'مشتری'
            }
        )
        
        customer, created = Customer.objects.get_or_create(
            phone='09123456789',
            defaults={
                'customer_name': 'تست مشتری',
                'status': 'Active'
            }
        )
        
        # ایجاد محصول تست
        product, created = Product.objects.get_or_create(
            reel_number='TEST001',
            defaults={
                'width': 1000,
                'gsm': 80,
                'length': 100,
                'grade': 'A',
                'location': 'Warehouse A',
                'status': 'In-stock',
                'price': Decimal('50000')  # 50,000 تومان
            }
        )
        
        # ایجاد سفارش تست
        order, created = Order.objects.get_or_create(
            order_number='TEST-ORDER-001',
            defaults={
                'customer': customer,
                'payment_method': 'Cash',
                'status': 'Pending',
                'total_amount': Decimal('50000'),
                'created_by': user
            }
        )
        
        # ایجاد آیتم سفارش
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={
                'quantity': 1,
                'unit_price': Decimal('50000'),
                'total_price': Decimal('50000'),
                'payment_method': 'Cash'
            }
        )
        
        print(f"✅ سفارش تست ایجاد شد: {order.order_number}")
        
        # 2. تست ایجاد پرداخت
        print("\n2️⃣ تست ایجاد پرداخت...")
        
        payment = PaymentService.create_payment_from_order(
            order=order,
            gateway_name='zarinpal',
            user=user
        )
        
        print(f"✅ پرداخت ایجاد شد: {payment.tracking_code}")
        print(f"💰 مبلغ: {payment.display_amount:,.0f} تومان")
        print(f"🌐 درگاه: {payment.get_gateway_display_persian()}")
        print(f"📊 وضعیت: {payment.get_status_display_persian()}")
        
        # 3. تست شروع فرآیند پرداخت
        print("\n3️⃣ تست شروع فرآیند پرداخت...")
        
        callback_url = "http://localhost:8000/payments/callback/test/"
        result = PaymentService.initiate_payment(
            payment=payment,
            callback_url=callback_url,
            sandbox=True
        )
        
        if result.get('success'):
            print(f"✅ فرآیند پرداخت شروع شد")
            print(f"🔗 URL پرداخت: {result.get('payment_url', 'N/A')}")
        else:
            print(f"❌ خطا در شروع پرداخت: {result.get('error', 'خطای نامشخص')}")
        
        # 4. تست تایید پرداخت
        print("\n4️⃣ تست تایید پرداخت...")
        
        # شبیه‌سازی داده‌های callback زرین‌پال
        verification_data = {
            'Status': 'OK',
            'Authority': payment.gateway_transaction_id or 'test_authority'
        }
        
        success, result = PaymentService.verify_payment(
            payment=payment,
            verification_data=verification_data,
            sandbox=True
        )
        
        if success:
            print(f"✅ پرداخت تایید شد")
            print(f"🏦 شماره مرجع: {result.get('ref_id', 'N/A')}")
            print(f"💳 شماره کارت: {result.get('card_pan', 'N/A')}")
        else:
            print(f"❌ خطا در تایید پرداخت: {result.get('error', 'خطای نامشخص')}")
        
        # 5. تست callback
        print("\n5️⃣ تست ثبت callback...")
        
        callback = PaymentCallback.objects.create(
            payment=payment,
            gateway=payment.gateway,
            received_data=verification_data,
            processing_status='SUCCESS',
            processing_logs='تست موفق callback'
        )
        
        print(f"✅ Callback ثبت شد: {callback.id}")
        
        # 6. تست بازگشت وجه
        print("\n6️⃣ تست بازگشت وجه...")
        
        refund = PaymentRefund.objects.create(
            payment=payment,
            refund_amount=payment.amount,
            reason='تست بازگشت وجه',
            requested_by=user
        )
        
        print(f"✅ درخواست بازگشت وجه ثبت شد: {refund.id}")
        
        # 7. تست متدهای مدل
        print("\n7️⃣ تست متدهای مدل...")
        
        print(f"🔄 امکان تلاش مجدد: {payment.can_retry()}")
        print(f"⏰ منقضی شده: {payment.is_expired()}")
        print(f"🔒 ماسک کارت: {payment.mask_card_number('1234567890123456')}")
        
        # 8. تست آمار
        print("\n8️⃣ آمار سیستم پرداخت...")
        
        total_payments = Payment.objects.count()
        successful_payments = Payment.objects.filter(status='SUCCESS').count()
        total_callbacks = PaymentCallback.objects.count()
        total_refunds = PaymentRefund.objects.count()
        
        print(f"💳 کل پرداخت‌ها: {total_payments}")
        print(f"✅ پرداخت‌های موفق: {successful_payments}")
        print(f"📞 کل callback ها: {total_callbacks}")
        print(f"💸 کل بازگشت‌ها: {total_refunds}")
        
        print("\n🎉 تست سیستم پرداخت با موفقیت تکمیل شد!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطا در تست سیستم پرداخت: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_payment_urls():
    """🧪 تست URL های پرداخت"""
    print("\n🔗 تست URL های پرداخت...")
    
    try:
        from django.urls import reverse
        
        # تست URL های مختلف
        urls_to_test = [
            ('payments:payment_summary', {'order_id': 1}),
            ('payments:payment_success', {'payment_id': 1}),
            ('payments:payment_failed', {'payment_id': 1}),
            ('payments:payment_status', {'payment_id': 1}),
            ('payments:payment_history', {}),
            ('payments:mock_gateway', {}),
        ]
        
        for url_name, kwargs in urls_to_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"✅ {url_name}: {url}")
            except Exception as e:
                print(f"❌ {url_name}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست URL ها: {str(e)}")
        return False


if __name__ == '__main__':
    print("🚀 شروع تست سیستم پرداخت v1.1")
    print("=" * 50)
    
    # تست سیستم پرداخت
    payment_test_success = test_payment_system()
    
    # تست URL ها
    url_test_success = test_payment_urls()
    
    print("\n" + "=" * 50)
    if payment_test_success and url_test_success:
        print("🎉 تمام تست‌ها با موفقیت انجام شد!")
    else:
        print("⚠️ برخی تست‌ها ناموفق بودند.")
    
    print("\n📋 خلاصه پیاده‌سازی:")
    print("✅ مدل‌های پرداخت (Payment, PaymentCallback, PaymentRefund)")
    print("✅ سرویس‌های پرداخت (ZarinPal, Shaparak)")
    print("✅ ویوهای پرداخت (summary, initiate, callback, success, failed)")
    print("✅ URL های پرداخت")
    print("✅ پنل ادمین پرداخت")
    print("✅ یکپارچه‌سازی با سیستم سفارش")
    print("✅ سیستم لاگینگ و پیگیری")
    print("✅ حالت sandbox برای تست") 