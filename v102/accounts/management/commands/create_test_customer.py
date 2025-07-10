"""
🔵 دستور مدیریت برای ایجاد کاربر مشتری تست
👤 ایجاد کاربر مشتری با اطلاعات پیش‌فرض برای تست
🎯 استفاده: python manage.py create_test_customer
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = '🔵 ایجاد کاربر مشتری تست برای HomayOMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='customer_test',
            help='نام کاربری مشتری تست'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='customer123',
            help='رمز عبور مشتری تست'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='customer@homayoms.com',
            help='ایمیل مشتری تست'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='09123456789',
            help='شماره تلفن مشتری تست'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='مشتری',
            help='نام مشتری تست'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='تست',
            help='نام خانوادگی مشتری تست'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        phone = options['phone']
        first_name = options['first_name']
        last_name = options['last_name']

        # بررسی وجود کاربر
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️ کاربر {username} از قبل وجود دارد!')
            )
            return

        # بررسی وجود شماره تلفن
        if User.objects.filter(phone=phone).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️ شماره تلفن {phone} از قبل ثبت شده است!')
            )
            return

        try:
            # ایجاد کاربر مشتری
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=User.UserRole.CUSTOMER,
                status=User.UserStatus.ACTIVE,
                is_active=True,
                date_joined=timezone.now(),
                last_login=timezone.now()
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ کاربر مشتری {username} با موفقیت ایجاد شد!\n'
                    f'📋 اطلاعات ورود:\n'
                    f'   👤 نام کاربری: {username}\n'
                    f'   🔐 رمز عبور: {password}\n'
                    f'   📞 تلفن: {phone}\n'
                    f'   📧 ایمیل: {email}\n'
                    f'   🎭 نقش: {user.get_role_display()}\n'
                    f'   📊 وضعیت: {user.get_status_display()}\n'
                    f'\n🔗 لینک ورود مشتریان: /accounts/customer/login/'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در ایجاد کاربر: {str(e)}')
            ) 