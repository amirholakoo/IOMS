"""
⚙️ دستور راه‌اندازی نقش‌ها و مجوزها - HomayOMS
🔐 ایجاد گروه‌ها، مجوزها و کاربر Super Admin اولیه
🎯 اجرا پس از migration برای آماده‌سازی سیستم
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import User


class Command(BaseCommand):
    """
    ⚙️ دستور راه‌اندازی نقش‌ها و مجوزهای سیستم
    
    🔧 استفاده:
        python manage.py setup_roles
    """
    
    help = '🔐 راه‌اندازی نقش‌ها، گروه‌ها و مجوزهای سیستم'
    
    def add_arguments(self, parser):
        """
        📋 اضافه کردن آرگومان‌های دستور
        """
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='🔴 ایجاد کاربر Super Admin پیش‌فرض'
        )
        
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='👤 نام کاربری Super Admin (پیش‌فرض: admin)'
        )
        
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='🔐 رمز عبور Super Admin (پیش‌فرض: admin123)'
        )
        
        parser.add_argument(
            '--phone',
            type=str,
            default='09123456789',
            help='📞 شماره تلفن Super Admin'
        )
    
    def handle(self, *args, **options):
        """
        🎯 اجرای اصلی دستور
        """
        self.stdout.write(
            self.style.SUCCESS('🚀 شروع راه‌اندازی سیستم نقش‌ها و مجوزها...')
        )
        
        # 🏗️ ایجاد گروه‌های کاربری
        self.create_user_groups()
        
        # 🔐 تنظیم مجوزهای گروه‌ها
        self.setup_group_permissions()
        
        # 🔴 ایجاد Super Admin (در صورت درخواست)
        if options['create_superuser']:
            self.create_super_admin(
                username=options['username'],
                password=options['password'],
                phone=options['phone']
            )
        
        self.stdout.write(
            self.style.SUCCESS('✅ راه‌اندازی با موفقیت تکمیل شد!')
        )
    
    def create_user_groups(self):
        """
        🏗️ ایجاد گروه‌های کاربری
        """
        self.stdout.write('🏗️ ایجاد گروه‌های کاربری...')
        
        groups_data = [
            ('super_admin_group', '🔴 گروه Super Admin'),
            ('admin_group', '🟡 گروه Admin'),
            ('finance_group', '🟢 گروه Finance'),
            ('customer_group', '🔵 گروه Customer'),
        ]
        
        for group_name, description in groups_data:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'  ✅ گروه {description} ایجاد شد')
            else:
                self.stdout.write(f'  ⚡ گروه {description} قبلاً وجود دارد')
    
    def setup_group_permissions(self):
        """
        🔐 تنظیم مجوزهای گروه‌ها
        """
        self.stdout.write('🔐 تنظیم مجوزهای گروه‌ها...')
        
        # 🔍 دریافت content type مدل User
        user_content_type = ContentType.objects.get_for_model(User)
        
        # 📋 مجوزهای هر گروه
        group_permissions = {
            'super_admin_group': [
                'manage_all_users', 'access_all_data', 'system_settings',
                'backup_restore', 'manage_customers', 'manage_orders',
                'manage_inventory', 'view_reports', 'manage_business_hours',
                'manage_prices', 'manage_invoices', 'view_financial_reports',
                'manage_payments', 'export_financial_data'
            ],
            'admin_group': [
                'manage_customers', 'manage_orders', 'manage_inventory',
                'view_reports', 'manage_business_hours'
            ],
            'finance_group': [
                'manage_prices', 'manage_invoices', 'view_financial_reports',
                'manage_payments', 'export_financial_data', 'view_reports'
            ],
            'customer_group': [
                'view_own_orders', 'create_orders', 'view_own_profile',
                'update_own_profile'
            ]
        }
        
        # 🔄 تنظیم مجوزها برای هر گروه
        for group_name, permission_codenames in group_permissions.items():
            try:
                group = Group.objects.get(name=group_name)
                group.permissions.clear()  # حذف مجوزهای قبلی
                
                assigned_count = 0
                for codename in permission_codenames:
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=user_content_type
                        )
                        group.permissions.add(permission)
                        assigned_count += 1
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️ مجوز {codename} یافت نشد')
                        )
                
                self.stdout.write(
                    f'  ✅ {assigned_count} مجوز به گروه {group_name} اختصاص یافت'
                )
                
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ گروه {group_name} یافت نشد')
                )
    
    def create_super_admin(self, username, password, phone):
        """
        🔴 ایجاد کاربر Super Admin
        """
        self.stdout.write('🔴 ایجاد کاربر Super Admin...')
        
        # 🔍 بررسی وجود کاربر
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'  ⚠️ کاربر {username} قبلاً وجود دارد')
            )
            return
        
        # 🔍 بررسی وجود شماره تلفن
        if User.objects.filter(phone=phone).exists():
            self.stdout.write(
                self.style.WARNING(f'  ⚠️ شماره تلفن {phone} قبلاً استفاده شده')
            )
            return
        
        try:
            # 👤 ایجاد کاربر Super Admin
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f'{username}@homayoms.com',
                phone=phone,
                first_name='Super',
                last_name='Admin',
                role=User.UserRole.SUPER_ADMIN,
                status=User.UserStatus.ACTIVE,
                is_staff=True,
                is_superuser=True
            )
            
            # 📅 تنظیم تاریخ انقضای رمز عبور
            from django.utils import timezone
            from datetime import timedelta
            user.password_expires_at = timezone.now() + timedelta(days=90)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✅ کاربر Super Admin ایجاد شد:\n'
                    f'     👤 نام کاربری: {username}\n'
                    f'     🔐 رمز عبور: {password}\n'
                    f'     📞 تلفن: {phone}\n'
                    f'     🎭 نقش: {user.get_role_display()}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ خطا در ایجاد کاربر: {str(e)}')
            ) 