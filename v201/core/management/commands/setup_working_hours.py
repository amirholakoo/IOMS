"""
⏰ Management Command برای راه‌اندازی تنظیمات ساعات کاری
🔧 ایجاد تنظیمات پیش‌فرض ساعات کاری برای محیط Docker
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import WorkingHours


class Command(BaseCommand):
    help = 'راه‌اندازی تنظیمات ساعات کاری پیش‌فرض'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('⏰ شروع راه‌اندازی تنظیمات ساعات کاری...')
        )

        # بررسی وجود تنظیمات قبلی
        if WorkingHours.objects.exists():
            self.stdout.write(
                self.style.WARNING('⚠️ تنظیمات ساعات کاری قبلاً وجود دارد. به‌روزرسانی...')
            )
            working_hours = WorkingHours.objects.first()
        else:
            self.stdout.write('🆕 ایجاد تنظیمات جدید ساعات کاری...')
            working_hours = WorkingHours()

        # تنظیمات پیش‌فرض
        working_hours.opening_time = '08:00'
        working_hours.closing_time = '18:00'
        working_hours.is_thursday_open = True
        working_hours.thursday_closing_time = '16:00'
        working_hours.is_holiday = False
        working_hours.holiday_help_text = 'متأسفانه امروز تعطیل رسمی است. لطفاً در روز کاری مراجعه فرمایید.'
        working_hours.max_selection_limit = 6  # محدودیت پیش‌فرض انتخاب محصولات
        
        # تنظیم روزهای کاری
        working_hours.monday_open = True
        working_hours.tuesday_open = True
        working_hours.wednesday_open = True
        working_hours.thursday_open = True
        working_hours.friday_open = False  # جمعه تعطیل
        working_hours.saturday_open = True
        working_hours.sunday_open = True

        working_hours.save()

        self.stdout.write(
            self.style.SUCCESS('✅ تنظیمات ساعات کاری با موفقیت راه‌اندازی شد!')
        )
        
        self.stdout.write('📋 خلاصه تنظیمات:')
        self.stdout.write(f'   🕐 ساعت کاری: {working_hours.opening_time} - {working_hours.closing_time}')
        self.stdout.write(f'   📅 پنج‌شنبه: {"باز" if working_hours.is_thursday_open else "بسته"} ({working_hours.thursday_closing_time})')
        self.stdout.write(f'   🔢 محدودیت انتخاب: {working_hours.max_selection_limit} محصول')
        self.stdout.write(f'   📅 جمعه: {"باز" if working_hours.friday_open else "تعطیل"}')
        
        if working_hours.is_holiday:
            self.stdout.write(f'   🚫 تعطیل رسمی: {working_hours.holiday_help_text}')
        else:
            self.stdout.write('   ✅ امروز روز کاری است') 