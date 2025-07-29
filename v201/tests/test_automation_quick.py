#!/usr/bin/env python3
"""
🧪 تست سریع سیستم خودکار لغو سفارشات
⏰ این اسکریپت برای تست سریع سیستم بدون نیاز به Django shell
🔧 شامل بررسی تنظیمات و تست توابع
"""

import os
import sys
import django
from datetime import timedelta

# 📁 اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 🔧 تنظیم محیط Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.dev')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.conf import settings
from django.utils import timezone
from core.models import Order, ActivityLog
from core.signals import (
    cancel_expired_processing_orders, 
    is_automation_running,
    start_automated_cancellation,
    set_automation_interval
)

def test_automation_system():
    """🧪 تست کامل سیستم خودکار"""
    print("\n🚀 شروع تست سیستم خودکار لغو سفارشات")
    print("=" * 50)
    
    # 📊 بررسی تنظیمات
    timeout = getattr(settings, 'ORDER_CANCELLATION_TIMEOUT', 5)
    print(f"⏰ زمان انقضا تنظیم شده: {timeout} دقیقه")
    
    # 🔍 بررسی سفارشات Processing
    processing_orders = Order.objects.filter(status='Processing')
    print(f"📦 تعداد سفارشات Processing موجود: {processing_orders.count()}")
    
    if processing_orders.exists():
        print("\n📋 لیست سفارشات Processing:")
        for order in processing_orders:
            time_in_processing = timezone.now() - order.updated_at
            minutes_in_processing = int(time_in_processing.total_seconds() / 60)
            print(f"  - {order.order_number}: {minutes_in_processing} دقیقه در Processing")
            print(f"    آخرین بروزرسانی: {order.updated_at}")
    
    # 🤖 بررسی وضعیت سیستم خودکار
    automation_status = is_automation_running()
    print(f"\n🤖 وضعیت سیستم خودکار: {'در حال اجرا' if automation_status else 'متوقف'}")
    
    # 🧪 تست تابع لغو خودکار
    print(f"\n🧪 اجرای تابع لغو خودکار...")
    cancelled_count = cancel_expired_processing_orders()
    print(f"✅ {cancelled_count} سفارش لغو شد")
    
    # 📊 آمار نهایی
    final_processing = Order.objects.filter(status='Processing').count()
    final_cancelled = Order.objects.filter(status='Cancelled').count()
    
    print(f"\n📊 آمار نهایی:")
    print(f"  🔄 Processing: {final_processing}")
    print(f"  ❌ Cancelled: {final_cancelled}")
    
    # 📝 لاگ‌های اخیر
    recent_logs = ActivityLog.objects.filter(
        action__in=['CANCEL', 'UPDATE']
    ).order_by('-created_at')[:3]
    
    if recent_logs.exists():
        print(f"\n📝 آخرین لاگ‌های مرتبط:")
        for log in recent_logs:
            print(f"  - {log.created_at.strftime('%H:%M:%S')}: {log.description}")
    
    return cancelled_count

def test_automation_control():
    """🔧 تست کنترل سیستم خودکار"""
    print("\n🔧 تست کنترل سیستم خودکار")
    print("=" * 30)
    
    # 🚀 شروع سیستم خودکار
    print("🚀 شروع سیستم خودکار...")
    thread = start_automated_cancellation()
    print(f"✅ Thread ID: {thread.ident if thread else 'None'}")
    
    # ⏰ تنظیم فاصله بررسی کوتاه
    print("⏰ تنظیم فاصله بررسی به 30 ثانیه...")
    set_automation_interval(30)
    
    # 🔍 بررسی وضعیت
    status = is_automation_running()
    print(f"🤖 وضعیت: {'در حال اجرا' if status else 'متوقف'}")
    
    return status

def create_test_processing_order():
    """🧪 ایجاد سفارش Processing تست"""
    print("\n🔧 ایجاد سفارش Processing تست")
    print("=" * 35)
    
    try:
        # پیدا کردن مشتری
        customer = Customer.objects.first()
        if not customer:
            print("❌ هیچ مشتری یافت نشد")
            return None
        
        # ایجاد سفارش Processing قدیمی (برای تست)
        old_time = timezone.now() - timedelta(minutes=2)  # 2 دقیقه قبل
        
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
    print("🧪 تست سریع سیستم خودکار لغو سفارشات - HomayOMS")
    print("=" * 60)
    
    try:
        # 🧪 تست کنترل سیستم
        test_automation_control()
        
        # 🧪 تست سیستم
        cancelled_count = test_automation_system()
        
        print(f"\n🎉 تست کامل شد!")
        print(f"📊 نتیجه: {cancelled_count} سفارش لغو شد")
        
        if cancelled_count > 0:
            print("✅ سیستم خودکار کار می‌کند!")
        else:
            print("⚠️ هیچ سفارش منقضی‌ای یافت نشد")
            print("💡 برای تست بهتر، یک سفارش Processing قدیمی ایجاد کنید")
        
    except Exception as e:
        print(f"❌ خطا در تست: {str(e)}")
        import traceback
        traceback.print_exc() 