"""
🚫 دستور مدیریت لغو خودکار سفارشات منقضی شده
⏰ این دستور برای اجرای دستی تابع لغو خودکار سفارشات استفاده می‌شود
🔧 می‌تواند برای تست یا اجرای دستی استفاده شود
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from core.signals import cancel_expired_processing_orders, schedule_order_cancellation_check
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'لغو خودکار سفارشات Processing که بیش از زمان تعیین شده در این وضعیت مانده‌اند'
    
    def add_arguments(self, parser):
        """
        🔧 اضافه کردن پارامترهای اختیاری به دستور
        """
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش سفارشات بدون لغو کردن آن‌ها (تست)',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            help='زمان انقضا به دقیقه (پیش‌فرض: از تنظیمات)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='نمایش جزئیات بیشتر',
        )
    
    def handle(self, *args, **options):
        """
        🎯 اجرای اصلی دستور
        """
        try:
            # 📊 نمایش اطلاعات شروع
            timeout = options.get('timeout') or getattr(settings, 'ORDER_CANCELLATION_TIMEOUT', 5)
            dry_run = options.get('dry_run', False)
            verbose = options.get('verbose', False)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"🚀 شروع بررسی لغو خودکار سفارشات..."
                )
            )
            
            if verbose:
                self.stdout.write(f"⏰ زمان انقضا: {timeout} دقیقه")
                self.stdout.write(f"🔍 حالت تست: {'بله' if dry_run else 'خیر'}")
            
            if dry_run:
                # 🔍 حالت تست - فقط نمایش سفارشات
                from django.utils import timezone
                from datetime import timedelta
                from core.models import Order
                
                expiration_time = timezone.now() - timedelta(minutes=timeout)
                expired_orders = Order.objects.filter(
                    status='Processing',
                    updated_at__lt=expiration_time
                )
                
                self.stdout.write(
                    self.style.WARNING(
                        f"🔍 {expired_orders.count()} سفارش Processing منقضی شده یافت شد:"
                    )
                )
                
                for order in expired_orders:
                    time_in_processing = timezone.now() - order.updated_at
                    minutes_in_processing = int(time_in_processing.total_seconds() / 60)
                    
                    self.stdout.write(
                        f"  📦 سفارش {order.order_number}:"
                    )
                    self.stdout.write(
                        f"    👤 مشتری: {order.customer.customer_name}"
                    )
                    self.stdout.write(
                        f"    ⏰ زمان در Processing: {minutes_in_processing} دقیقه"
                    )
                    self.stdout.write(
                        f"    📅 آخرین بروزرسانی: {order.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    self.stdout.write(
                        f"    💰 مبلغ: {order.final_amount:,} تومان"
                    )
                    self.stdout.write("")
                
                if expired_orders.count() == 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "✅ هیچ سفارش Processing منقضی شده‌ای یافت نشد"
                        )
                    )
                
            else:
                # 🚫 اجرای واقعی لغو خودکار
                cancelled_count = schedule_order_cancellation_check()
                
                if cancelled_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {cancelled_count} سفارش Processing به صورت خودکار لغو شد"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "✅ هیچ سفارشی برای لغو یافت نشد"
                        )
                    )
            
            # 📊 نمایش آمار نهایی
            if verbose:
                from core.models import Order
                processing_count = Order.objects.filter(status='Processing').count()
                cancelled_count = Order.objects.filter(status='Cancelled').count()
                
                self.stdout.write("")
                self.stdout.write("📊 آمار سفارشات:")
                self.stdout.write(f"  🔄 Processing: {processing_count}")
                self.stdout.write(f"  ❌ Cancelled: {cancelled_count}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ خطا در اجرای دستور: {str(e)}"
                )
            )
            logger.error(f"❌ خطا در دستور لغو خودکار سفارشات: {str(e)}")
            raise 