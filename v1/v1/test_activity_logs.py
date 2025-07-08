#!/usr/bin/env python
"""
🧪 تست لاگ‌های فعالیت - HomayOMS
📝 ایجاد لاگ‌های نمونه برای نمایش عملکرد سیستم
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Customer, Product, Order, ActivityLog
from accounts.models import User

User = get_user_model()

def create_test_logs():
    """📝 ایجاد لاگ‌های تست"""
    
    print("🧪 شروع ایجاد لاگ‌های تست...")
    
    # دریافت کاربران موجود
    users = list(User.objects.all())
    if not users:
        print("❌ هیچ کاربری یافت نشد!")
        return
    
    # دریافت محصولات موجود
    products = list(Product.objects.all())
    if not products:
        print("❌ هیچ محصولی یافت نشد!")
        return
    
    # دریافت مشتریان موجود
    customers = list(Customer.objects.all())
    if not customers:
        print("❌ هیچ مشتری یافت نشد!")
        return
    
    # انواع عملیات
    actions = ['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'LOGIN', 'LOGOUT', 'PRICE_UPDATE']
    severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    # ایجاد لاگ‌های متنوع
    for i in range(20):
        user = random.choice(users)
        action = random.choice(actions)
        severity = random.choice(severities)
        
        # توضیحات مختلف بر اساس نوع عملیات
        if action == 'CREATE':
            if random.choice([True, False]):
                description = f"ایجاد مشتری جدید: {random.choice(['شرکت آلفا', 'شرکت بتا', 'شرکت گاما'])}"
            else:
                description = f"ایجاد محصول جدید: ریل شماره R{random.randint(100, 999)}"
        elif action == 'UPDATE':
            if random.choice([True, False]):
                description = f"بروزرسانی اطلاعات مشتری: {random.choice(customers).customer_name}"
            else:
                description = f"بروزرسانی اطلاعات محصول: {random.choice(products).reel_number}"
        elif action == 'DELETE':
            description = f"حذف {random.choice(['مشتری', 'محصول', 'سفارش'])}"
        elif action == 'VIEW':
            descriptions = [
                "مشاهده داشبورد مدیریت",
                "مشاهده لیست محصولات",
                "مشاهده لیست مشتریان",
                "مشاهده لاگ‌های فعالیت",
                "مشاهده گزارش مالی"
            ]
            description = random.choice(descriptions)
        elif action == 'LOGIN':
            description = f"ورود موفق کاربر {user.username}"
        elif action == 'LOGOUT':
            description = f"خروج کاربر {user.username}"
        elif action == 'PRICE_UPDATE':
            product = random.choice(products)
            old_price = product.price
            new_price = old_price + random.randint(-50000, 100000)
            description = f"تغییر قیمت محصول {product.reel_number} از {old_price:,} به {new_price:,} تومان"
        
        # ایجاد لاگ
        log = ActivityLog.objects.create(
            user=user,
            action=action,
            description=description,
            severity=severity,
            ip_address=f"192.168.1.{random.randint(100, 200)}",
            user_agent=f"Chrome/{random.randint(90, 120)}.0.{random.randint(1000, 9999)}.0",
        )
        
        # برای تغییرات قیمت، اطلاعات اضافی اضافه کن
        if action == 'PRICE_UPDATE':
            log.old_price = old_price
            log.new_price = new_price
            log.price_change = new_price - old_price
            log.save()
        
        print(f"✅ لاگ {i+1}/20 ایجاد شد: {action} - {severity}")
    
    print("🎉 ایجاد لاگ‌های تست با موفقیت انجام شد!")
    print(f"📊 تعداد کل لاگ‌ها: {ActivityLog.objects.count()}")

if __name__ == '__main__':
    create_test_logs() 