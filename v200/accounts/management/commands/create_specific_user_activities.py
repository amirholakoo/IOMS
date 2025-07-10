"""
🎯 Management Command برای ایجاد Activity Log های مربوط به کاربران خاص
👥 این کامند برای ایجاد فعالیت‌های تست کاربران جدید استفاده می‌شود

🔧 نحوه استفاده:
    python manage.py create_specific_user_activities
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import ActivityLog, Customer, Product, Order
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = '🎯 ایجاد Activity Log های مربوط به کاربران خاص برای نمایش به رئیس'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 شروع ایجاد Activity Log های کاربران خاص...')
        )

        # 👥 یافتن کاربران خاص
        target_users = {
            'fallahnejad_admin': 'خانم فلاح نژاد',
            'imani_finance': 'خانم ایمانی',
            'salar_customer': 'شرکت سالار ایرانیان',
            'amir_superadmin': 'امیر هلاکو'
        }

        created_logs = 0

        for username, display_name in target_users.items():
            try:
                user = User.objects.get(username=username)
                
                # 📊 ایجاد فعالیت‌های مختلف برای هر کاربر
                activities = self.generate_user_activities(user, display_name)
                
                for activity in activities:
                    ActivityLog.objects.create(**activity)
                    created_logs += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {len(activities)} فعالیت برای {display_name} ({username}) ایجاد شد')
                )
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ کاربر {username} یافت نشد!')
                )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 مجموعاً {created_logs} Activity Log ایجاد شد!')
        )

    def generate_user_activities(self, user, display_name):
        """
        🎭 ایجاد فعالیت‌های متنوع برای هر کاربر بر اساس نقش آن‌ها
        """
        activities = []
        
        # 📅 بازه زمانی: 15 روز گذشته
        end_date = timezone.now()
        start_date = end_date - timedelta(days=15)
        
        # 🎭 فعالیت‌های مختلف بر اساس نقش کاربر
        if user.role == 'admin':
            activities.extend(self.admin_activities(user, display_name, start_date, end_date))
        elif user.role == 'finance':
            activities.extend(self.finance_activities(user, display_name, start_date, end_date))
        elif user.role == 'customer':
            activities.extend(self.customer_activities(user, display_name, start_date, end_date))
        elif user.role == 'super_admin':
            activities.extend(self.superadmin_activities(user, display_name, start_date, end_date))
        
        return activities

    def admin_activities(self, user, display_name, start_date, end_date):
        """🛠️ فعالیت‌های مربوط به Admin"""
        activities = []
        
        activities.append({
            'user': user,
            'action': 'LOGIN',
            'description': f'{display_name} وارد پنل مدیریت شد',
            'ip_address': '192.168.1.105',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'severity': 'LOW',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'VIEW',
            'description': f'{display_name} لیست مشتریان را مشاهده کرد',
            'ip_address': '192.168.1.105',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'severity': 'LOW',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'UPDATE',
            'description': f'{display_name} اطلاعات مشتری "شرکت آبان صنعت" را بروزرسانی کرد',
            'ip_address': '192.168.1.105',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'CREATE',
            'description': f'{display_name} مشتری جدید "شرکت پارسا تجارت" را در سیستم ثبت کرد',
            'ip_address': '192.168.1.105',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'VIEW',
            'description': f'{display_name} گزارش محصولات موجود در انبار را بررسی کرد',
            'ip_address': '192.168.1.105',
            'severity': 'LOW',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        return activities

    def finance_activities(self, user, display_name, start_date, end_date):
        """💰 فعالیت‌های مربوط به Finance"""
        activities = []
        
        activities.append({
            'user': user,
            'action': 'LOGIN',
            'description': f'{display_name} وارد بخش مالی شد',
            'ip_address': '192.168.1.108',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'severity': 'LOW',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'VIEW',
            'description': f'{display_name} گزارش مالی ماهانه را بررسی کرد',
            'ip_address': '192.168.1.108',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'APPROVE',
            'description': f'{display_name} سفارش شماره ORD-240629-008 را تایید کرد',
            'ip_address': '192.168.1.108',
            'severity': 'HIGH',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'PAYMENT',
            'description': f'{display_name} پرداخت 15,000,000 تومانی شرکت کاوه صنعت را ثبت کرد',
            'ip_address': '192.168.1.108',
            'severity': 'HIGH',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'EXPORT',
            'description': f'{display_name} گزارش مالی هفتگی را خروجی گرفت',
            'ip_address': '192.168.1.108',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'VIEW',
            'description': f'{display_name} لیست سفارشات معوقه را بررسی کرد',
            'ip_address': '192.168.1.108',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        return activities

    def customer_activities(self, user, display_name, start_date, end_date):
        """👤 فعالیت‌های مربوط به Customer"""
        activities = []
        
        activities.append({
            'user': user,
            'action': 'LOGIN',
            'description': f'{display_name} وارد پنل مشتری شد',
            'ip_address': '185.45.168.45',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'severity': 'LOW',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'VIEW',
            'description': f'{display_name} لیست محصولات موجود را مشاهده کرد',
            'ip_address': '185.45.168.45',
            'severity': 'LOW',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'ORDER',
            'description': f'{display_name} سفارش جدید برای 500 کیلوگرم کاغذ A4 ثبت کرد',
            'ip_address': '185.45.168.45',
            'severity': 'HIGH',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'UPDATE',
            'description': f'{display_name} آدرس تحویل سفارش را به "تهران، خیابان ولیعصر، پلاک 1250" تغییر داد',
            'ip_address': '185.45.168.45',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'VIEW',
            'description': f'{display_name} وضعیت سفارش‌هایش را بررسی کرد',
            'ip_address': '185.45.168.45',
            'severity': 'LOW',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        return activities

    def superadmin_activities(self, user, display_name, start_date, end_date):
        """👑 فعالیت‌های مربوط به Super Admin"""
        activities = []
        
        activities.append({
            'user': user,
            'action': 'LOGIN',
            'description': f'{display_name} وارد پنل مدیریت ارشد شد',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'PRICE_UPDATE',
            'description': f'{display_name} قیمت محصولات کاغذ A4 را 5% افزایش داد',
            'ip_address': '192.168.1.100',
            'severity': 'CRITICAL',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'CREATE',
            'description': f'{display_name} کاربر جدید "مدیر انبار" در سیستم ایجاد کرد',
            'ip_address': '192.168.1.100',
            'severity': 'HIGH',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'UPDATE',
            'description': f'{display_name} ساعات کاری فروشگاه را از 9 تا 18 تنظیم کرد',
            'ip_address': '192.168.1.100',
            'severity': 'HIGH',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'BACKUP',
            'description': f'{display_name} پشتیبان‌گیری کامل از پایگاه داده انجام داد',
            'ip_address': '192.168.1.100',
            'severity': 'CRITICAL',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'VIEW',
            'description': f'{display_name} گزارش عملکرد سیستم و Activity Log ها را بررسی کرد',
            'ip_address': '192.168.1.100',
            'severity': 'MEDIUM',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        activities.append({
            'user': user,
            'action': 'APPROVE',
            'description': f'{display_name} درخواست تخفیف 10% برای شرکت بزرگ پتروشیمی را تایید کرد',
            'ip_address': '192.168.1.100',
            'severity': 'HIGH',
            'created_at': self.random_datetime(start_date, end_date)
        })
        
        return activities

    def random_datetime(self, start_date, end_date):
        """📅 تولید تاریخ و زمان تصادفی در بازه مشخص"""
        time_between = end_date - start_date
        random_duration = random.random() * time_between.total_seconds()
        return start_date + timedelta(seconds=random_duration) 