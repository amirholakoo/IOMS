from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        🔔 ثبت سیگنال‌ها هنگام راه‌اندازی اپلیکیشن
        ⏰ این متد هنگام بارگذاری اپلیکیشن اجرا می‌شود
        """
        import core.signals  # noqa
