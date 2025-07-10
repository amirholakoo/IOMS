"""
🏗️ تنظیمات پایه جنگو برای پروژه HomayOMS
📦 این فایل شامل تمام تنظیمات مشترک بین محیط‌های مختلف است
🔧 تنظیمات خاص هر محیط در فایل‌های جداگانه تعریف می‌شوند
"""

from pathlib import Path
import sys
import os

# 📁 اضافه کردن مسیر اصلی پروژه به Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 📥 واردات متغیرهای پیکربندی از config.py
from config import (
    SECRET_KEY, DEBUG, ALLOWED_HOSTS, 
    STATIC_URL, STATIC_ROOT, STATICFILES_DIRS,
    MEDIA_URL, MEDIA_ROOT, CORS_ALLOWED_ORIGINS,
    PAYMENT_SANDBOX, ZARINPAL_MERCHANT_ID, 
    SHAPARAK_TERMINAL_ID, SHAPARAK_MERCHANT_ID
)

# 📁 مسیر اصلی پروژه
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 🔐 تنظیمات امنیتی
SECRET_KEY = SECRET_KEY  # کلید امنیتی جنگو
DEBUG = DEBUG            # حالت دیباگ
ALLOWED_HOSTS = ALLOWED_HOSTS  # هاست‌های مجاز

# 📦 تعریف اپلیکیشن‌های نصب شده
INSTALLED_APPS = [
    # 🏠 اپلیکیشن‌های محلی پروژه (قبل از Django apps برای override کردن commands)
    'accounts',  # 👥 مدیریت کاربران و نقش‌ها - FIRST to override createsuperuser
    
    # 🎛️ اپلیکیشن‌های پیش‌فرض جنگو
    'django.contrib.admin',        # پنل مدیریت
    'django.contrib.auth',         # سیستم احراز هویت
    'django.contrib.contenttypes', # نوع محتوا
    'django.contrib.sessions',     # مدیریت نشست‌ها
    'django.contrib.messages',     # سیستم پیام‌ها
    'django.contrib.staticfiles',  # مدیریت فایل‌های استاتیک
    
    # 🔗 اپلیکیشن‌های شخص ثالث
    'corsheaders',  # مدیریت CORS
    
    # 🏠 اپلیکیشن‌های محلی پروژه (ادامه)
    'core',      # 🏢 اپلیکیشن اصلی کسب‌وکار
    'payments',  # 💳 سیستم پرداخت و درگاه‌های ایرانی
]

# 🔄 میدل‌ویرهای پردازش درخواست
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',           # 🔗 CORS middleware
    'django.middleware.security.SecurityMiddleware',   # 🔐 امنیت
    'django.contrib.sessions.middleware.SessionMiddleware',  # 📝 نشست‌ها
    'django.middleware.common.CommonMiddleware',       # 🔧 عمومی
    'django.middleware.csrf.CsrfViewMiddleware',       # 🛡️ محافظت CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 👤 احراز هویت
    'django.contrib.messages.middleware.MessageMiddleware',  # 💬 پیام‌ها
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 🚫 محافظت Clickjacking
    'core.middleware.CurrentUserMiddleware',           # 🔍 ردیابی کاربر فعلی برای لاگ‌ها
]

# 🌐 URL اصلی پروژه
ROOT_URLCONF = 'HomayOMS.urls'

# 📄 تنظیمات قالب‌ها (Templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 📁 مسیر قالب‌ها
        'APP_DIRS': True,  # جستجو در پوشه templates اپلیکیشن‌ها
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.permissions.user_permissions_context',  # 🔐 کنترل دسترسی کاربران
            ],
        },
    },
]

# 🌐 اپلیکیشن WSGI
WSGI_APPLICATION = 'HomayOMS.wsgi.application'

# 🗄️ تنظیمات پایگاه داده
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🔐 اعتبارسنجی رمز عبور
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 🌍 تنظیمات بین‌المللی‌سازی
LANGUAGE_CODE = 'fa-ir'       # 🇮🇷 زبان فارسی
TIME_ZONE = 'Asia/Tehran'     # ⏰ منطقه زمانی ایران
USE_I18N = True               # 📝 فعال‌سازی بین‌المللی‌سازی
USE_TZ = True                 # ⏰ استفاده از منطقه زمانی

# 📁 تنظیمات فایل‌های استاتیک (CSS, JavaScript, تصاویر)
STATIC_URL = STATIC_URL           # 🔗 URL فایل‌های استاتیک
STATIC_ROOT = STATIC_ROOT         # 📂 مسیر جمع‌آوری فایل‌های استاتیک
STATICFILES_DIRS = STATICFILES_DIRS  # 📂 مسیرهای جستجوی فایل‌های استاتیک

# 🖼️ تنظیمات فایل‌های رسانه‌ای
MEDIA_URL = MEDIA_URL      # 🔗 URL فایل‌های رسانه‌ای
MEDIA_ROOT = MEDIA_ROOT    # 📂 مسیر ذخیره فایل‌های آپلود شده

# 🔑 نوع کلید اصلی پیش‌فرض
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🔗 تنظیمات CORS - برای دسترسی از دامنه‌های مختلف
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS  # دامنه‌های مجاز
CORS_ALLOW_CREDENTIALS = True                 # اجازه ارسال کوکی‌ها

# 🛡️ تنظیمات امنیتی برای تولید
SECURE_BROWSER_XSS_FILTER = True      # 🚫 فیلتر XSS مرورگر
SECURE_CONTENT_TYPE_NOSNIFF = True    # 🚫 جلوگیری از Content-Type sniffing
X_FRAME_OPTIONS = 'DENY'              # 🚫 جلوگیری از iframe

# 👤 مدل کاربر سفارشی
AUTH_USER_MODEL = 'accounts.User' 

# 🚨 تنظیمات مدیریت خطاها
HANDLER_404 = 'HomayOMS.views.handler404'
HANDLER_500 = 'HomayOMS.views.handler500'

# 💳 تنظیمات درگاه‌های پرداخت
PAYMENT_SANDBOX = PAYMENT_SANDBOX
ZARINPAL_MERCHANT_ID = ZARINPAL_MERCHANT_ID
SHAPARAK_TERMINAL_ID = SHAPARAK_TERMINAL_ID
SHAPARAK_MERCHANT_ID = SHAPARAK_MERCHANT_ID 