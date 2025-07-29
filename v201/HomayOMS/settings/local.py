"""
🏠 تنظیمات محیط محلی توسعه - HomayOMS
🎯 این فایل برای توسعه محلی طراحی شده است
🗄️ از پایگاه داده SQLite استفاده می‌کند و حالت دیباگ فعال است
"""

from .base import *
from decouple import config
import os

# 🐛 فعال‌سازی حالت دیباگ برای توسعه محلی
DEBUG = True

# 🗄️ پایگاه داده برای توسعه محلی (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 🔧 موتور SQLite
        'NAME': BASE_DIR / 'db.sqlite3',         # 📁 مسیر فایل پایگاه داده
    }
}

# 🌐 هاست‌های مجاز اضافی برای توسعه محلی
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# 📧 تنظیمات ایمیل برای توسعه محلی (خروجی کنسول)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 📊 تنظیمات لاگ‌گیری برای توسعه محلی
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',  # خروجی به کنسول
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # سطح اطلاعات
        },
    },
}

# 🔗 تنظیمات CORS برای توسعه محلی (اجازه کلی)
CORS_ALLOW_ALL_ORIGINS = True

# 📱 تنظیمات SMS برای توسعه محلی
SMS_SERVER_URL = config('SMS_SERVER_URL', default='http://localhost:5003')
SMS_API_KEY = config('SMS_API_KEY', default='ioms_sms_server_2025')
SMS_TIMEOUT = config('SMS_TIMEOUT', default=30, cast=int)
SMS_RETRY_ATTEMPTS = config('SMS_RETRY_ATTEMPTS', default=3, cast=int)
SMS_FALLBACK_TO_FAKE = config('SMS_FALLBACK_TO_FAKE', default=True, cast=bool)

# 📊 تنظیمات لاگ‌گیری و مانیتورینگ
LOG_LEVEL = config('LOG_LEVEL', default='DEBUG')
LOG_FILE_PATH = config('LOG_FILE_PATH', default=os.path.join(BASE_DIR, 'logs'))
ENABLE_HEALTH_CHECKS = config('ENABLE_HEALTH_CHECKS', default=True, cast=bool)
ENABLE_METRICS = config('ENABLE_METRICS', default=True, cast=bool) 