"""
🔧 تنظیمات محیط توسعه/آزمایش - HomayOMS
🚀 این فایل برای سرور آزمایش و توسعه طراحی شده است
📊 مشابه محیط محلی اما قابل تنظیم برای سرور staging
"""

from .base import *
from decouple import config
import os

# 🐛 فعال‌سازی حالت دیباگ برای توسعه
DEBUG = True

# 🗄️ پایگاه داده برای توسعه (SQLite - قابل تغییر به PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 🔧 موتور SQLite
        'NAME': BASE_DIR / 'db_dev.sqlite3',     # 📁 فایل جداگانه برای dev
    }
}

# 🌐 هاست‌های مجاز برای سرور توسعه
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'dev.homayoms.local']

# 📧 تنظیمات ایمیل برای توسعه
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 📊 تنظیمات لاگ‌گیری برای توسعه
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_dev.log',  # 📁 ذخیره در فایل
        },
        'console': {
            'class': 'logging.StreamHandler',  # 📺 خروجی کنسول
        },
    },
    'root': {
        'handlers': ['console', 'file'],  # هر دو خروجی
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',  # 🔍 سطح جزئیات کامل
        },
    },
}

# 🔗 تنظیمات CORS برای توسعه
CORS_ALLOW_ALL_ORIGINS = True

# 🔧 تنظیمات اضافی توسعه
INTERNAL_IPS = ['127.0.0.1']  # آی‌پی‌های داخلی

# 📱 تنظیمات SMS برای توسعه
SMS_SERVER_URL = config('SMS_SERVER_URL', default='http://192.168.1.60:5003')
SMS_API_KEY = config('SMS_API_KEY', default='ioms_sms_server_2025')
SMS_TIMEOUT = config('SMS_TIMEOUT', default=30, cast=int)
SMS_RETRY_ATTEMPTS = config('SMS_RETRY_ATTEMPTS', default=3, cast=int)
SMS_FALLBACK_TO_FAKE = config('SMS_FALLBACK_TO_FAKE', default=True, cast=bool)

# 📊 تنظیمات لاگ‌گیری و مانیتورینگ
LOG_LEVEL = config('LOG_LEVEL', default='INFO')
LOG_FILE_PATH = config('LOG_FILE_PATH', default=os.path.join(BASE_DIR, 'logs'))
ENABLE_HEALTH_CHECKS = config('ENABLE_HEALTH_CHECKS', default=True, cast=bool)
ENABLE_METRICS = config('ENABLE_METRICS', default=True, cast=bool) 