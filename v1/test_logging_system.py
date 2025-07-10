#!/usr/bin/env python3
"""
🧪 تست سیستم لاگ‌گیری HomayOMS
📊 ایجاد داده‌های تست و بررسی لاگ‌ها در دیتابیس و فایل CSV
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
from core.models import Customer, Product, Order, OrderItem, ActivityLog
from accounts.models import User
from django.utils import timezone
from django.db import transaction
from django.db.models import Count

User = get_user_model()

def create_test_users():
    """👥 ایجاد کاربران تست"""
    print("👥 ایجاد کاربران تست...")
    
    users_data = [
        {
            'username': 'test_super_admin',
            'first_name': 'مدیر',
            'last_name': 'کل سیستم',
            'email': 'superadmin@test.com',
            'phone': '09123456789',
            'password': 'test123456',
            'role': 'super_admin'
        },
        {
            'username': 'test_admin',
            'first_name': 'مدیر',
            'last_name': 'عملیات',
            'email': 'admin@test.com',
            'phone': '09123456790',
            'password': 'test123456',
            'role': 'admin'
        },
        {
            'username': 'test_finance',
            'first_name': 'کاربر',
            'last_name': 'مالی',
            'email': 'finance@test.com',
            'phone': '09123456791',
            'password': 'test123456',
            'role': 'finance'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'email': user_data['email'],
                'phone': user_data['phone'],
                'role': user_data['role']
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ کاربر {user.username} ایجاد شد")
        else:
            print(f"ℹ️ کاربر {user.username} قبلاً وجود دارد")
        created_users.append(user)
    
    return created_users

def create_test_customers():
    """👤 ایجاد مشتریان تست"""
    print("👤 ایجاد مشتریان تست...")
    
    customers_data = [
        {
            'customer_name': 'شرکت کاغذ پارس',
            'phone': '02112345678',
            'email': 'info@pars-paper.com',
            'address': 'تهران، خیابان ولیعصر',
            'status': 'Active'
        },
        {
            'customer_name': 'کارخانه مقوا سازی ایران',
            'phone': '02187654321',
            'email': 'info@iran-cardboard.com',
            'address': 'اصفهان، شهرک صنعتی',
            'status': 'Active'
        },
        {
            'customer_name': 'مجتمع کاغذ سازی تهران',
            'phone': '02111223344',
            'email': 'info@tehran-paper.com',
            'address': 'تهران، جاده قدیم کرج',
            'status': 'Inactive'
        }
    ]
    
    created_customers = []
    for customer_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            customer_name=customer_data['customer_name'],
            defaults=customer_data
        )
        if created:
            print(f"✅ مشتری {customer.customer_name} ایجاد شد")
        else:
            print(f"ℹ️ مشتری {customer.customer_name} قبلاً وجود دارد")
        created_customers.append(customer)
    
    return created_customers

def create_test_products():
    """📦 ایجاد محصولات تست"""
    print("📦 ایجاد محصولات تست...")
    
    products_data = [
        {
            'reel_number': 'TEST-R001',
            'grade': 'A+',
            'location': 'A1',
            'status': 'In-stock',
            'price': 150000,
            'payment_status': 'Paid'
        },
        {
            'reel_number': 'TEST-R002',
            'grade': 'A',
            'location': 'A2',
            'status': 'In-stock',
            'price': 120000,
            'payment_status': 'Paid'
        },
        {
            'reel_number': 'TEST-R003',
            'grade': 'B+',
            'location': 'B1',
            'status': 'In-stock',
            'price': 100000,
            'payment_status': 'Unpaid'
        },
        {
            'reel_number': 'TEST-R004',
            'grade': 'B',
            'location': 'B2',
            'status': 'Sold',
            'price': 80000,
            'payment_status': 'Paid'
        },
        {
            'reel_number': 'TEST-R005',
            'grade': 'C+',
            'location': 'C1',
            'status': 'Pre-order',
            'price': 60000,
            'payment_status': 'Unpaid'
        }
    ]
    
    created_products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            reel_number=product_data['reel_number'],
            defaults=product_data
        )
        if created:
            print(f"✅ محصول {product.reel_number} ایجاد شد")
        else:
            print(f"ℹ️ محصول {product.reel_number} قبلاً وجود دارد")
        created_products.append(product)
    
    return created_products

def create_test_orders(customers, products, users):
    """🛒 ایجاد سفارشات تست"""
    print("🛒 ایجاد سفارشات تست...")
    
    orders_data = [
        {
            'customer': customers[0],
            'status': 'Confirmed',
            'payment_method': 'Cash',
            'notes': 'سفارش تست شماره 1',
            'created_by': users[0]
        },
        {
            'customer': customers[1],
            'status': 'Pending',
            'payment_method': 'Installment',
            'notes': 'سفارش تست شماره 2',
            'created_by': users[1]
        },
        {
            'customer': customers[2],
            'status': 'Cancelled',
            'payment_method': 'Cash',
            'notes': 'سفارش تست شماره 3',
            'created_by': users[2]
        }
    ]
    
    created_orders = []
    for order_data in orders_data:
        order = Order.objects.create(**order_data)
        print(f"✅ سفارش {order.order_number} ایجاد شد")
        
        # اضافه کردن اقلام سفارش
        num_items = random.randint(1, 3)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        for product in selected_products:
            quantity = random.randint(1, 5)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
                payment_method=order.payment_method
            )
            print(f"  📦 محصول {product.reel_number} به سفارش اضافه شد")
        
        created_orders.append(order)
    
    return created_orders

def simulate_user_activities(users, customers, products, orders):
    """🎭 شبیه‌سازی فعالیت‌های کاربران"""
    print("🎭 شبیه‌سازی فعالیت‌های کاربران...")
    
    # فعالیت‌های مختلف
    activities = [
        # ورود و خروج
        ('LOGIN', 'ورود موفق به سیستم'),
        ('LOGOUT', 'خروج از سیستم'),
        
        # مشاهده صفحات
        ('VIEW', 'مشاهده داشبورد مدیریت'),
        ('VIEW', 'مشاهده لیست محصولات'),
        ('VIEW', 'مشاهده لیست مشتریان'),
        ('VIEW', 'مشاهده لیست سفارشات'),
        ('VIEW', 'مشاهده لاگ‌های فعالیت'),
        
        # تغییر قیمت محصولات
        ('PRICE_UPDATE', 'تغییر قیمت محصول'),
        
        # ایجاد و ویرایش
        ('CREATE', 'ایجاد محصول جدید'),
        ('UPDATE', 'ویرایش اطلاعات محصول'),
        ('DELETE', 'حذف محصول'),
    ]
    
    for i in range(20):  # 20 فعالیت تصادفی
        user = random.choice(users)
        activity = random.choice(activities)
        
        if activity[0] == 'PRICE_UPDATE' and products:
            product = random.choice(products)
            old_price = product.price
            new_price = old_price + random.randint(-20000, 30000)
            if new_price < 0:
                new_price = 50000
            
            # ثبت لاگ تغییر قیمت
            ActivityLog.log_activity(
                user=user,
                action='PRICE_UPDATE',
                description=f'تغییر قیمت محصول {product.reel_number} از {old_price:,} به {new_price:,} تومان',
                content_object=product,
                severity='HIGH',
                old_price=float(old_price),
                new_price=float(new_price),
                price_change=float(new_price - old_price)
            )
            
            # بروزرسانی قیمت
            product.price = new_price
            product.price_updated_at = timezone.now()
            product.price_updated_by = user
            product.save()
            
            print(f"💰 تغییر قیمت محصول {product.reel_number} توسط {user.username}")
            
        elif activity[0] in ['CREATE', 'UPDATE', 'DELETE'] and products:
            product = random.choice(products)
            ActivityLog.log_activity(
                user=user,
                action=activity[0],
                description=f'{activity[1]} {product.reel_number}',
                content_object=product,
                severity='MEDIUM'
            )
            print(f"📦 {activity[1]} {product.reel_number} توسط {user.username}")
            
        else:
            ActivityLog.log_activity(
                user=user,
                action=activity[0],
                description=activity[1],
                severity='LOW'
            )
            print(f"👤 {activity[1]} توسط {user.username}")

def check_database_logs():
    """📊 بررسی لاگ‌های دیتابیس"""
    print("\n📊 بررسی لاگ‌های دیتابیس:")
    print("=" * 50)
    
    total_logs = ActivityLog.objects.count()
    print(f"📈 کل لاگ‌ها: {total_logs}")
    
    # آمار بر اساس نوع عملیات
    action_stats = ActivityLog.objects.values('action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    print("\n📋 آمار بر اساس نوع عملیات:")
    for stat in action_stats:
        print(f"  {stat['action']}: {stat['count']}")
    
    # آمار بر اساس سطح اهمیت
    severity_stats = ActivityLog.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('-count')
    
    print("\n⚠️ آمار بر اساس سطح اهمیت:")
    for stat in severity_stats:
        print(f"  {stat['severity']}: {stat['count']}")
    
    # آمار بر اساس کاربر
    user_stats = ActivityLog.objects.values('user__username').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    print("\n👤 آمار بر اساس کاربر (5 کاربر برتر):")
    for stat in user_stats:
        username = stat['user__username'] or 'سیستم'
        print(f"  {username}: {stat['count']}")
    
    # لاگ‌های اخیر
    recent_logs = ActivityLog.objects.select_related('user').order_by('-created_at')[:5]
    
    print("\n🕐 آخرین 5 لاگ:")
    for log in recent_logs:
        username = log.user.username if log.user else 'سیستم'
        print(f"  {log.created_at.strftime('%Y/%m/%d %H:%M:%S')} - {username}: {log.description}")

def check_csv_logs():
    """📄 بررسی فایل‌های CSV"""
    print("\n📄 بررسی فایل‌های CSV:")
    print("=" * 50)
    
    csv_dir = '../csv_logs'
    if os.path.exists(csv_dir):
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        
        if csv_files:
            print(f"📁 فایل‌های CSV موجود: {len(csv_files)}")
            
            for csv_file in csv_files:
                file_path = os.path.join(csv_dir, csv_file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                print(f"\n📄 {csv_file}:")
                print(f"  📏 اندازه: {file_size:,} بایت")
                print(f"  🕐 آخرین تغییر: {file_time.strftime('%Y/%m/%d %H:%M:%S')}")
                
                # خواندن چند خط اول
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"  📊 تعداد خطوط: {len(lines)}")
                        
                        if len(lines) > 1:  # اگر هدر و حداقل یک رکورد وجود دارد
                            print("  📋 نمونه رکوردها:")
                            for i, line in enumerate(lines[1:4]):  # 3 رکورد اول
                                if line.strip():
                                    print(f"    {i+1}. {line.strip()}")
                except Exception as e:
                    print(f"  ❌ خطا در خواندن فایل: {e}")
        else:
            print("❌ هیچ فایل CSV یافت نشد")
    else:
        print("❌ پوشه csv_logs وجود ندارد")

def run_export_command():
    """📤 اجرای دستور خروجی CSV"""
    print("\n📤 اجرای دستور خروجی CSV:")
    print("=" * 50)
    
    try:
        from django.core.management import call_command
        call_command('export_logs_to_csv')
        print("✅ دستور خروجی CSV با موفقیت اجرا شد")
    except Exception as e:
        print(f"❌ خطا در اجرای دستور: {e}")

def main():
    """🏃‍♂️ اجرای اصلی تست"""
    print("🧪 شروع تست سیستم لاگ‌گیری HomayOMS")
    print("=" * 60)
    
    try:
        # ایجاد داده‌های تست
        users = create_test_users()
        customers = create_test_customers()
        products = create_test_products()
        orders = create_test_orders(customers, products, users)
        
        # شبیه‌سازی فعالیت‌ها
        simulate_user_activities(users, customers, products, orders)
        
        # بررسی لاگ‌ها
        check_database_logs()
        check_csv_logs()
        
        # اجرای دستور خروجی
        run_export_command()
        
        # بررسی نهایی
        print("\n🔄 بررسی نهایی پس از خروجی CSV:")
        check_csv_logs()
        
        print("\n✅ تست سیستم لاگ‌گیری با موفقیت تکمیل شد!")
        print("\n📋 خلاصه:")
        print(f"  👥 کاربران: {len(users)}")
        print(f"  👤 مشتریان: {len(customers)}")
        print(f"  📦 محصولات: {len(products)}")
        print(f"  🛒 سفارشات: {len(orders)}")
        print(f"  📊 لاگ‌ها: {ActivityLog.objects.count()}")
        
    except Exception as e:
        print(f"❌ خطا در اجرای تست: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 