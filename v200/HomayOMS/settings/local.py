"""
🏠 تنظیمات محیط محلی توسعه - HomayOMS
🎯 این فایل برای توسعه محلی طراحی شده است
🗄️ از پایگاه داده SQLite استفاده می‌کند و حالت دیباگ فعال است
"""

from .base import *

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