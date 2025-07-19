"""
🧪 تست سیستم لغو خودکار سفارشات
⏰ این اسکریپت برای تست عملکرد سیستم لغو خودکار سفارشات استفاده می‌شود
🔧 شامل تست توابع و نمایش نحوه استفاده
"""

import os
import sys
import django
from datetime import timedelta

# 📁 اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 🔧 تنظیم محیط Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')
django.setup()

from django.utils import timezone
from django.conf import settings
from core.models import Order, Customer, Product, ActivityLog
from core.signals import cancel_expired_processing_orders, schedule_order_cancellation_check


def test_order_cancellation_system():
    """
    🧪 تست کامل سیستم لغو خودکار سفارشات
    """
    print("🚀 شروع تست سیستم لغو خودکار سفارشات")
    print("=" * 50)
    
    # 📊 نمایش تنظیمات فعلی
    timeout = getattr(settings, 'ORDER_CANCELLATION_TIMEOUT', 5)
    print(f"⏰ زمان انقضا فعلی: {timeout} دقیقه")
    
    # 🔍 بررسی سفارشات Processing موجود
    processing_orders = Order.objects.filter(status='Processing')
    print(f"📦 تعداد سفارشات Processing موجود: {processing_orders.count()}")
    
    if processing_orders.exists():
        print("\n📋 لیست سفارشات Processing:")
        for order in processing_orders:
            time_in_processing = timezone.now() - order.updated_at
            minutes_in_processing = int(time_in_processing.total_seconds() / 60)
            print(f"  - {order.order_number}: {minutes_in_processing} دقیقه در Processing")
    
    # 🧪 تست تابع لغو خودکار
    print(f"\n🧪 اجرای تابع لغو خودکار...")
    cancelled_count = cancel_expired_processing_orders()
    print(f"✅ {cancelled_count} سفارش لغو شد")
    
    # 📊 نمایش آمار نهایی
    final_processing = Order.objects.filter(status='Processing').count()
    final_cancelled = Order.objects.filter(status='Cancelled').count()
    
    print(f"\n📊 آمار نهایی:")
    print(f"  🔄 Processing: {final_processing}")
    print(f"  ❌ Cancelled: {final_cancelled}")
    
    # 📝 نمایش لاگ‌های اخیر
    recent_logs = ActivityLog.objects.filter(
        action__in=['CANCEL', 'UPDATE']
    ).order_by('-created_at')[:5]
    
    if recent_logs.exists():
        print(f"\n📝 آخرین لاگ‌های مرتبط:")
        for log in recent_logs:
            print(f"  - {log.created_at.strftime('%H:%M:%S')}: {log.description}")
    
    print("\n✅ تست کامل شد!")


def test_manual_cancellation():
    """
    🧪 تست لغو دستی سفارشات
    """
    print("\n🔧 تست لغو دستی سفارشات")
    print("=" * 30)
    
    # 🧪 تست حالت dry-run
    print("🔍 تست حالت dry-run...")
    
    # شبیه‌سازی درخواست dry-run
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from core.views import manual_cancel_expired_orders_view
    import json
    
    User = get_user_model()
    
    # ایجاد درخواست تست
    factory = RequestFactory()
    request = factory.post(
        '/api/cancel-expired-orders/',
        data=json.dumps({'dry_run': True}),
        content_type='application/json'
    )
    
    # پیدا کردن یک Super Admin
    super_admin = User.objects.filter(role='Super Admin').first()
    if super_admin:
        request.user = super_admin
        
        # اجرای view
        response = manual_cancel_expired_orders_view(request)
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"✅ حالت dry-run: {data.get('message', '')}")
            if 'expired_orders' in data:
                print(f"📋 {len(data['expired_orders'])} سفارش منقضی شده یافت شد")
        else:
            print(f"❌ خطا در حالت dry-run: {response.status_code}")
    else:
        print("⚠️ هیچ Super Admin یافت نشد")


def create_test_processing_order():
    """
    🧪 ایجاد سفارش Processing تست برای آزمایش
    """
    print("\n🔧 ایجاد سفارش Processing تست")
    print("=" * 35)
    
    try:
        # پیدا کردن مشتری
        customer = Customer.objects.first()
        if not customer:
            print("❌ هیچ مشتری یافت نشد")
            return None
        
        # پیدا کردن محصول
        product = Product.objects.filter(status='In-stock').first()
        if not product:
            print("❌ هیچ محصول موجودی یافت نشد")
            return None
        
        # ایجاد سفارش Processing قدیمی (برای تست)
        old_time = timezone.now() - timedelta(minutes=10)  # 10 دقیقه قبل
        
        order = Order.objects.create(
            customer=customer,
            order_number=f"TEST-{timezone.now().strftime('%Y%m%d-%H%M%S')}",
            status='Processing',
            payment_method='Cash',
            total_amount=100000,
            final_amount=100000,
            notes='سفارش تست برای آزمایش لغو خودکار'
        )
        
        # تنظیم زمان بروزرسانی به گذشته
        order.updated_at = old_time
        order.save(update_fields=['updated_at'])
        
        print(f"✅ سفارش تست ایجاد شد: {order.order_number}")
        print(f"⏰ زمان بروزرسانی: {order.updated_at}")
        
        return order
        
    except Exception as e:
        print(f"❌ خطا در ایجاد سفارش تست: {str(e)}")
        return None


if __name__ == "__main__":
    print("🧪 تست سیستم لغو خودکار سفارشات - HomayOMS")
    print("=" * 60)
    
    # 🧪 ایجاد سفارش تست
    test_order = create_test_processing_order()
    
    # 🧪 تست سیستم
    test_order_cancellation_system()
    
    # 🧪 تست لغو دستی
    test_manual_cancellation()
    
    print("\n🎉 تمام تست‌ها کامل شد!")
    print("\n📋 نحوه استفاده:")
    print("1. تنظیم ORDER_CANCELLATION_TIMEOUT در settings")
    print("2. اجرای دستور: python manage.py cancel_expired_orders")
    print("3. یا فراخوانی API: POST /core/api/cancel-expired-orders/")
    print("4. یا استفاده از تابع: cancel_expired_processing_orders()") 