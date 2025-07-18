"""
🔔 سیگنال‌های Django برای اپلیکیشن Core - HomayOMS
⏰ این فایل شامل سیگنال‌های خودکار برای مدیریت سفارشات است
🔄 شامل لغو خودکار سفارشات Processing پس از گذشت زمان مشخص
🤖 سیستم کاملاً خودکار بدون نیاز به cron jobs
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging
import threading
import time
from .models import Order, ActivityLog

# 📝 تنظیم لاگر
logger = logging.getLogger(__name__)

# 🔄 متغیرهای کنترل خودکار
_automation_thread = None
_automation_running = False
_automation_interval = 60  # بررسی هر 60 ثانیه


def start_automated_cancellation():
    """
    🤖 شروع سیستم خودکار لغو سفارشات
    
    🎯 این تابع یک thread جداگانه ایجاد می‌کند که به صورت مداوم
    سفارشات منقضی شده را بررسی و لغو می‌کند
    
    🔧 استفاده:
        start_automated_cancellation()
    
    📊 خروجی:
        - Thread ID برای کنترل
        - وضعیت اجرا
    """
    global _automation_thread, _automation_running
    
    if _automation_running:
        logger.info("🤖 سیستم خودکار قبلاً در حال اجرا است")
        return _automation_thread
    
    _automation_running = True
    
    def automation_worker():
        """🔧 کارگر خودکار - بررسی مداوم سفارشات"""
        logger.info("🤖 سیستم خودکار لغو سفارشات شروع شد")
        
        while _automation_running:
            try:
                # 🔍 بررسی سفارشات منقضی شده
                cancelled_count = cancel_expired_processing_orders()
                
                if cancelled_count > 0:
                    logger.info(f"🤖 {cancelled_count} سفارش به صورت خودکار لغو شد")
                
                # ⏰ انتظار تا بررسی بعدی
                time.sleep(_automation_interval)
                
            except Exception as e:
                logger.error(f"❌ خطا در سیستم خودکار: {str(e)}")
                time.sleep(_automation_interval)
    
    # 🧵 ایجاد thread جدید
    _automation_thread = threading.Thread(target=automation_worker, daemon=True)
    _automation_thread.start()
    
    logger.info(f"🤖 سیستم خودکار شروع شد - Thread ID: {_automation_thread.ident}")
    return _automation_thread


def stop_automated_cancellation():
    """
    🛑 توقف سیستم خودکار لغو سفارشات
    
    🎯 این تابع سیستم خودکار را متوقف می‌کند
    
    🔧 استفاده:
        stop_automated_cancellation()
    
    📊 خروجی:
        - وضعیت توقف
    """
    global _automation_running
    
    if not _automation_running:
        logger.info("🤖 سیستم خودکار در حال اجرا نیست")
        return False
    
    _automation_running = False
    logger.info("🤖 سیستم خودکار متوقف شد")
    return True


def is_automation_running():
    """
    🔍 بررسی وضعیت سیستم خودکار
    
    🎯 این تابع وضعیت اجرای سیستم خودکار را برمی‌گرداند
    
    🔧 استفاده:
        is_automation_running()
    
    📊 خروجی:
        - True/False
    """
    global _automation_running
    return _automation_running


def set_automation_interval(seconds):
    """
    ⏰ تنظیم فاصله زمانی بررسی خودکار
    
    🎯 این تابع فاصله زمانی بررسی سفارشات را تنظیم می‌کند
    
    🔧 استفاده:
        set_automation_interval(30)  # هر 30 ثانیه
    
    📊 خروجی:
        - فاصله زمانی جدید
    """
    global _automation_interval
    _automation_interval = max(10, seconds)  # حداقل 10 ثانیه
    logger.info(f"⏰ فاصله بررسی خودکار به {_automation_interval} ثانیه تغییر کرد")
    return _automation_interval


def cancel_expired_processing_orders():
    """
    🚫 لغو خودکار سفارشات Processing که بیش از زمان تعیین شده در حالت Processing مانده‌اند
    
    🎯 این تابع:
    - سفارشات با وضعیت 'Processing' را پیدا می‌کند
    - آن‌هایی که بیش از ORDER_CANCELLATION_TIMEOUT دقیقه در این وضعیت مانده‌اند را لغو می‌کند
    - محصولات مربوطه را آزاد می‌کند
    - لاگ فعالیت ایجاد می‌کند
    
    🔧 استفاده:
        cancel_expired_processing_orders()
    
    📊 خروجی:
        - تعداد سفارشات لغو شده
        - لاگ‌های فعالیت برای هر سفارش لغو شده
    """
    try:
        # ⏰ محاسبه زمان انقضا
        timeout_minutes = getattr(settings, 'ORDER_CANCELLATION_TIMEOUT', 5)
        expiration_time = timezone.now() - timedelta(minutes=timeout_minutes)
        
        # 🔍 پیدا کردن سفارشات Processing منقضی شده
        expired_orders = Order.objects.filter(
            status='Processing',
            updated_at__lt=expiration_time
        )
        
        cancelled_count = 0
        
        for order in expired_orders:
            try:
                # 📝 لاگ قبل از لغو
                logger.info(f"🔄 لغو خودکار سفارش {order.order_number} - منقضی شده پس از {timeout_minutes} دقیقه")
                
                # 🚫 تغییر وضعیت به لغو شده
                old_status = order.status
                order.status = 'Cancelled'
                order.notes = f"لغو خودکار پس از {timeout_minutes} دقیقه عدم پردازش - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
                order.save()
                
                # 📦 آزاد کردن محصولات
                for order_item in order.order_items.all():
                    product = order_item.product
                    if product.status == 'Pre-order':
                        product.status = 'In-stock'
                        product.save()
                        
                        # 📝 لاگ آزادسازی محصول
                        ActivityLog.log_activity(
                            user=None,  # سیستم
                            action='UPDATE',
                            description=f'محصول {product.reel_number} آزاد شد پس از لغو خودکار سفارش {order.order_number}',
                            content_object=product,
                            severity='MEDIUM',
                            extra_data={
                                'order_number': order.order_number,
                                'cancellation_reason': 'timeout',
                                'timeout_minutes': timeout_minutes,
                                'automated': True
                            }
                        )
                
                # 📝 لاگ لغو سفارش
                ActivityLog.log_activity(
                    user=None,  # سیستم
                    action='CANCEL',
                    description=f'سفارش {order.order_number} به صورت خودکار لغو شد پس از {timeout_minutes} دقیقه',
                    content_object=order,
                    severity='HIGH',
                    extra_data={
                        'old_status': old_status,
                        'new_status': 'Cancelled',
                        'cancellation_reason': 'timeout',
                        'timeout_minutes': timeout_minutes,
                        'expiration_time': expiration_time.isoformat(),
                        'automated': True
                    }
                )
                
                cancelled_count += 1
                
            except Exception as e:
                logger.error(f"❌ خطا در لغو سفارش {order.order_number}: {str(e)}")
                continue
        
        if cancelled_count > 0:
            logger.info(f"✅ {cancelled_count} سفارش Processing به صورت خودکار لغو شد")
        
        return cancelled_count
        
    except Exception as e:
        logger.error(f"❌ خطا در تابع لغو خودکار سفارشات: {str(e)}")
        return 0


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    """
    🔔 سیگنال تغییر وضعیت سفارش
    
    🎯 این سیگنال:
    - هنگام تغییر وضعیت سفارش اجرا می‌شود
    - اگر وضعیت به 'Processing' تغییر کند، زمان را ثبت می‌کند
    - برای پیگیری زمان‌بندی لغو خودکار استفاده می‌شود
    - سیستم خودکار را شروع می‌کند اگر در حال اجرا نباشد
    
    📝 لاگ تغییر وضعیت را ایجاد می‌کند
    """
    if not created:  # فقط برای تغییرات، نه ایجاد جدید
        try:
            # 🔍 بررسی تغییر وضعیت
            if hasattr(instance, '_state') and hasattr(instance._state, 'fields_cache'):
                old_status = instance._state.fields_cache.get('status')
                if old_status and old_status != instance.status:
                    # 📝 لاگ تغییر وضعیت
                    ActivityLog.log_activity(
                        user=None,  # سیستم
                        action='UPDATE',
                        description=f'وضعیت سفارش {instance.order_number} از {old_status} به {instance.status} تغییر کرد',
                        content_object=instance,
                        severity='MEDIUM',
                        extra_data={
                            'old_status': old_status,
                            'new_status': instance.status,
                            'change_time': timezone.now().isoformat(),
                            'automated': True
                        }
                    )
                    
                    # ⏰ اگر وضعیت به Processing تغییر کرد، زمان را ثبت کن
                    if instance.status == 'Processing':
                        logger.info(f"⏰ سفارش {instance.order_number} وارد وضعیت Processing شد - زمان شروع: {timezone.now()}")
                        
                        # 🤖 شروع سیستم خودکار اگر در حال اجرا نیست
                        if not is_automation_running():
                            start_automated_cancellation()
                        
        except Exception as e:
            logger.error(f"❌ خطا در سیگنال تغییر وضعیت سفارش: {str(e)}")


def schedule_order_cancellation_check():
    """
    ⏰ برنامه‌ریزی بررسی لغو خودکار سفارشات
    
    🎯 این تابع برای برنامه‌ریزی اجرای دوره‌ای تابع لغو خودکار استفاده می‌شود
    حالا به صورت خودکار توسط thread جداگانه اجرا می‌شود
    
    🔧 استفاده:
        schedule_order_cancellation_check()
    
    📊 خروجی:
        - نتیجه اجرای تابع لغو خودکار
    """
    try:
        logger.info("⏰ شروع بررسی لغو خودکار سفارشات...")
        cancelled_count = cancel_expired_processing_orders()
        
        if cancelled_count > 0:
            logger.info(f"✅ بررسی کامل شد - {cancelled_count} سفارش لغو شد")
        else:
            logger.info("✅ بررسی کامل شد - هیچ سفارشی برای لغو یافت نشد")
            
        return cancelled_count
        
    except Exception as e:
        logger.error(f"❌ خطا در برنامه‌ریزی بررسی لغو سفارشات: {str(e)}")
        return 0


# 🤖 شروع خودکار سیستم هنگام بارگذاری ماژول
def initialize_automation():
    """
    🤖 راه‌اندازی اولیه سیستم خودکار
    
    🎯 این تابع هنگام بارگذاری ماژول اجرا می‌شود
    سیستم خودکار را شروع می‌کند
    """
    try:
        # 🔍 بررسی وجود سفارشات Processing
        processing_orders = Order.objects.filter(status='Processing').count()
        
        if processing_orders > 0:
            logger.info(f"🤖 {processing_orders} سفارش Processing یافت شد - شروع سیستم خودکار")
            start_automated_cancellation()
        else:
            logger.info("🤖 هیچ سفارش Processing یافت نشد - سیستم خودکار آماده است")
            
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی سیستم خودکار: {str(e)}")


# 🚀 راه‌اندازی خودکار
initialize_automation() 