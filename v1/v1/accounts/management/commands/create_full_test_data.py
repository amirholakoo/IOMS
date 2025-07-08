#!/usr/bin/env python
"""
🎯 ایجاد داده تستی کامل برای همه نقش‌ها و چاپ اطلاعات ورود
"""
from django.core.management.base import BaseCommand
from accounts.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string

class Command(BaseCommand):
    help = '🎯 ایجاد داده تستی کامل برای همه نقش‌ها و چاپ اطلاعات ورود'

    def handle(self, *args, **options):
        users_data = [
            # Super Admin
            {
                'username': 'superadmin1',
                'password': '123456',
                'first_name': 'علی',
                'last_name': 'مدیرارشد',
                'role': User.UserRole.SUPER_ADMIN,
                'phone': '09120000001',
                'email': 'superadmin1@homayoms.com',
                'is_staff': True,
                'is_superuser': True,
            },
            # Admin
            {
                'username': 'admin1',
                'password': '123456',
                'first_name': 'مریم',
                'last_name': 'ادمین',
                'role': User.UserRole.ADMIN,
                'phone': '09120000002',
                'email': 'admin1@homayoms.com',
                'is_staff': True,
                'is_superuser': False,
            },
            # Finance
            {
                'username': 'finance1',
                'password': '123456',
                'first_name': 'رضا',
                'last_name': 'مالی',
                'role': User.UserRole.FINANCE,
                'phone': '09120000003',
                'email': 'finance1@homayoms.com',
                'is_staff': True,
                'is_superuser': False,
            },
            # Customer 1
            {
                'username': 'customer1',
                'password': '123456',
                'first_name': 'سارا',
                'last_name': 'مشتری',
                'role': User.UserRole.CUSTOMER,
                'phone': '09120000004',
                'email': 'customer1@homayoms.com',
                'is_staff': False,
                'is_superuser': False,
            },
            # Customer 2
            {
                'username': 'customer2',
                'password': '123456',
                'first_name': 'حسین',
                'last_name': 'مشتری',
                'role': User.UserRole.CUSTOMER,
                'phone': '09120000005',
                'email': 'customer2@homayoms.com',
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        created_users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data['role'],
                    'phone': data['phone'],
                    'email': data['email'],
                    'status': User.UserStatus.ACTIVE,
                    'is_staff': data['is_staff'],
                    'is_superuser': data['is_superuser'],
                }
            )
            if created:
                user.set_password(data['password'])
                user.password_expires_at = timezone.now() + timedelta(days=90)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ کاربر {user.username} ساخته شد."))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ کاربر {user.username} قبلاً وجود دارد."))
            created_users.append((user, data['password']))

        # چاپ جدول اطلاعات ورود
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📋 اطلاعات ورود تستی برای همه نقش‌ها:')
        self.stdout.write('-'*60)
        self.stdout.write(f"{'نقش':<15}{'نام کاربری':<15}{'موبایل':<15}{'رمز عبور':<12}")
        self.stdout.write('-'*60)
        for user, password in created_users:
            role_display = user.get_role_display()
            self.stdout.write(f"{role_display:<15}{user.username:<15}{user.phone:<15}{password:<12}")
        self.stdout.write('='*60)
        self.stdout.write('✅ حالا می‌توانید با این اطلاعات وارد شوید!') 