from django.apps import AppConfig


class SmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sms'
    verbose_name = '📱 سیستم پیامک'
    
    def ready(self):
        """Initialize SMS app when Django starts"""
        try:
            # Import signals if they exist
            import sms.signals
        except ImportError:
            pass 