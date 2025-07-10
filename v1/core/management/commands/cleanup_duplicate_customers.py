"""
🧹 مدیریت دستور پاکسازی مشتریان تکراری
🔧 حذف مشتریان تکراری و تثبیت یکپارچگی پایگاه داده
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Customer
from collections import defaultdict


class Command(BaseCommand):
    help = '🧹 پاکسازی مشتریان تکراری و تثبیت یکپارچگی پایگاه داده'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش تغییرات بدون اعمال آن‌ها',
        )
        parser.add_argument(
            '--by-name',
            action='store_true',
            help='پاکسازی بر اساس نام مشتری',
        )
        parser.add_argument(
            '--by-phone',
            action='store_true',
            help='پاکسازی بر اساس شماره تلفن',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        by_name = options['by_name']
        by_phone = options['by_phone']

        self.stdout.write(
            self.style.SUCCESS('🧹 شروع پاکسازی مشتریان تکراری...')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️ حالت نمایش تغییرات (بدون اعمال)')
            )

        # پاکسازی بر اساس نام
        if by_name or not (by_name or by_phone):
            self.cleanup_by_name(dry_run)

        # پاکسازی بر اساس شماره تلفن
        if by_phone or not (by_name or by_phone):
            self.cleanup_by_phone(dry_run)

        self.stdout.write(
            self.style.SUCCESS('✅ پاکسازی مشتریان تکراری تکمیل شد')
        )

    def cleanup_by_name(self, dry_run=False):
        """پاکسازی مشتریان تکراری بر اساس نام"""
        self.stdout.write('\n📝 پاکسازی بر اساس نام مشتری:')

        # گروه‌بندی مشتریان بر اساس نام
        customers_by_name = defaultdict(list)
        for customer in Customer.objects.all():
            if customer.customer_name:
                customers_by_name[customer.customer_name].append(customer)

        duplicates_found = 0
        duplicates_removed = 0

        for name, customers in customers_by_name.items():
            if len(customers) > 1:
                duplicates_found += 1
                self.stdout.write(f'\n🔍 نام تکراری: "{name}" ({len(customers)} مورد)')

                # مرتب‌سازی بر اساس تاریخ ایجاد (قدیمی‌ترین اول)
                customers.sort(key=lambda x: x.created_at)

                # نگه داشتن اولین مورد (قدیمی‌ترین) و حذف بقیه
                keep_customer = customers[0]
                remove_customers = customers[1:]

                self.stdout.write(f'   ✅ نگه داشتن: {keep_customer.id} (تاریخ: {keep_customer.created_at})')

                for customer in remove_customers:
                    self.stdout.write(f'   🗑️ حذف: {customer.id} (تاریخ: {customer.created_at})')
                    
                    if not dry_run:
                        try:
                            customer.delete()
                            duplicates_removed += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'   ❌ خطا در حذف {customer.id}: {e}')
                            )

        self.stdout.write(f'\n📊 خلاصه پاکسازی بر اساس نام:')
        self.stdout.write(f'   🔍 موارد تکراری یافت شده: {duplicates_found}')
        self.stdout.write(f'   🗑️ موارد حذف شده: {duplicates_removed}')

    def cleanup_by_phone(self, dry_run=False):
        """پاکسازی مشتریان تکراری بر اساس شماره تلفن"""
        self.stdout.write('\n📞 پاکسازی بر اساس شماره تلفن:')

        # گروه‌بندی مشتریان بر اساس شماره تلفن
        customers_by_phone = defaultdict(list)
        for customer in Customer.objects.all():
            if customer.phone:
                customers_by_phone[customer.phone].append(customer)

        duplicates_found = 0
        duplicates_removed = 0

        for phone, customers in customers_by_phone.items():
            if len(customers) > 1:
                duplicates_found += 1
                self.stdout.write(f'\n🔍 شماره تلفن تکراری: "{phone}" ({len(customers)} مورد)')

                # مرتب‌سازی بر اساس تاریخ ایجاد (قدیمی‌ترین اول)
                customers.sort(key=lambda x: x.created_at)

                # نگه داشتن اولین مورد (قدیمی‌ترین) و حذف بقیه
                keep_customer = customers[0]
                remove_customers = customers[1:]

                self.stdout.write(f'   ✅ نگه داشتن: {keep_customer.id} - {keep_customer.customer_name} (تاریخ: {keep_customer.created_at})')

                for customer in remove_customers:
                    self.stdout.write(f'   🗑️ حذف: {customer.id} - {keep_customer.customer_name} (تاریخ: {customer.created_at})')
                    
                    if not dry_run:
                        try:
                            customer.delete()
                            duplicates_removed += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'   ❌ خطا در حذف {customer.id}: {e}')
                            )

        self.stdout.write(f'\n📊 خلاصه پاکسازی بر اساس شماره تلفن:')
        self.stdout.write(f'   🔍 موارد تکراری یافت شده: {duplicates_found}')
        self.stdout.write(f'   🗑️ موارد حذف شده: {duplicates_removed}')
