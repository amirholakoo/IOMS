#!/usr/bin/env python
"""
🧪 تست درگاه‌های پرداخت - بررسی رفع مشکلات
"""

import os
import sys
import django
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from payments.services import ZarinPalGateway, ShaparakGateway
from core.models import Order, Customer, Product, OrderItem
from accounts.models import User
from payments.models import Payment
import uuid


def test_zarinpal_authority():
    """تست تولید authority صحیح برای زرین‌پال"""
    print("🧪 تست تولید Authority زرین‌پال...")
    
    gateway = ZarinPalGateway(sandbox=True)
    
    # تست تولید authority در mock response
    mock_response = gateway._get_mock_response(
        'https://sandbox.zarinpal.com/pg/v4/payment/request.json',
        {'amount': 100000},
        'POST'
    )
    
    authority = mock_response['data']['authority']
    print(f"   Authority تولید شده: {authority}")
    print(f"   طول Authority: {len(authority)}")
    
    if len(authority) == 36:
        print("   ✅ Authority صحیح است (36 کاراکتر)")
        return True
    else:
        print(f"   ❌ Authority نادرست است (انتظار 36، دریافت {len(authority)})")
        return False


def test_shaparak_token():
    """تست تولید token صحیح برای شاپرک"""
    print("🧪 تست تولید Token شاپرک...")
    
    gateway = ShaparakGateway(sandbox=True)
    
    # تست تولید token در mock response
    mock_response = gateway._get_mock_response(
        'https://sandbox.shaparak.ir/api/v1/payment/request',
        {'amount': 100000, 'order_id': 'TEST123'},
        'POST'
    )
    
    token = mock_response['data']['token']
    print(f"   Token تولید شده: {token}")
    print(f"   طول Token: {len(token)}")
    
    if len(token) == 32:
        print("   ✅ Token صحیح است (32 کاراکتر)")
        return True
    else:
        print(f"   ❌ Token نادرست است (انتظار 32، دریافت {len(token)})")
        return False


def test_payment_creation():
    """تست ایجاد پرداخت و تولید authority/token"""
    print("🧪 تست ایجاد پرداخت...")
    
    try:
        # ایجاد مشتری تست
        test_phone = f"09{random.randint(100000000, 999999999)}"
        customer = Customer.objects.create(
            customer_name="مشتری تست",
            phone=test_phone,
            status='Active'
        )
        
        # ایجاد محصول تست
        product = Product.objects.create(
            reel_number=f"R{random.randint(10000, 99999)}",
            location="Anbar_Akhal",
            width=100,
            gsm=80,
            length=1000,
            grade="A",
            price=Decimal('10000'),
            status="In-stock"
        )
        
        # ایجاد سفارش تست
        order = Order.objects.create(
            customer=customer,
            order_number=f"TEST-{uuid.uuid4().hex[:8]}",
            status='Pending'
        )
        
        # ایجاد آیتم سفارش
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price=Decimal('10000'),
            total_price=Decimal('10000'),
            payment_method='Cash'
        )
        
        # ایجاد پرداخت زرین‌پال
        zarinpal_payment = Payment.objects.create(
            order=order,
            amount=100000,  # 10000 تومان = 100000 ریال
            gateway='zarinpal',
            description='پرداخت تست زرین‌پال',
            tracking_code=f"ZP-{uuid.uuid4().hex[:8]}"
        )
        
        # تست ایجاد پرداخت زرین‌پال
        zarinpal_gateway = ZarinPalGateway(sandbox=True)
        callback_url = "http://localhost:8000/payments/callback/1/"
        
        result = zarinpal_gateway.create_payment(zarinpal_payment, callback_url)
        
        if result.get('success'):
            authority = result.get('authority')
            print(f"   ✅ پرداخت زرین‌پال ایجاد شد")
            print(f"   Authority: {authority}")
            print(f"   طول Authority: {len(authority) if authority else 0}")
            
            if authority and len(authority) == 36:
                print("   ✅ Authority صحیح است")
            else:
                print("   ❌ Authority نادرست است")
        else:
            print(f"   ❌ خطا در ایجاد پرداخت زرین‌پال: {result.get('error')}")
        
        # ایجاد پرداخت شاپرک
        shaparak_payment = Payment.objects.create(
            order=order,
            amount=100000,  # 10000 تومان = 100000 ریال
            gateway='shaparak',
            description='پرداخت تست شاپرک',
            tracking_code=f"SP-{uuid.uuid4().hex[:8]}"
        )
        
        # تست ایجاد پرداخت شاپرک
        shaparak_gateway = ShaparakGateway(sandbox=True)
        
        result = shaparak_gateway.create_payment(shaparak_payment, callback_url)
        
        if result.get('success'):
            token = result.get('token')
            print(f"   ✅ پرداخت شاپرک ایجاد شد")
            print(f"   Token: {token}")
            print(f"   طول Token: {len(token) if token else 0}")
            
            if token and len(token) == 32:
                print("   ✅ Token صحیح است")
            else:
                print("   ❌ Token نادرست است")
        else:
            print(f"   ❌ خطا در ایجاد پرداخت شاپرک: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطا در تست ایجاد پرداخت: {e}")
        return False


def main():
    """تابع اصلی تست"""
    print("🚀 شروع تست درگاه‌های پرداخت")
    print("=" * 50)
    
    # تست تولید authority زرین‌پال
    zarinpal_ok = test_zarinpal_authority()
    print()
    
    # تست تولید token شاپرک
    shaparak_ok = test_shaparak_token()
    print()
    
    # تست ایجاد پرداخت
    payment_ok = test_payment_creation()
    print()
    
    # نتیجه نهایی
    print("=" * 50)
    print("📊 نتیجه نهایی:")
    print(f"   زرین‌پال: {'✅ موفق' if zarinpal_ok else '❌ ناموفق'}")
    print(f"   شاپرک: {'✅ موفق' if shaparak_ok else '❌ ناموفق'}")
    print(f"   ایجاد پرداخت: {'✅ موفق' if payment_ok else '❌ ناموفق'}")
    
    if zarinpal_ok and shaparak_ok and payment_ok:
        print("\n🎉 تمام تست‌ها موفق بودند!")
        return True
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 