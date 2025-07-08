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

# 💳 تنظیمات درگاه‌های پرداخت ایرانی
PAYMENT_SANDBOX = config('PAYMENT_SANDBOX', default=True, cast=bool)  # 🧪 حالت sandbox
ZARINPAL_MERCHANT_ID = config('ZARINPAL_MERCHANT_ID', default='')     # 💎 کد پذیرنده زرین‌پال
SHAPARAK_TERMINAL_ID = config('SHAPARAK_TERMINAL_ID', default='')     # 🏦 شناسه ترمینال شاپرک
SHAPARAK_MERCHANT_ID = config('SHAPARAK_MERCHANT_ID', default='')     # 🏦 کد پذیرنده شاپرک 