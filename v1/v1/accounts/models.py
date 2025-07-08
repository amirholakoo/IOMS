"""
👥 مدل‌های حساب کاربری و نقش‌ها - HomayOMS
🔐 سیستم مدیریت کاربران با نقش‌های مختلف و سطوح دسترسی منحصر به فرد
🎯 شامل Super Admin، Admin، و Finance با اختیارات کاملاً متفاوت
"""

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError
from HomayOMS.baseModel import BaseModel
from core.middleware import get_current_user


class User(AbstractUser, BaseModel):
    """
    👤 مدل کاربر سفارشی با سیستم نقش‌های پیشرفته
    
    🎯 این مدل کاربران سیستم را با نقش‌های مختلف مدیریت می‌کند
    🔐 هر نقش دارای اختیارات و محدودیت‌های منحصر به فرد است
    ⏰ دارای فیلدهای زمانی از BaseModel
    
    نقش‌های پشتیبانی شده:
    🔴 Super Admin: دسترسی کامل به تمام بخش‌ها
    🟡 Admin: مدیریت عملیات روزانه و گزارش‌گیری      
    🟢 Finance: مدیریت مالی، قیمت‌ها و فاکتورها
    """
    
    # 🏷️ انواع نقش‌های کاربری
    class UserRole(models.TextChoices):
        SUPER_ADMIN = 'super_admin', '🔴 Super Admin'
        ADMIN = 'admin', '🟡 Admin'
        FINANCE = 'finance', '🟢 Finance'
        CUSTOMER = 'customer', '🔵 Customer'
    
    # 📊 وضعیت‌های کاربر
    class UserStatus(models.TextChoices):
        ACTIVE = 'active', '✅ فعال'
        INACTIVE = 'inactive', '❌ غیرفعال'
        SUSPENDED = 'suspended', '⏸️ معلق'
        PENDING = 'pending', '⏳ در انتظار تأیید'
    
    # 🎭 نقش کاربر (اصلی‌ترین فیلد برای کنترل دسترسی)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        verbose_name="🎭 نقش کاربری",
        help_text="نقش کاربر که سطح دسترسی او را تعیین می‌کند"
    )
    
    # 📊 وضعیت کاربر
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.PENDING,
        verbose_name="📊 وضعیت کاربر",
        help_text="وضعیت فعلی کاربر در سیستم"
    )
    
    # 📞 شماره تلفن (اجباری برای احراز هویت)
    phone = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="📞 شماره تلفن",
        help_text="شماره تلفن همراه برای احراز هویت و تماس"
    )
    
    # 🏢 بخش کاری
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="🏢 بخش",
        help_text="بخش یا واحد کاری کاربر"
    )
    
    # 📝 توضیحات کاربر
    notes = models.TextField(
        blank=True,
        verbose_name="📝 یادداشت‌ها",
        help_text="یادداشت‌ها و توضیحات اضافی درباره کاربر"
    )
    
    # ⏰ آخرین ورود به سیستم
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="⏰ آخرین فعالیت",
        help_text="زمان آخرین فعالیت کاربر در سیستم"
    )
    
    # 🔐 تاریخ انقضای رمز عبور
    password_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="🔐 انقضای رمز عبور",
        help_text="تاریخ انقضای رمز عبور کاربر"
    )
    
    class Meta:
        verbose_name = "👤 کاربر"
        verbose_name_plural = "👥 کاربران"
        ordering = ['-created_at']
        
        # 📇 ایندکس‌های پایگاه داده
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['phone']),
            models.Index(fields=['username']),
        ]
        
        # 🔐 مجوزهای سفارشی برای هر نقش
        permissions = [
            # 🔴 Super Admin permissions
            ('manage_all_users', 'مدیریت کامل کاربران'),
            ('access_all_data', 'دسترسی به تمام داده‌ها'),
            ('system_settings', 'تنظیمات سیستم'),
            ('backup_restore', 'پشتیبان‌گیری و بازگردانی'),
            
            # 🟡 Admin permissions  
            ('manage_customers', 'مدیریت مشتریان'),
            ('manage_orders', 'مدیریت سفارشات'),
            ('manage_inventory', 'مدیریت موجودی'),
            ('view_reports', 'مشاهده گزارش‌ها'),
            ('manage_business_hours', 'مدیریت ساعات کاری'),
            
            # 🟢 Finance permissions
            ('manage_prices', 'مدیریت قیمت‌ها'),
            ('manage_invoices', 'مدیریت فاکتورها'),
            ('view_financial_reports', 'گزارش‌های مالی'),
            ('manage_payments', 'مدیریت پرداخت‌ها'),
            ('export_financial_data', 'خروجی داده‌های مالی'),
            
            # 🔵 Customer permissions
            ('view_own_orders', 'مشاهده سفارشات خود'),
            ('create_orders', 'ایجاد سفارش جدید'),
            ('view_own_profile', 'مشاهده پروفایل شخصی'),
            ('update_own_profile', 'ویرایش اطلاعات شخصی'),
        ]
    
    def clean(self):
        """
        🧹 اعتبارسنجی داده‌های کاربر
        """
        # 📞 بررسی فرمت شماره تلفن
        if self.phone and not self.phone.startswith('09'):
            raise ValidationError({
                'phone': '📞 شماره تلفن باید با 09 شروع شود'
            })
        
        # 👑 Super Admin هیچ محدودیتی ندارد - کامنت شده
        # if self.role == self.UserRole.SUPER_ADMIN:
        #     existing_super_admins = User.objects.filter(
        #         role=self.UserRole.SUPER_ADMIN
        #     ).exclude(pk=self.pk).count()
        #     
        #     if existing_super_admins >= 2:  # حداکثر 2 Super Admin
        #         raise ValidationError({
        #             'role': '🔴 حداکثر 2 Super Admin مجاز است'
        #         })
    
    def save(self, *args, **kwargs):
        """
        💾 ذخیره کاربر با تنظیم خودکار گروه‌ها و ایجاد Customer و لاگ کردن تغییرات
        """
        from core.models import ActivityLog
        
        # بررسی اینکه آیا این یک کاربر جدید است یا ویرایش
        is_new_user = not self.pk
        is_new_customer = False
        
        # اگر کاربر جدید نیست، اطلاعات قبلی را ذخیره کن
        if not is_new_user:
            try:
                old_user = User.objects.get(pk=self.pk)
                old_role = old_user.role
                old_status = old_user.status
                old_phone = old_user.phone
                old_username = old_user.username
            except User.DoesNotExist:
                old_role = None
                old_status = None
                old_phone = None
                old_username = None
        else:
            old_role = None
            old_status = None
            old_phone = None
            old_username = None
        
        # 🔐 اگر رمز عبور تغییر کرده، تاریخ انقضا را بازنشانی کن
        if self.pk:
            old_user = User.objects.get(pk=self.pk)
            if old_user.password != self.password:
                from django.utils import timezone
                from datetime import timedelta
                self.password_expires_at = timezone.now() + timedelta(days=90)
            
            # بررسی تغییر نقش به Customer
            if old_user.role != self.role and self.role == self.UserRole.CUSTOMER:
                is_new_customer = True
        
        # اگر کاربر جدید با نقش Customer است
        if is_new_user and self.role == self.UserRole.CUSTOMER:
            is_new_customer = True
        
        super().save(*args, **kwargs)
        
        # 🎭 تنظیم گروه کاربر بر اساس نقش
        self._assign_user_group()
        
        # 🔵 ایجاد خودکار Customer object برای کاربران Customer
        if is_new_customer:
            self._create_customer_profile()
        
        # دریافت کاربر فعلی
        current_user = get_current_user()
        
        # لاگ کردن عملیات فقط اگر کاربر معتبر باشد
        if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            if is_new_user:
                # کاربر جدید ایجاد شد
                ActivityLog.log_activity(
                    user=current_user,
                    action='CREATE',
                    description=f'👤 کاربر جدید ایجاد شد: {self.username} - نقش: {self.get_role_display()} - تلفن: {self.phone}',
                    content_object=self,
                    severity='HIGH',
                    extra_data={
                        'user_id': self.id,
                        'username': self.username,
                        'role': self.role,
                        'status': self.status,
                        'phone': self.phone,
                        'email': self.email,
                        'full_name': self.get_full_name()
                    }
                )
            else:
                # کاربر ویرایش شد - بررسی تغییرات مهم
                changes = []
                
                if old_role != self.role:
                    changes.append(f'🎭 نقش: {old_role} → {self.role}')
                
                if old_status != self.status:
                    changes.append(f'📊 وضعیت: {old_status} → {self.status}')
                
                if old_phone != self.phone:
                    changes.append(f'📞 تلفن: {old_phone} → {self.phone}')
                
                if old_username != self.username:
                    changes.append(f'👤 نام کاربری: {old_username} → {self.username}')
                
                # اگر تغییرات مهمی وجود دارد، لاگ کن
                if changes:
                    ActivityLog.log_activity(
                        user=current_user,
                        action='UPDATE',
                        description=f'📝 کاربر ویرایش شد: {self.username} - تغییرات: {", ".join(changes)}',
                        content_object=self,
                        severity='HIGH',
                        extra_data={
                            'user_id': self.id,
                            'username': self.username,
                            'changes': changes,
                            'old_role': old_role,
                            'new_role': self.role,
                            'old_status': old_status,
                            'new_status': self.status,
                            'old_phone': old_phone,
                            'new_phone': self.phone,
                            'old_username': old_username,
                            'new_username': self.username
                        }
                    )
    
    def _assign_user_group(self):
        """
        🎭 اختصاص گروه مناسب به کاربر بر اساس نقشش
        """
        # حذف از تمام گروه‌های قبلی
        self.groups.clear()
        
        # اضافه کردن به گروه مناسب
        group_name = f"{self.role}_group"
        group, created = Group.objects.get_or_create(name=group_name)
        self.groups.add(group)
        
        # تنظیم مجوزهای گروه
        self._setup_group_permissions(group)
    
    def _setup_group_permissions(self, group):
        """
        🔐 تنظیم مجوزهای هر گروه
        """
        # حذف مجوزهای قبلی
        group.permissions.clear()
        
        # مجوزهای هر نقش
        role_permissions = {
            self.UserRole.SUPER_ADMIN: [
                'manage_all_users', 'access_all_data', 'system_settings',
                'backup_restore', 'manage_customers', 'manage_orders',
                'manage_inventory', 'view_reports', 'manage_business_hours',
                'manage_prices', 'manage_invoices', 'view_financial_reports',
                'manage_payments', 'export_financial_data'
            ],
            self.UserRole.ADMIN: [
                'manage_customers', 'manage_orders', 'manage_inventory',
                'view_reports', 'manage_business_hours'
            ],
            self.UserRole.FINANCE: [
                'manage_prices', 'manage_invoices', 'view_financial_reports',
                'manage_payments', 'export_financial_data', 'view_reports'
            ],
            self.UserRole.CUSTOMER: [
                'view_own_orders', 'create_orders', 'view_own_profile',
                'update_own_profile'
            ]
        }
        
        # اضافه کردن مجوزهای مربوط به نقش
        permissions_list = role_permissions.get(self.role, [])
        for perm_codename in permissions_list:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass  # مجوز وجود ندارد، در migration ایجاد می‌شود
    
    def _create_customer_profile(self):
        """
        🔵 ایجاد خودکار پروفایل Customer برای کاربران با نقش Customer
        📋 این متد وقتی فراخوانی می‌شود که کاربر نقش Customer داشته باشد
        """
        # جلوگیری از import circular
        from core.models import Customer
        
        # بررسی اینکه آیا Customer object از قبل وجود دارد یا نه
        existing_customer = Customer.objects.filter(
            customer_name=self.get_full_name() or self.username
        ).first()
        
        if not existing_customer:
            # ایجاد Customer object جدید
            customer = Customer.objects.create(
                customer_name=self.get_full_name() or self.username,
                phone=self.phone if self.phone else '',
                address='',  # آدرس خالی - کاربر بعداً پر می‌کند
                comments=f'�� پروفایل خودکار ایجاد شده برای کاربر: {self.username}',
                status='Active',
                # اطلاعات قانونی خالی - کاربر در صورت نیاز پر می‌کند
                economic_code='',
                postcode='',
                national_id=''
            )
            
            # اتصال Customer به User (در آینده می‌توان یک ForeignKey اضافه کرد)
            # برای الان از طریق نام و شماره تلفن ارتباط برقرار می‌کنیم
            
            return customer
        
        return existing_customer
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای کاربر
        """
        role_emoji = {
            self.UserRole.SUPER_ADMIN: '🔴',
            self.UserRole.ADMIN: '🟡',
            self.UserRole.FINANCE: '🟢',
            self.UserRole.CUSTOMER: '🔵'
        }
        emoji = role_emoji.get(self.role, '👤')
        return f"{emoji} {self.get_full_name() or self.username}"
    
    def get_role_display_with_emoji(self):
        """
        🎭 نمایش نقش با ایموجی مناسب
        """
        return self.get_role_display()
    
    def is_super_admin(self):
        """
        🔴 بررسی Super Admin بودن کاربر
        """
        return self.role == self.UserRole.SUPER_ADMIN
    
    def is_admin(self):
        """
        🟡 بررسی Admin بودن کاربر
        """
        return self.role == self.UserRole.ADMIN
    
    def is_finance(self):
        """
        🟢 بررسی Finance بودن کاربر
        """
        return self.role == self.UserRole.FINANCE
    
    def is_customer(self):
        """
        🔵 بررسی Customer بودن کاربر
        """
        return self.role == self.UserRole.CUSTOMER
    
    def can_manage_users(self):
        """
        👥 بررسی اجازه مدیریت کاربران
        """
        return self.role == self.UserRole.SUPER_ADMIN
    
    def can_access_financial_data(self):
        """
        💰 بررسی دسترسی به داده‌های مالی
        """
        return self.role in [self.UserRole.SUPER_ADMIN, self.UserRole.FINANCE]
    
    def can_manage_inventory(self):
        """
        📦 بررسی اجازه مدیریت موجودی
        """
        return self.role in [self.UserRole.SUPER_ADMIN, self.UserRole.ADMIN]
    
    def get_accessible_features(self):
        """
        🔐 لیست ویژگی‌های قابل دسترس برای کاربر
        """
        features = {
            self.UserRole.SUPER_ADMIN: [
                '👥 مدیریت کاربران', '🔧 تنظیمات سیستم', '💾 پشتیبان‌گیری',
                '👤 مدیریت مشتریان', '📋 مدیریت سفارشات', '📦 مدیریت موجودی',
                '💰 مدیریت مالی', '📊 گزارش‌گیری', '⏰ ساعات کاری'
            ],
            self.UserRole.ADMIN: [
                '👤 مدیریت مشتریان', '📋 مدیریت سفارشات', '📦 مدیریت موجودی',
                '📊 گزارش‌گیری', '⏰ ساعات کاری'
            ],
            self.UserRole.FINANCE: [
                '💰 مدیریت قیمت‌ها', '🧾 مدیریت فاکتورها', '💳 مدیریت پرداخت‌ها',
                '📊 گزارش‌های مالی', '📤 خروجی داده‌های مالی'
            ],
            self.UserRole.CUSTOMER: [
                '📋 مشاهده سفارشات من', '🛒 ثبت سفارش جدید', '👤 ویرایش پروفایل',
                '📞 درخواست پشتیبانی', '📊 تاریخچه خرید'
            ]
        }
        return features.get(self.role, [])
    
    def is_active_user(self):
        """
        ✅ بررسی فعال بودن کاربر
        🔴 Super Admin همیشه فعال محسوب می‌شود
        """
        # Super Admin همیشه فعال است
        if self.is_super_admin():
            return True
        
        # سایر کاربران بر اساس وضعیت و فیلد is_active
        return self.status == self.UserStatus.ACTIVE and self.is_active


class UserSession(BaseModel):
    """
    📱 مدل نشست‌های کاربر برای ردیابی فعالیت
    🔍 ثبت ورود، خروج و فعالیت‌های کاربران
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="👤 کاربر"
    )
    
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="⏰ زمان ورود"
    )
    
    logout_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="⏰ زمان خروج"
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name="🌐 آدرس IP"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="🖥️ مشخصات مرورگر"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="✅ فعال"
    )
    
    class Meta:
        verbose_name = "📱 نشست کاربر"
        verbose_name_plural = "📱 نشست‌های کاربران"
        ordering = ['-login_time']
    
    def __str__(self):
        return f"📱 {self.user} - {self.login_time}"
    
    def get_session_duration(self):
        """
        ⏱️ محاسبه مدت زمان نشست
        """
        if self.logout_time:
            return self.logout_time - self.login_time
        else:
            from django.utils import timezone
            return timezone.now() - self.login_time
