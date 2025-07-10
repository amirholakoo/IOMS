"""
🏭 تنظیمات محیط تولید - HomayOMS
🔒 این فایل برای سرور تولید با حداکثر امنیت طراحی شده است
🗄️ از پایگاه داده PostgreSQL و تنظیمات امنیتی پیشرفته استفاده می‌کند
"""

from .base import *
import sys
import os
from decouple import config

# 📁 اضافه کردن مسیر اصلی پروژه به Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# 🔐 تنظیمات امنیتی تولید
DEBUG = config('DEBUG', default=False, cast=bool)  # ❌ غیرفعال کردن حالت دیباگ
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# 🗄️ پایگاه داده PostgreSQL برای تولید
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # 🐘 موتور PostgreSQL
        'NAME': config('DB_NAME', default='homayoms_db'),
        'USER': config('DB_USER', default='homayoms_user'),
        'PASSWORD': config('DB_PASSWORD', default='homayoms_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# 🛡️ تنظیمات امنیتی پیشرفته برای تولید
SECURE_BROWSER_XSS_FILTER = True          # 🚫 فیلتر XSS مرورگر
SECURE_CONTENT_TYPE_NOSNIFF = True        # 🚫 جلوگیری از Content-Type sniffing
SECURE_HSTS_SECONDS = 31536000            # ⏰ HSTS برای یک سال
SECURE_HSTS_INCLUDE_SUBDOMAINS = True     # 🌐 HSTS برای زیردامنه‌ها
SECURE_HSTS_PRELOAD = True                # 📋 HSTS preload
# SECURE_SSL_REDIRECT = True                # 🔀 هدایت به HTTPS (فقط در production واقعی)
SESSION_COOKIE_SECURE = False             # 🍪 کوکی نشست امن (False برای development)
CSRF_COOKIE_SECURE = False                # 🍪 کوکی CSRF امن (False برای development)
X_FRAME_OPTIONS = 'DENY'                 # 🚫 جلوگیری از iframe

# 📊 سیستم لاگ‌گیری تولید
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_production.log',
            'maxBytes': 1024*1024*5,  # 📏 حداکثر 5 مگابایت
            'backupCount': 10,        # 🗂️ نگه‌داری 10 فایل قبلی
            'formatter': 'verbose',   # 📝 فرمت کامل
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'maxBytes': 1024*1024*5,  # 📏 حداکثر 5 مگابایت
            'backupCount': 10,        # 🗂️ نگه‌داری 10 فایل قبلی
            'formatter': 'verbose',   # 📝 فرمت کامل
            'level': 'ERROR',         # ⚠️ فقط خطاها
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',          # 📋 سطح اطلاعات
            'propagate': False,
        },
    },
}

# 📧 تنظیمات ایمیل برای تولید (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# 🔗 تنظیمات CORS برای تولید (محدود)
CORS_ALLOW_ALL_ORIGINS = False            # ❌ جلوگیری از دسترسی کلی
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:8000,http://127.0.0.1:8000', cast=lambda v: [s.strip() for s in v.split(',')])

# 📝 تنظیمات نشست برای تولید
SESSION_COOKIE_AGE = 3600                 # ⏰ مدت اعتبار 1 ساعت
SESSION_EXPIRE_AT_BROWSER_CLOSE = True    # 🚪 انقضا هنگام بستن مرورگر

# 📁 تنظیمات فایل‌های استاتیک و رسانه
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles')
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media')

# 🔧 تنظیمات timezone
TIME_ZONE = config('TIME_ZONE', default='Asia/Tehran')
LANGUAGE_CODE = config('LANGUAGE_CODE', default='fa-ir') 