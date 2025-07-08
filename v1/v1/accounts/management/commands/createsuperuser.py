"""
🔴 دستور سفارشی ایجاد Super Admin - HomayOMS
👑 جایگزین دستور پیش‌فرض Django برای ایجاد superuser
🎯 کاربران ایجاد شده با این دستور نقش SUPER_ADMIN دریافت می‌کنند
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core.management.utils import get_random_secret_key
from django.db import DEFAULT_DB_ALIAS
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import getpass
import sys

User = get_user_model()


class Command(BaseCommand):
    """
    🔴 دستور سفارشی ایجاد Super Admin
    
    🔧 استفاده:
        python manage.py createsuperuser
        python manage.py createsuperuser --username admin --phone 09123456789
    """
    
    help = '🔴 ایجاد کاربر Super Admin با دسترسی کامل به سیستم'
    requires_migrations_checks = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = User
        self.username_field = self.UserModel._meta.get_field(self.UserModel.USERNAME_FIELD)
    
    def add_arguments(self, parser):
        """
        📋 اضافه کردن آرگومان‌های دستور
        """
        parser.add_argument('--username', help='نام کاربری Super Admin')
        parser.add_argument('--phone', help='شماره تلفن Super Admin (اجباری)')
        parser.add_argument('--email', help='ایمیل Super Admin')
        parser.add_argument('--noinput', '--no-input', action='store_true', 
                          help='تنظیم پیش‌فرض بدون درخواست ورودی از کاربر')
        parser.add_argument('--database', default=DEFAULT_DB_ALIAS,
                          help='پایگاه داده برای ذخیره کاربر')
    
    def handle(self, *args, **options):
        """
        🎯 اجرای اصلی دستور
        """
        username = options['username']
        phone = options['phone']
        email = options['email']
        database = options['database']
        
        self.stdout.write(self.style.SUCCESS('🔴 شروع ایجاد کاربر Super Admin...'))
        
        # بررسی اتصال به پایگاه داده
        try:
            self.UserModel._default_manager.db_manager(database).get_queryset().exists()
        except Exception as e:
            raise CommandError(f"❌ خطا در اتصال به پایگاه داده: {e}")
        
        user_data = {}
        
        # 1️⃣ دریافت نام کاربری
        if username is None:
            username = self.get_input_username()
        
        # بررسی منحصر به فرد بودن نام کاربری
        try:
            self.UserModel._default_manager.db_manager(database).get_by_natural_key(username)
        except self.UserModel.DoesNotExist:
            pass
        else:
            raise CommandError(f"❌ کاربری با نام '{username}' قبلاً وجود دارد")
        
        user_data[self.UserModel.USERNAME_FIELD] = username
        
        # 2️⃣ دریافت شماره تلفن (اجباری)
        if phone is None:
            phone = self.get_input_phone()
        
        # بررسی منحصر به فرد بودن شماره تلفن
        if self.UserModel.objects.filter(phone=phone).exists():
            raise CommandError(f"❌ شماره تلفن '{phone}' قبلاً استفاده شده است")
        
        user_data['phone'] = phone
        
        # 3️⃣ دریافت ایمیل
        if email is None:
            email = self.get_input_email(username)
        
        user_data['email'] = email
        
        # 4️⃣ دریافت رمز عبور
        if not options['noinput']:
            password = self.get_input_password()
        else:
            password = get_random_secret_key()
            self.stdout.write(f"🔐 رمز عبور خودکار: {password}")
        
        # 5️⃣ ایجاد کاربر Super Admin
        try:
            user = self.UserModel._default_manager.db_manager(database).create_user(
                username=username,
                email=email,
                phone=phone,
                password=password,
                first_name='Super',
                last_name='Admin',
                role=User.UserRole.SUPER_ADMIN,  # 🔴 نقش SUPER_ADMIN
                status=User.UserStatus.ACTIVE,   # ✅ فعال
                is_staff=True,                   # 🎛️ دسترسی به پنل مدیریت
                is_superuser=True,               # 👑 superuser Django
                is_active=True                   # ✅ حساب فعال
            )
            
            # 📅 تنظیم تاریخ انقضای رمز عبور (90 روز)
            user.password_expires_at = timezone.now() + timedelta(days=90)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ کاربر Super Admin با موفقیت ایجاد شد!\n'
                    f'     👤 نام کاربری: {username}\n'
                    f'     📞 تلفن: {phone}\n'
                    f'     📧 ایمیل: {email}\n'
                    f'     🎭 نقش: {user.get_role_display()}\n'
                    f'     📊 وضعیت: {user.get_status_display()}'
                )
            )
            
            # نمایش اطلاعات دسترسی
            self.stdout.write(
                self.style.WARNING(
                    f'\n🌐 برای ورود به سیستم:\n'
                    f'     🔗 پنل مدیریت: http://localhost:8000/admin/\n'
                    f'     🎛️ داشبورد Admin: http://localhost:8000/core/admin-dashboard/\n'
                    f'     👤 نام کاربری: {username}'
                )
            )
            
        except Exception as e:
            raise CommandError(f"❌ خطا در ایجاد کاربر: {str(e)}")
    
    def get_input_username(self):
        """👤 دریافت نام کاربری از کاربر"""
        while True:
            username = input("👤 نام کاربری Super Admin: ")
            if not username:
                self.stderr.write("❌ نام کاربری نمی‌تواند خالی باشد")
                continue
            if len(username) < 3:
                self.stderr.write("❌ نام کاربری باید حداقل 3 کاراکتر باشد")
                continue
            return username
    
    def get_input_phone(self):
        """📞 دریافت شماره تلفن از کاربر"""
        while True:
            phone = input("📞 شماره تلفن Super Admin (مثال: 09123456789): ")
            if not phone:
                self.stderr.write("❌ شماره تلفن اجباری است")
                continue
            if not phone.startswith('09') or len(phone) != 11:
                self.stderr.write("❌ شماره تلفن باید با 09 شروع شود و 11 رقم باشد")
                continue
            return phone
    
    def get_input_email(self, username):
        """📧 دریافت ایمیل از کاربر"""
        default_email = f"{username}@homayoms.com"
        email = input(f"📧 ایمیل Super Admin (پیش‌فرض: {default_email}): ")
        
        if not email:
            email = default_email
        
        # اعتبارسنجی ایمیل
        try:
            validate_email(email)
        except ValidationError:
            self.stderr.write("❌ فرمت ایمیل نامعتبر است")
            return self.get_input_email(username)
        
        return email
    
    def get_input_password(self):
        """🔐 دریافت رمز عبور از کاربر"""
        while True:
            password = getpass.getpass("🔐 رمز عبور Super Admin: ")
            if not password:
                self.stderr.write("❌ رمز عبور نمی‌تواند خالی باشد")
                continue
            if len(password) < 8:
                self.stderr.write("❌ رمز عبور باید حداقل 8 کاراکتر باشد")
                continue
            password2 = getpass.getpass("🔐 تکرار رمز عبور: ")
            if password != password2:
                self.stderr.write("❌ رمزهای عبور مطابقت ندارند")
                continue
            return password