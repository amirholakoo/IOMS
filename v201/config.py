"""
🔧 فایل پیکربندی متغیرهای محیطی - HomayOMS
📋 این فایل مسئول مدیریت و واردات تمام متغیرهای محیطی از فایل .env است
🎯 هدف: ایجاد یک مرکز واحد برای مدیریت تنظیمات پروژه
"""

from decouple import config, Csv
import os

# 📁 مسیر اصلی پروژه
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔐 کلید امنیتی جنگو - باید همیشه مخفی نگه داشته شود
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key')

# 🐛 حالت دیباگ - در تولید باید False باشد
DEBUG = config('DEBUG', default=True, cast=bool)

# 🌐 هاست‌های مجاز - آدرس‌هایی که مجاز به دسترسی به سرور هستند
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver', cast=Csv())

# 🏷️ نوع سرور (local, dev, production) - برای انتخاب تنظیمات مناسب
SERVER_TYPE = config('TYPE', default='local')

# 🗄️ تنظیمات پایگاه داده PostgreSQL برای محیط تولید
DB_NAME = config('DB_NAME', default='homayoms_db')        # 📊 نام پایگاه داده
DB_USER = config('DB_USER', default='homayoms_user')      # 👤 نام کاربری پایگاه داده
DB_PASSWORD = config('DB_PASSWORD', default='password')   # 🔒 رمز عبور پایگاه داده
DB_HOST = config('DB_HOST', default='localhost')          # 🏠 آدرس سرور پایگاه داده
DB_PORT = config('DB_PORT', default='5432')               # 🚪 پورت پایگاه داده

# 🔗 تنظیمات CORS - برای دسترسی از دامنه‌های مختلف
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:8000', cast=Csv())

# 📁 تنظیمات فایل‌های استاتیک (CSS, JS, تصاویر)
STATIC_URL = '/static/'                                   # 🔗 آدرس URL فایل‌های استاتیک
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')      # 📂 مسیر ذخیره فایل‌های استاتیک تولید
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]    # 📂 مسیرهای جستجوی فایل‌های استاتیک

# 🖼️ تنظیمات فایل‌های رسانه‌ای (عکس، ویدیو، فایل)
MEDIA_URL = '/media/'                                     # 🔗 آدرس URL فایل‌های رسانه‌ای
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')             # 📂 مسیر ذخیره فایل‌های آپلود شده

# 📱 تنظیمات SMS Server
SMS_SERVER_URL = config('SMS_SERVER_URL', default='http://192.168.1.60:5003')  # 🔗 آدرس سرور SMS
SMS_API_KEY = config('SMS_API_KEY', default='ioms_sms_server_2025')            # 🔑 کلید API سرور SMS
SMS_TIMEOUT = config('SMS_TIMEOUT', default=30, cast=int)                      # ⏰ زمان انتظار برای SMS (ثانیه)
SMS_RETRY_ATTEMPTS = config('SMS_RETRY_ATTEMPTS', default=3, cast=int)         # 🔄 تعداد تلاش‌های مجدد SMS
SMS_FALLBACK_TO_FAKE = config('SMS_FALLBACK_TO_FAKE', default=True, cast=bool) # 🔄 استفاده از SMS فیک در صورت خطا

# 📊 تنظیمات لاگ‌گیری و مانیتورینگ
LOG_LEVEL = config('LOG_LEVEL', default='INFO')                               # 📋 سطح لاگ‌گیری
LOG_FILE_PATH = config('LOG_FILE_PATH', default=os.path.join(BASE_DIR, 'logs')) # 📂 مسیر فایل‌های لاگ
ENABLE_HEALTH_CHECKS = config('ENABLE_HEALTH_CHECKS', default=True, cast=bool)  # 🔍 فعال‌سازی بررسی سلامت
ENABLE_METRICS = config('ENABLE_METRICS', default=True, cast=bool)              # 📊 فعال‌سازی متریک‌ها 