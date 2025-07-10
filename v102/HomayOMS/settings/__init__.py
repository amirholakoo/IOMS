"""
🔄 ماژول مقداردهی تنظیمات - HomayOMS
🎯 این فایل مسئول انتخاب و واردات تنظیمات مناسب بر اساس نوع محیط است
⚙️ محیط‌های پشتیبانی شده: local, dev, production
"""

import sys
import os

# 📁 اضافه کردن مسیر اصلی پروژه به Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 📥 واردات نوع سرور از فایل پیکربندی
from config import SERVER_TYPE

# 🔀 انتخاب تنظیمات مناسب بر اساس نوع محیط
if SERVER_TYPE == 'production':
    # 🏭 محیط تولید - امنیت بالا، PostgreSQL
    from .production import *
elif SERVER_TYPE == 'dev':
    # 🔧 محیط توسعه - تست و آزمایش
    from .dev import *
else:  
    # 🏠 محیط محلی - پیش‌فرض برای توسعه محلی
    from .local import * 