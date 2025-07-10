#!/usr/bin/env python
"""
🔄 همگام‌سازی کاربران و مشتریان
🎯 ایجاد Customer objects برای User های موجود که Customer role دارند
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from core.models import Customer


class Command(BaseCommand):
    help = '🔄 همگام‌سازی کاربران و مشتریان - ایجاد Customer objects برای User های موجود'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='اجبار بروزرسانی Customer های موجود'
        )
        parser.add_argument(
            '--create-test',
            action='store_true',
            help='ایجاد مشتریان تستی اضافی'
        )

    def handle(self, *args, **options):
        """🔄 اجرای اصلی دستور همگام‌سازی"""
        self.stdout.write(self.style.SUCCESS('🔄 شروع همگام‌سازی کاربران و مشتریان...'))
        
        # 📊 آمار قبل از همگام‌سازی
        total_users = User.objects.filter(role=User.UserRole.CUSTOMER).count()
        total_customers = Customer.objects.count()
        
        self.stdout.write(f'📊 قبل از همگام‌سازی: {total_users} کاربر Customer، {total_customers} مشتری')
        
        # 🔄 همگام‌سازی کاربران Customer با مشتریان
        customer_users = User.objects.filter(role=User.UserRole.CUSTOMER)
        created_count = 0
        updated_count = 0
        
        for user in customer_users:
            # بررسی وجود Customer برای این کاربر
            customer, created = Customer.objects.get_or_create(
                phone=user.phone,
                defaults={
                    'customer_name': user.get_full_name() or user.username,
                    'status': 'Active' if user.is_active else 'Inactive',
                    'comments': f'🔄 همگام‌سازی خودکار از کاربر: {user.username}'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✅ مشتری جدید ایجاد شد: {customer.customer_name} ({customer.phone})')
            else:
                # بروزرسانی Customer موجود
                old_name = customer.customer_name
                customer.customer_name = user.get_full_name() or user.username
                customer.status = 'Active' if user.is_active else 'Inactive'
                customer.save()
                updated_count += 1
                self.stdout.write(f'📝 مشتری بروزرسانی شد: {old_name} → {customer.customer_name}')
            
            # 🔄 همگام‌سازی وضعیت User با Customer
            if customer.status == 'Active' and user.status != User.UserStatus.ACTIVE:
                user.status = User.UserStatus.ACTIVE
                user.is_active = True
                user.save()
                self.stdout.write(f'🔄 وضعیت کاربر فعال شد: {user.username}')
            elif customer.status != 'Active' and user.status == User.UserStatus.ACTIVE:
                user.status = User.UserStatus.INACTIVE
                user.is_active = False
                user.save()
                self.stdout.write(f'🔄 وضعیت کاربر غیرفعال شد: {user.username}')
            
            # 🔄 همگام‌سازی معکوس: بروزرسانی Customer بر اساس User status
            if user.status == User.UserStatus.ACTIVE and customer.status != 'Active':
                customer.status = 'Active'
                customer.save()
                self.stdout.write(f'🔄 وضعیت مشتری فعال شد: {customer.customer_name}')
            elif user.status != User.UserStatus.ACTIVE and customer.status == 'Active':
                customer.status = 'Inactive'
                customer.save()
                self.stdout.write(f'🔄 وضعیت مشتری غیرفعال شد: {customer.customer_name}')
        
        # 🔄 همگام‌سازی معکوس: بروزرسانی Customer های بدون User
        customers_without_user = Customer.objects.filter(phone__isnull=True).exclude(phone='')
        for customer in customers_without_user:
            if customer.phone:
                # بررسی وجود User با این شماره تلفن
                user = User.objects.filter(phone=customer.phone).first()
                if not user:
                    # ایجاد User جدید برای این Customer
                    username = f"customer_{customer.id}"
                    user = User.objects.create_user(
                        username=username,
                        phone=customer.phone,
                        first_name=customer.customer_name.split()[0] if customer.customer_name else '',
                        last_name=' '.join(customer.customer_name.split()[1:]) if customer.customer_name and len(customer.customer_name.split()) > 1 else '',
                        role=User.UserRole.CUSTOMER,
                        status=User.UserStatus.ACTIVE if customer.status == 'Active' else User.UserStatus.INACTIVE,
                        is_active=customer.status == 'Active'
                    )
                    self.stdout.write(f'✅ کاربر جدید ایجاد شد: {user.username} برای مشتری {customer.customer_name}')
        
        # 🧹 حذف Customer های بدون شماره تلفن
        customers_without_phone = Customer.objects.filter(phone__isnull=True) | Customer.objects.filter(phone='')
        if customers_without_phone.exists():
            deleted_count = customers_without_phone.count()
            customers_without_phone.delete()
            self.stdout.write(f'🗑️ {deleted_count} مشتری بدون شماره تلفن حذف شد')
        
        # 📊 آمار نهایی
        final_users = User.objects.filter(role=User.UserRole.CUSTOMER).count()
        final_customers = Customer.objects.count()
        active_users = User.objects.filter(role=User.UserRole.CUSTOMER, status=User.UserStatus.ACTIVE).count()
        active_customers = Customer.objects.filter(status='Active').count()
        
        self.stdout.write(self.style.SUCCESS(f'✅ همگام‌سازی تکمیل شد!'))
        self.stdout.write(f'📊 نتایج نهایی:')
        self.stdout.write(f'   👥 کاربران Customer: {final_users} (فعال: {active_users})')
        self.stdout.write(f'   👤 مشتریان: {final_customers} (فعال: {active_customers})')
        self.stdout.write(f'   ➕ مشتریان جدید: {created_count}')
        self.stdout.write(f'   📝 مشتریان بروزرسانی شده: {updated_count}')
        
        # 🧪 ایجاد مشتریان تستی اگر درخواست شده
        if options['create_test']:
            self.create_test_customers()

    def create_test_customers(self):
        self.stdout.write(self.style.SUCCESS('🔄 ایجاد مشتریان تستی...'))
        
        test_customers = [
            {
                'customer_name': 'احمد محمدی',
                'phone': '09120000001',
                'status': 'Active',
                'address': 'تهران، خیابان ولیعصر',
                'national_id': '1234567890',
                'economic_code': '123456789',
                'postcode': '1234567890'
            },
            {
                'customer_name': 'فاطمه احمدی',
                'phone': '09120000002',
                'status': 'Active',
                'address': 'اصفهان، خیابان چهارباغ',
                'national_id': '0987654321',
                'economic_code': '987654321',
                'postcode': '0987654321'
            },
            {
                'customer_name': 'علی رضایی',
                'phone': '09120000003',
                'status': 'Active',
                'address': 'مشهد، خیابان امام رضا',
                'national_id': '1122334455',
                'economic_code': '112233445',
                'postcode': '1122334455'
            }
        ]
        
        for test_data in test_customers:
            if not Customer.objects.filter(phone=test_data['phone']).exists():
                try:
                    customer = Customer.objects.create(**test_data)
                    self.stdout.write(f'✅ ایجاد تستی: {customer.customer_name}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ خطا در ایجاد مشتری تستی: {e}')
                    ) 