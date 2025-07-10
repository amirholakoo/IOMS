"""
👥 دستور مدیریت ایجاد کاربران تستی - HomayOMS
🔐 این دستور برای ایجاد کاربران نمونه با نقش‌های مختلف استفاده می‌شود
🎯 هدف: تست سیستم احراز هویت و کنترل دسترسی

🔧 استفاده:
    python manage.py create_test_users
    python manage.py create_test_users --reset
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    """
    👥 دستور ایجاد کاربران تستی
    🎛️ کلاس فرماندهی برای ایجاد کاربران با نقش‌های مختلف
    """
    
    help = '👥 ایجاد کاربران تستی برای نمایش قابلیت‌های سیستم'
    
    def add_arguments(self, parser):
        """
        ⚙️ اضافه کردن آرگومان‌های خط فرمان
        """
        parser.add_argument(
            '--reset',
            action='store_true',
            help='🗑️ حذف کاربران تستی موجود و ایجاد مجدد'
        )
    
    def handle(self, *args, **options):
        """
        🚀 اجرای اصلی دستور
        """
        reset = options['reset']
        
        try:
            with transaction.atomic():
                # 🗑️ حذف کاربران تستی موجود (در صورت درخواست)
                if reset:
                    self._delete_test_users()
                
                # 👥 ایجاد کاربران تستی
                created_users = self._create_test_users()
                
                # 📊 نمایش خلاصه نتایج
                self._display_summary(created_users)
                
                # 🎉 پیام موفقیت
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🎉 عملیات با موفقیت انجام شد! {len(created_users)} کاربر ایجاد شد.'
                    )
                )
                
        except Exception as e:
            # ❌ مدیریت خطاها
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در اجرای دستور: {str(e)}')
            )
            raise CommandError(f'❌ خطا در ایجاد کاربران تستی: {str(e)}')
    
    def _delete_test_users(self):
        """
        🗑️ حذف کاربران تستی موجود
        """
        test_usernames = ['super_admin_test', 'admin_test', 'finance_test', 'customer_test']
        deleted_count = 0
        
        for username in test_usernames:
            try:
                user = User.objects.get(username=username)
                user.delete()
                deleted_count += 1
                self.stdout.write(f'🗑️ کاربر {username} حذف شد')
            except User.DoesNotExist:
                pass
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(f'🗑️ {deleted_count} کاربر تستی حذف شد.')
            )
    
    def _create_test_users(self):
        """
        👥 ایجاد کاربران تستی با نقش‌های مختلف
        """
        users_data = [
            {
                'username': 'super_admin_test',
                'password': 'super123',
                'email': 'super@homayoms.com',
                'first_name': 'سوپر',
                'last_name': 'ادمین',
                'phone': '09100000001',
                'role': User.UserRole.SUPER_ADMIN,
                'status': User.UserStatus.ACTIVE,
                'is_superuser': True,
                'is_staff': True,
                'department': 'مدیریت کل'
            },
            {
                'username': 'admin_test',
                'password': 'admin123',
                'email': 'admin@homayoms.com',
                'first_name': 'مدیر',
                'last_name': 'عملیات',
                'phone': '09100000002',
                'role': User.UserRole.ADMIN,
                'status': User.UserStatus.ACTIVE,
                'is_staff': True,
                'department': 'عملیات'
            },
            {
                'username': 'finance_test',
                'password': 'finance123',
                'email': 'finance@homayoms.com',
                'first_name': 'مدیر',
                'last_name': 'مالی',
                'phone': '09100000003',
                'role': User.UserRole.FINANCE,
                'status': User.UserStatus.ACTIVE,
                'is_staff': True,
                'department': 'مالی'
            },
            {
                'username': 'customer_test',
                'password': 'customer123',
                'email': 'customer@homayoms.com',
                'first_name': 'مشتری',
                'last_name': 'تستی',
                'phone': '09100000004',
                'role': User.UserRole.CUSTOMER,
                'status': User.UserStatus.ACTIVE,
                'is_staff': False,
                'department': ''
            }
        ]
        
        created_users = []
        
        for user_data in users_data:
            # بررسی وجود کاربر
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️ کاربر {user_data["username"]} از قبل وجود دارد')
                )
                continue
            
            # ایجاد کاربر
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                role=user_data['role'],
                status=user_data['status'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data.get('is_superuser', False),
                department=user_data['department']
            )
            
            created_users.append(user)
            
            # نمایش پیام ایجاد
            role_emoji = {
                User.UserRole.SUPER_ADMIN: '🔴',
                User.UserRole.ADMIN: '🟡',
                User.UserRole.FINANCE: '🟢',
                User.UserRole.CUSTOMER: '🔵'
            }
            emoji = role_emoji.get(user.role, '👤')
            
            self.stdout.write(
                f'✅ {emoji} کاربر {user.username} ({user.get_role_display()}) ایجاد شد'
            )
        
        return created_users
    
    def _display_summary(self, created_users):
        """
        📊 نمایش خلاصه کاربران ایجاد شده
        """
        if not created_users:
            self.stdout.write('📋 هیچ کاربر جدیدی ایجاد نشد.')
            return
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('📋 اطلاعات ورود کاربران تستی:')
        self.stdout.write('=' * 80)
        
        for user in created_users:
            role_info = {
                User.UserRole.SUPER_ADMIN: {
                    'emoji': '🔴',
                    'description': 'دسترسی کامل به سیستم + تغییر قیمت محصولات',
                    'login_url': '/admin/ یا /accounts/staff/login/'
                },
                User.UserRole.ADMIN: {
                    'emoji': '🟡', 
                    'description': 'مدیریت عملیات، مشتریان و موجودی',
                    'login_url': '/accounts/staff/login/'
                },
                User.UserRole.FINANCE: {
                    'emoji': '🟢',
                    'description': 'مدیریت مالی و گزارش‌های مالی',
                    'login_url': '/accounts/staff/login/'
                },
                User.UserRole.CUSTOMER: {
                    'emoji': '🔵',
                    'description': 'مشاهده سفارشات و پروفایل شخصی',
                    'login_url': '/accounts/customer/login/ (فقط SMS)'
                }
            }
            
            info = role_info.get(user.role, {})
            
            self.stdout.write(f'\n{info.get("emoji", "👤")} {user.get_role_display()}:')
            self.stdout.write(f'   👤 نام کاربری: {user.username}')
            
            # برای Customer فقط شماره تلفن نمایش داده می‌شود
            if user.role == User.UserRole.CUSTOMER:
                self.stdout.write(f'   📞 شماره تلفن: {user.phone} (برای ورود با SMS)')
            else:
                self.stdout.write(f'   🔐 رمز عبور: {self._get_password_for_user(user.username)}')
            
            self.stdout.write(f'   📧 ایمیل: {user.email}')
            self.stdout.write(f'   🌐 آدرس ورود: {info.get("login_url", "/accounts/login/")}')
            self.stdout.write(f'   📋 دسترسی‌ها: {info.get("description", "تعریف نشده")}')
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('🔗 لینک‌های مفید:')
        self.stdout.write('   🏠 صفحه اصلی: http://127.0.0.1:8000/')
        self.stdout.write('   🔑 ورود اصلی: http://127.0.0.1:8000/accounts/login/')
        self.stdout.write('   👥 ورود کارمندان: http://127.0.0.1:8000/accounts/staff/login/')
        self.stdout.write('   🔵 ورود مشتریان: http://127.0.0.1:8000/accounts/customer/login/')
        self.stdout.write('   🎛️ پنل مدیریت: http://127.0.0.1:8000/admin/')
        self.stdout.write('=' * 80)
    
    def _get_password_for_user(self, username):
        """
        🔐 دریافت رمز عبور برای نمایش
        """
        passwords = {
            'super_admin_test': 'super123',
            'admin_test': 'admin123', 
            'finance_test': 'finance123',
            'customer_test': 'customer123'
        }
        return passwords.get(username, '***') 