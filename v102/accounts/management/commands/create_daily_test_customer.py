#!/usr/bin/env python
"""
📱 ایجاد مشتری تستی روزانه برای تست SMS
🎯 این دستور هر روز یک مشتری جدید با شماره موبایل منحصر به فرد ایجاد می‌کند
"""

import os
import sys
import django
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
import random
import string

class Command(BaseCommand):
    help = '📱 ایجاد مشتری تستی روزانه برای تست SMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='تعداد مشتریان تستی که ایجاد شوند (پیش‌فرض: 1)'
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='0915',
            help='پیشوند شماره موبایل (پیش‌فرض: 0915)'
        )

    def handle(self, *args, **options):
        count = options['count']
        prefix = options['prefix']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 شروع ایجاد {count} مشتری تستی...')
        )
        
        created_count = 0
        
        for i in range(count):
            try:
                # تولید شماره موبایل منحصر به فرد
                while True:
                    # تولید 7 رقم تصادفی
                    random_digits = ''.join(random.choices(string.digits, k=7))
                    phone = f"{prefix}{random_digits}"
                    
                    # بررسی اینکه شماره قبلاً وجود ندارد
                    if not User.objects.filter(phone=phone).exists():
                        break
                
                # تولید نام کاربری منحصر به فرد
                timestamp = datetime.now().strftime('%m%d_%H%M')
                username = f"test_customer_{timestamp}_{i+1}"
                
                # ایجاد مشتری
                customer = User.objects.create_user(
                    username=username,
                    password='123456',
                    first_name='مشتری',
                    last_name='تست',
                    role='customer',
                    phone=phone,
                    status='active'
                )
                
                created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ مشتری {created_count} ایجاد شد:\n'
                        f'   📞 شماره موبایل: {phone}\n'
                        f'   👤 نام کاربری: {username}\n'
                        f'   🔑 رمز عبور: 123456\n'
                        f'   📊 وضعیت: {customer.status}\n'
                        f'   ⏰ تاریخ ایجاد: {customer.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ خطا در ایجاد مشتری {i+1}: {str(e)}')
                )
        
        # خلاصه
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 عملیات تکمیل شد!\n'
                f'📊 تعداد مشتریان ایجاد شده: {created_count}\n'
                f'📱 برای تست SMS به آدرس زیر بروید:\n'
                f'   http://127.0.0.1:8000/accounts/customer/sms-login/\n'
                f'📋 کدهای تایید در ترمینال نمایش داده می‌شوند'
            )
        )
        
        # نمایش تمام مشتریان فعال
        active_customers = User.objects.filter(role='customer', status='active').order_by('-created_at')[:5]
        if active_customers:
            self.stdout.write(
                self.style.WARNING('\n📱 آخرین مشتریان فعال:')
            )
            for customer in active_customers:
                self.stdout.write(
                    f'   📞 {customer.phone} - {customer.username}'
                ) 