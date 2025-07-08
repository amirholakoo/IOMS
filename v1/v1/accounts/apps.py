"""
🔧 تنظیمات اپلیکیشن accounts - HomayOMS
👥 اپلیکیشن مدیریت کاربران، نقش‌ها و مجوزها
🔐 سیستم پیشرفته کنترل دسترسی
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    ⚙️ کلاس تنظیمات اپلیکیشن accounts
    
    🎯 شامل تنظیمات اصلی اپلیکیشن مدیریت کاربران
    🔐 مدیریت نقش‌ها: Super Admin، Admin، Finance
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = "👥 مدیریت حساب‌های کاربری"
    
    def ready(self):
        """
        🚀 اجرای کدهای آماده‌سازی هنگام بارگذاری اپلیکیشن
        
        ⚡ این متد هنگام شروع Django اجرا می‌شود
        🔧 برای تنظیمات اولیه و ثبت سیگنال‌ها استفاده می‌شود
        """
        try:
            # 📡 وارد کردن سیگنال‌های اپلیکیشن (در آینده)
            # import accounts.signals
            pass
        except ImportError:
            # 🚫 در صورت عدم وجود ماژول signals
            pass
