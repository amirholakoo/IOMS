"""
🏢 مدل‌های اصلی اپلیکیشن Core - HomayOMS
📋 این فایل شامل مدل‌های اصلی کسب‌وکار مانند مشتری، محصولات و سیستم لاگ‌گیری است
👥 تمام مدل‌ها از BaseModel ارث‌بری می‌کنند تا دارای فیلدهای زمانی باشند
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from HomayOMS.baseModel import BaseModel
from core.middleware import get_current_user
import json
from decimal import Decimal
from django.utils import timezone
from django.core.management import call_command


class Customer(BaseModel):
    """
    👤 مدل مشتری - اطلاعات کامل مشتریان سیستم
    
    🎯 این مدل برای ذخیره اطلاعات مشتریان کسب‌وکار استفاده می‌شود
    📋 شامل اطلاعات تماس، آدرس، و کدهای قانونی مشتری
    ⏰ دارای فیلدهای created_at و updated_at از BaseModel
    
    🔧 استفاده:
        customer = Customer.objects.create(
            customer_name="نام مشتری",
            phone="09123456789",
            address="آدرس کامل"
        )
    """
    
    # 📊 گزینه‌های وضعیت مشتری
    STATUS_CHOICES = [
        ('Active', '✅ فعال'),
        ('Inactive', '⏸️ غیرفعال'),
        ('Suspended', '🚫 معلق'),
        ('Blocked', '🔒 مسدود'),
    ]
    
    # 📊 وضعیت مشتری
    status = models.CharField(
        max_length=255, 
        choices=STATUS_CHOICES,
        default='Active',
        verbose_name="📊 وضعیت مشتری",
        help_text="وضعیت فعلی مشتری در سیستم"
    )
    
    # 👤 نام مشتری (اجباری)
    customer_name = models.CharField(
        max_length=255, 
        null=False,
        verbose_name="👤 نام مشتری",
        help_text="نام کامل یا نام شرکت مشتری (اجباری)"
    )
    
    # 🏠 آدرس کامل
    address = models.TextField(
        blank=True,
        verbose_name="🏠 آدرس",
        help_text="آدرس کامل محل سکونت یا کسب‌وکار مشتری"
    )
    
    # 📞 شماره تلفن
    phone = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name="📞 شماره تلفن",
        help_text="شماره تلفن تماس مشتری (همراه یا ثابت)"
    )
    
    # 💬 توضیحات اضافی
    comments = models.TextField(
        blank=True,
        verbose_name="💬 توضیحات",
        help_text="یادداشت‌ها و توضیحات اضافی درباره مشتری"
    )
    
    # 💼 کد اقتصادی خریدار (فیلد جدید)
    economic_code = models.CharField(
        "💼 کد اقتصادی خریدار", 
        max_length=15, 
        blank=True, 
        null=True,
        help_text="کد اقتصادی شرکت یا کسب‌وکار مشتری برای صدور فاکتور رسمی"
    )
    
    # 📮 کد پستی خریدار (فیلد جدید)
    postcode = models.CharField(
        "📮 کد پستی خریدار", 
        max_length=10, 
        blank=True, 
        null=True,
        help_text="کد پستی ده رقمی آدرس مشتری"
    )
    
    # 🆔 شناسه ملی خریدار (فیلد جدید)
    national_id = models.CharField(
        "🆔 شناسه ملی خریدار", 
        max_length=50, 
        blank=True, 
        null=True,
        help_text="شناسه ملی (اشخاص حقیقی) یا شناسه اقتصادی (اشخاص حقوقی)"
    )
    
    # 📝 لاگ‌های تحلیلی
    logs = models.TextField(
        blank=True,
        default='',
        verbose_name="📝 لاگ‌ها",
        help_text="لاگ‌های تحلیلی برای تیم آنالیتیکس (append only)"
    )
    
    class Meta:
        verbose_name = "👤 مشتری"
        verbose_name_plural = "👥 مشتریان"
        ordering = ['-created_at']  # 📅 مرتب‌سازی بر اساس تاریخ ایجاد (جدیدترین ابتدا)
        
        # 📇 ایندکس‌های پایگاه داده برای بهبود عملکرد
        indexes = [
            models.Index(fields=['customer_name']),   # 🔍 جستجوی سریع بر اساس نام
            models.Index(fields=['phone']),           # 📞 جستجوی سریع بر اساس تلفن
            models.Index(fields=['national_id']),     # 🆔 جستجوی سریع بر اساس شناسه ملی
            models.Index(fields=['status']),          # 📊 فیلتر بر اساس وضعیت
        ]
        
        # 🚫 جلوگیری از تکرار نام مشتری
        constraints = [
            models.UniqueConstraint(
                fields=['customer_name'],
                name='unique_customer_name',
                violation_error_message='👤 مشتری با این نام قبلاً ثبت شده است'
            ),
        ]
    
    def clean(self):
        """
        🧹 اعتبارسنجی داده‌های مدل قبل از ذخیره
        ✅ بررسی صحت کد پستی، شناسه ملی و سایر فیلدها
        """
        from django.core.exceptions import ValidationError
        
        # 📮 بررسی طول کد پستی
        if self.postcode and len(self.postcode) != 10:
            raise ValidationError({
                'postcode': '📮 کد پستی باید دقیقاً 10 رقم باشد'
            })
        
        # 🆔 بررسی طول شناسه ملی (برای اشخاص حقیقی)
        if self.national_id and len(self.national_id) == 10:
            # اعتبارسنجی کد ملی ایرانی می‌تواند در آینده اضافه شود
            pass
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای مشتری
        """
        return f"👤 {self.customer_name}"
    
    def get_full_address(self):
        """
        🏠 دریافت آدرس کامل شامل کد پستی
        📍 ترکیب آدرس و کد پستی برای نمایش کامل
        """
        if self.address and self.postcode:
            return f"{self.address} - کد پستی: {self.postcode}"
        elif self.address:
            return self.address
        else:
            return "❌ آدرس ثبت نشده"
    
    def is_active(self):
        """
        ✅ بررسی فعال بودن مشتری
        🔍 بررسی وضعیت مشتری برای عملیات‌های کسب‌وکار
        """
        if not self.status:
            return False
        return self.status.lower() == 'active'
    
    def get_contact_info(self):
        """
        📞 دریافت اطلاعات تماس کامل
        📋 ترکیب تلفن و آدرس برای نمایش سریع
        """
        contact_parts = []
        if self.phone:
            contact_parts.append(f"📞 {self.phone}")
        if self.address:
            contact_parts.append(f"🏠 {self.address}")
        
        return " | ".join(contact_parts) if contact_parts else "❌ اطلاعات تماس ناقص"

    def save(self, *args, **kwargs):
        from core.models import ActivityLog
        current_user = get_current_user()
        username = None
        if current_user and hasattr(current_user, 'get_full_name'):
            username = current_user.get_full_name() or current_user.username
        elif current_user and hasattr(current_user, 'username'):
            username = current_user.username
        else:
            username = 'system'
        is_new = not self.pk
        now_str = timezone.now().strftime('%Y-%m-%d %H:%M')
        log_entries = []
        if self.logs:
            log_entries = [entry.strip() for entry in self.logs.split(',') if entry.strip()]
        if is_new:
            # Creation log (English only)
            log_entries.append(f"{now_str} Created By {username}")
            if self.comments:
                log_entries.append(f"{now_str} {self.comments} By {username} FOR comments")
        else:
            try:
                old = Customer.objects.get(pk=self.pk)
            except Customer.DoesNotExist:
                old = None
            # Update log
            log_entries.append(f"{now_str} Updated By {username}")
            # Check for changed fields (e.g., comments)
            if old:
                if old.comments != self.comments:
                    log_entries.append(f"{now_str} {self.comments} By {username} FOR comments")
                if old.status != self.status:
                    log_entries.append(f"{now_str} Updated By {username} FOR status: {self.status}")
        # Sort logs chronologically (oldest first)
        log_entries = sorted(log_entries, key=lambda x: x[:16])
        self.logs = ', '.join(log_entries) + (',' if log_entries else '')
        super().save(*args, **kwargs)
        # Export logs to CSV after each save
        try:
            call_command('export_logs_to_csv')
        except Exception:
            pass
        # ActivityLog (optional, can be removed if not needed)
        # Only log if current_user is a valid authenticated User instance
        user_for_log = None
        if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_for_log = current_user
        
        if is_new:
            ActivityLog.log_activity(
                user=user_for_log,
                action='CREATE',
                description=f'Customer created: {self.customer_name} - {self.phone}',
                content_object=self,
                severity='MEDIUM',
                extra_data={
                    'customer_id': self.id,
                    'customer_name': self.customer_name,
                    'phone': self.phone,
                    'status': self.status,
                    'address': self.address,
                    'economic_code': self.economic_code,
                    'national_id': self.national_id
                }
            )
        else:
            ActivityLog.log_activity(
                user=user_for_log,
                action='UPDATE',
                description=f'Customer updated: {self.customer_name}',
                content_object=self,
                severity='MEDIUM',
                extra_data={
                    'customer_id': self.id,
                    'customer_name': self.customer_name,
                }
            )

    def delete(self, *args, **kwargs):
        from core.models import ActivityLog
        current_user = get_current_user()
        user_for_log = current_user if current_user and hasattr(current_user, 'username') else None
        ActivityLog.log_activity(
            user=user_for_log,
            action='DELETE',
            description=f'🗑️ مشتری حذف شد: {self.customer_name} - {self.phone}',
            content_object=self,
            severity='HIGH',
            extra_data={
                'customer_id': self.id,
                'customer_name': self.customer_name,
                'phone': self.phone,
                'status': self.status,
                'address': self.address,
                'economic_code': self.economic_code,
                'national_id': self.national_id
            }
        )
        super().delete(*args, **kwargs)


class Product(BaseModel):
    """
    📦 مدل محصولات - اطلاعات کامل محصولات انبار
    
    🎯 این مدل برای ذخیره اطلاعات محصولات کاغذی و مشخصات فنی آن‌ها استفاده می‌شود
    📋 شامل مکان انبار، ابعاد، وزن، کیفیت و وضعیت محصول
    ⏰ دارای فیلدهای created_at و updated_at از BaseModel
    
    🔧 استفاده:
        product = Product.objects.create(
            reel_number="R001",
            location="Anbar_Akhal",
            width=100,
            gsm=80,
            length=1000
        )
    """
    
    # 📍 گزینه‌های مکان انبار
    LOCATION_CHOICES = [
        ('Anbar_Akhal', '📍 انبار آخال'),
        ('Anbar_Muhvateh_Kordan', '📍 انبار محوطه کردان'),
        ('Anbar_Khamir_Kordan', '📍 انبار کردان'),
        ('Anbar_Khamir_Ghadim', '📍 انبار خمیر قدیم'),
        ('Anbar_Koochak', '📍 انبار کوچک'),
        ('Anbar_Salon_Tolid', '📍 انبار سالن تولید'),
        ('Anbar_Sangin', '📍 انبار سنگین'),
    ]
    
    # 📊 وضعیت محصول
    STATUS_CHOICES = [
        ('In-stock', '📦 موجود در انبار'),
        ('Sold', '💰 فروخته شده'),
        ('Pre-order', '⏳ پیش‌سفارش'),
    ]
    

    
    # 📍 مکان انبار محصول
    location = models.CharField(
        max_length=255,
        choices=LOCATION_CHOICES,
        verbose_name="📍 مکان انبار",
        help_text="انبار محل نگهداری محصول"
    )
    
    # 📊 وضعیت محصول
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='In-stock',
        verbose_name="📊 وضعیت محصول",
        help_text="وضعیت فعلی محصول در سیستم"
    )
    

    
    # 🏷️ شماره ریل محصول (یکتا)
    reel_number = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="🏷️ شماره ریل",
        help_text="شماره یکتای ریل محصول"
    )
    
    # 📏 عرض محصول (میلی‌متر)
    width = models.IntegerField(
        verbose_name="📏 عرض (mm)",
        help_text="عرض محصول به میلی‌متر"
    )
    
    # ⚖️ GSM (گرم بر متر مربع)
    gsm = models.IntegerField(
        verbose_name="⚖️ GSM (g/m²)",
        help_text="وزن محصول به گرم بر متر مربع"
    )
    
    # 📐 طول محصول (متر)
    length = models.IntegerField(
        verbose_name="📐 طول (m)",
        help_text="طول محصول به متر"
    )
    
    # 🏆 درجه کیفیت محصول
    grade = models.CharField(
        max_length=255,
        verbose_name="🏆 درجه کیفیت",
        help_text="درجه و کیفیت محصول"
    )
    
    # 💔 تعداد شکستگی‌ها
    breaks = models.IntegerField(
        default=0,
        verbose_name="💔 تعداد شکستگی",
        help_text="تعداد شکستگی‌های موجود در محصول"
    )
    
    # 📱 کد QR محصول
    qr_code = models.TextField(
        null=True,
        blank=True,
        verbose_name="📱 کد QR",
        help_text="کد QR مرتبط با محصول برای ردیابی سریع"
    )
    
    # 💰 قیمت محصول (فقط Super Admin می‌تواند تغییر دهد)
    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="💰 قیمت (تومان)",
        help_text="قیمت محصول به تومان - فقط Super Admin می‌تواند تغییر دهد"
    )
    
    # 📅 تاریخ آخرین تغییر قیمت
    price_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="📅 آخرین تغییر قیمت",
        help_text="زمان آخرین تغییر قیمت توسط Super Admin"
    )
    
    # 👤 کاربری که آخرین بار قیمت را تغییر داده
    price_updated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_product_prices',
        verbose_name="👤 تغییر قیمت توسط",
        help_text="کاربری که آخرین بار قیمت را تغییر داده است"
    )
    
    class Meta:
        verbose_name = "📦 محصول"
        verbose_name_plural = "📦 محصولات"
        db_table = 'Products'
        ordering = ['-created_at']  # 📅 مرتب‌سازی بر اساس تاریخ ایجاد (جدیدترین ابتدا)
        
        # 📇 ایندکس‌های پایگاه داده برای بهبود عملکرد
        indexes = [
            models.Index(fields=['reel_number']),     # 🔍 جستجوی سریع بر اساس شماره ریل
            models.Index(fields=['location']),        # 📍 فیلتر بر اساس مکان انبار
            models.Index(fields=['status']),          # 📊 فیلتر بر اساس وضعیت
            models.Index(fields=['width', 'gsm']),    # 📏 جستجوی ترکیبی ابعاد
        ]
    
    def clean(self):
        """
        🧹 اعتبارسنجی داده‌های محصول قبل از ذخیره
        ✅ بررسی صحت ابعاد، وزن و سایر مشخصات فنی
        """
        from django.core.exceptions import ValidationError
        
        # 📏 بررسی عرض مثبت بودن
        if self.width <= 0:
            raise ValidationError({
                'width': '📏 عرض محصول باید بیشتر از صفر باشد'
            })
        
        # ⚖️ بررسی GSM مثبت بودن
        if self.gsm <= 0:
            raise ValidationError({
                'gsm': '⚖️ وزن GSM باید بیشتر از صفر باشد'
            })
        
        # 📐 بررسی طول مثبت بودن
        if self.length <= 0:
            raise ValidationError({
                'length': '📐 طول محصول باید بیشتر از صفر باشد'
            })
        
        # 💔 بررسی تعداد شکستگی منفی نباشد
        if self.breaks < 0:
            raise ValidationError({
                'breaks': '💔 تعداد شکستگی نمی‌تواند منفی باشد'
            })
        
        # 💰 بررسی قیمت منفی نباشد
        if self.price < 0:
            raise ValidationError({
                'price': '💰 قیمت محصول نمی‌تواند منفی باشد'
            })
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای محصول
        """
        return f"📦 {self.reel_number} - {self.get_location_display()} - {self.get_status_display()}"
    
    def get_total_area(self):
        """
        📐 محاسبه مساحت کل محصول
        📏 محاسبه مساحت بر اساس عرض و طول
        """
        return (Decimal(self.width) / Decimal('1000')) * Decimal(self.length)  # تبدیل میلی‌متر به متر
    
    def get_total_weight(self):
        """
        ⚖️ محاسبه وزن کل محصول
        🧮 محاسبه وزن بر اساس مساحت و GSM
        """
        return self.get_total_area() * Decimal(self.gsm) / Decimal('1000')  # تبدیل گرم به کیلوگرم
    
    def is_available(self):
        """
        ✅ بررسی در دسترس بودن محصول
        🔍 بررسی وضعیت محصول برای فروش
        """
        return self.status == 'In-stock'
    
    def get_product_info(self):
        """
        📋 دریافت اطلاعات کامل محصول
        📊 خلاصه کامل مشخصات فنی محصول
        """
        return {
            'reel_number': self.reel_number,
            'location': self.get_location_display(),
            'dimensions': f"{self.width}mm × {self.length}m",
            'gsm': f"{self.gsm} g/m²",
            'grade': self.grade,
            'total_area': f"{self.get_total_area():.2f} m²",
            'total_weight': f"{self.get_total_weight():.2f} kg",
            'breaks': self.breaks,
            'status': self.get_status_display(),
            'price': f"{self.price:,.0f} تومان",
            'price_per_kg': f"{(self.price / self.get_total_weight() if self.get_total_weight() > 0 else 0):,.0f} تومان/کیلو",
            'price_updated_at': self.price_updated_at.strftime('%Y/%m/%d %H:%M') if self.price_updated_at else 'تعیین نشده',
            'price_updated_by': str(self.price_updated_by) if self.price_updated_by else 'تعیین نشده'
        }
    
    def get_total_value(self):
        """
        💰 محاسبه ارزش کل محصول
        💵 قیمت کل بر اساس قیمت واحد
        """
        return self.price
    
    def get_price_per_unit_area(self):
        """
        💰 محاسبه قیمت بر متر مربع
        📐 قیمت تقسیم بر مساحت کل
        """
        total_area = self.get_total_area()
        if total_area > 0:
            return self.price / total_area
        return 0
    
    def get_price_per_unit_weight(self):
        """
        💰 محاسبه قیمت بر کیلوگرم
        ⚖️ قیمت تقسیم بر وزن کل
        """
        total_weight = self.get_total_weight()
        if total_weight > 0:
            return self.price / total_weight
        return 0

    def save(self, *args, **kwargs):
        from core.models import ActivityLog
        current_user = get_current_user()
        user_for_log = current_user if current_user and hasattr(current_user, 'username') else None
        is_new = not self.pk
        if not is_new:
            try:
                old = Product.objects.get(pk=self.pk)
                old_data = {
                    'price': old.price,
                    'status': old.status,
                    'location': old.location,
                }
            except Product.DoesNotExist:
                old_data = None
        else:
            old_data = None
        super().save(*args, **kwargs)
        # Always log
        if is_new:
            ActivityLog.log_activity(
                user=user_for_log,
                action='CREATE',
                description=f'📦 محصول جدید ایجاد شد: {self.reel_number} - {self.get_product_info()}',
                content_object=self,
                severity='MEDIUM',
                extra_data={
                    'product_id': self.id,
                    'reel_number': self.reel_number,
                    'location': self.location,
                    'status': self.status,
                    'price': str(self.price),
                    'dimensions': f'{self.width}mm × {self.length}m',
                    'gsm': self.gsm,
                    'grade': self.grade
                }
            )
        else:
            changes = []
            if old_data:
                for field, old_val in old_data.items():
                    new_val = getattr(self, field)
                    if old_val != new_val:
                        changes.append(f'{field}: {old_val} → {new_val}')
            ActivityLog.log_activity(
                user=user_for_log,
                action='UPDATE',
                description=f'📝 محصول ویرایش شد: {self.reel_number} - تغییرات: {", ".join(changes) if changes else "بدون تغییر مهم"}',
                content_object=self,
                severity='MEDIUM',
                extra_data={
                    'product_id': self.id,
                    'reel_number': self.reel_number,
                    'changes': changes,
                }
            )

    def delete(self, *args, **kwargs):
        from core.models import ActivityLog
        current_user = get_current_user()
        user_for_log = current_user if current_user and hasattr(current_user, 'username') else None
        ActivityLog.log_activity(
            user=user_for_log,
            action='DELETE',
            description=f'🗑️ محصول حذف شد: {self.reel_number} - {self.get_product_info()}',
            content_object=self,
            severity='HIGH',
            extra_data={
                'product_id': self.id,
                'reel_number': self.reel_number,
                'location': self.location,
                'status': self.status,
                'price': str(self.price),
                'dimensions': f'{self.width}mm × {self.length}m',
                'gsm': self.gsm,
                'grade': self.grade
            }
        )
        super().delete(*args, **kwargs)


class ActivityLog(BaseModel):
    """
    📜 مدل لاگ فعالیت‌ها - ثبت تمام تغییرات و فعالیت‌های سیستم
    
    🎯 این مدل برای ردیابی و ثبت تمام فعالیت‌های کاربران و تغییرات داده‌ها استفاده می‌شود
    📋 با استفاده از GenericForeignKey می‌تواند به هر مدلی متصل شود
    ⏰ دارای فیلدهای created_at و updated_at از BaseModel
    
    🔧 استفاده:
        ActivityLog.objects.create(
            user=request.user,
            action='CREATE',
            content_object=product,
            description='محصول جدید ایجاد شد'
        )
    """
    
    # 🎭 انواع عملیات قابل ثبت
    ACTION_CHOICES = [
        ('CREATE', '✅ ایجاد'),
        ('UPDATE', '📝 ویرایش'),
        ('DELETE', '🗑️ حذف'),
        ('VIEW', '👁️ مشاهده'),
        ('LOGIN', '🔑 ورود'),
        ('LOGOUT', '🚪 خروج'),
        ('EXPORT', '📤 خروجی'),
        ('IMPORT', '📥 ورودی'),
        ('APPROVE', '✅ تایید'),
        ('REJECT', '❌ رد'),
        ('PAYMENT', '💰 پرداخت'),
        ('ORDER', '🛒 سفارش'),
        ('DELIVERY', '🚚 تحویل'),
        ('CANCEL', '🚫 لغو'),
        ('RESTORE', '♻️ بازگردانی'),
        ('BACKUP', '💾 پشتیبان‌گیری'),
        ('PRICE_UPDATE', '💰 تغییر قیمت'),
        ('ERROR', '⚠️ خطا'),
        ('WARNING', '⚡ هشدار'),
        ('INFO', 'ℹ️ اطلاعات'),
    ]
    
    # 👤 کاربر انجام‌دهنده عملیات
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="👤 کاربر",
        help_text="کاربری که این عملیات را انجام داده است"
    )
    
    # 🎭 نوع عملیات انجام شده
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="🎭 نوع عملیات",
        help_text="نوع عملیات انجام شده توسط کاربر"
    )
    
    # 📝 توضیحات عملیات
    description = models.TextField(
        verbose_name="📝 توضیحات",
        help_text="توضیحات کامل عملیات انجام شده"
    )
    
    # 🌐 آدرس IP کاربر
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="🌐 آدرس IP",
        help_text="آدرس IP کاربر در زمان انجام عملیات"
    )
    
    # 🖥️ اطلاعات مرورگر
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="🖥️ اطلاعات مرورگر",
        help_text="اطلاعات مرورگر و سیستم‌عامل کاربر"
    )
    
    # 📄 اطلاعات اضافی (JSON)
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="📄 اطلاعات اضافی",
        help_text="اطلاعات اضافی مرتبط با عملیات (JSON format)"
    )
    
    # 🔗 ارتباط عمومی با سایر مدل‌ها
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="🔗 نوع محتوا"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="🆔 شناسه آبجکت"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # ⚠️ سطح اهمیت لاگ
    SEVERITY_CHOICES = [
        ('LOW', '🟢 کم'),
        ('MEDIUM', '🟡 متوسط'),
        ('HIGH', '🟠 بالا'),
        ('CRITICAL', '🔴 بحرانی'),
    ]
    
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='LOW',
        verbose_name="⚠️ سطح اهمیت",
        help_text="سطح اهمیت این لاگ"
    )
    
    class Meta:
        verbose_name = "📜 لاگ فعالیت"
        verbose_name_plural = "📜 لاگ‌های فعالیت"
        ordering = ['-created_at']  # 📅 مرتب‌سازی بر اساس تاریخ (جدیدترین ابتدا)
        
        # 📇 ایندکس‌های پایگاه داده برای بهبود عملکرد
        indexes = [
            models.Index(fields=['user', 'action']),      # 🔍 جستجوی بر اساس کاربر و عملیات
            models.Index(fields=['action', 'severity']),  # 📊 فیلتر بر اساس نوع و اهمیت
            models.Index(fields=['created_at']),          # ⏰ مرتب‌سازی زمانی
            models.Index(fields=['content_type', 'object_id']),  # 🔗 ارتباط با آبجکت‌ها
        ]
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای لاگ فعالیت
        """
        user_display = self.user.username if self.user else "سیستم"
        return f"📜 {user_display} - {self.get_action_display()} - {self.created_at.strftime('%Y/%m/%d %H:%M')}"
    
    def get_related_object_info(self):
        """
        �� دریافت اطلاعات آبجکت مرتبط
        📋 اطلاعات آبجکتی که این لاگ مربوط به آن است
        """
        if self.content_object:
            return {
                'model': self.content_type.model,
                'object_id': self.object_id,
                'object_str': str(self.content_object)
            }
        return None
    
    @classmethod
    def log_activity(cls, user, action, description, content_object=None, 
                    severity='LOW', ip_address=None, user_agent=None, **extra_data):
        """
        📝 متد کمکی برای ثبت سریع لاگ فعالیت
        
        🔧 استفاده:
            ActivityLog.log_activity(
                user=request.user,
                action='CREATE',
                description='محصول جدید ایجاد شد',
                content_object=product,
                severity='MEDIUM',
                width=100,
                gsm=80
            )
        """
        # Validate user parameter to prevent AnonymousUser errors
        if user and not hasattr(user, 'is_authenticated'):
            user = None  # Convert invalid user objects to None
        elif user and hasattr(user, 'is_authenticated') and not user.is_authenticated:
            user = None  # Convert anonymous users to None
        
        return cls.objects.create(
            user=user,
            action=action,
            description=description,
            content_object=content_object,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )
    
    def get_action_icon(self):
        """
        🎭 دریافت آیکون مناسب برای نوع عملیات
        """
        action_icons = {
            'CREATE': '✅',
            'UPDATE': '📝',
            'DELETE': '🗑️',
            'VIEW': '👁️',
            'LOGIN': '🔑',
            'LOGOUT': '🚪',
            'EXPORT': '📤',
            'IMPORT': '📥',
            'APPROVE': '✅',
            'REJECT': '❌',
            'PAYMENT': '💰',
            'ORDER': '🛒',
            'DELIVERY': '🚚',
            'CANCEL': '🚫',
            'RESTORE': '♻️',
            'BACKUP': '💾',
            'ERROR': '⚠️',
            'WARNING': '⚡',
            'INFO': 'ℹ️',
        }
        return action_icons.get(self.action, '📋')
    
    def get_severity_color(self):
        """
        🎨 دریافت رنگ مناسب برای سطح اهمیت
        """
        severity_colors = {
            'LOW': 'green',
            'MEDIUM': 'yellow',
            'HIGH': 'orange',
            'CRITICAL': 'red'
        }
        return severity_colors.get(self.severity, 'gray')


class Order(BaseModel):
    """
    🛒 مدل سفارش - مدیریت سفارشات مشتریان
    
    🎯 این مدل برای ذخیره سفارشات مشتریان و مدیریت فرآیند خرید استفاده می‌شود
    📋 شامل اطلاعات مشتری، محصولات، قیمت‌ها و وضعیت سفارش
    ⏰ دارای فیلدهای created_at و updated_at از BaseModel
    
    🔧 استفاده:
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',
            status='Pending'
        )
    """
    
    # 📊 وضعیت سفارش
    ORDER_STATUS_CHOICES = [
        ('Pending', '⏳ در انتظار تایید'),
        ('Confirmed', '✅ تایید شده'),
        ('Processing', '🔄 در حال پردازش'),
        ('Ready', '📦 آماده تحویل'),
        ('Delivered', '🚚 تحویل داده شده'),
        ('Cancelled', '❌ لغو شده'),
        ('Returned', '↩️ مرجوع شده'),
    ]
    
    # 💳 روش پرداخت
    PAYMENT_METHOD_CHOICES = [
        ('Cash', '💵 نقدی'),
        ('Terms', '📅 قسطی'),
        ('Bank_Transfer', '🏦 حواله بانکی'),
        ('Check', '📝 چک'),
    ]
    
    # 👤 مشتری سفارش‌دهنده
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        verbose_name="👤 مشتری",
        help_text="مشتری سفارش‌دهنده"
    )
    
    # 🏷️ شماره سفارش (یکتا)
    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="🏷️ شماره سفارش",
        help_text="شماره یکتای سفارش"
    )
    
    # 📊 وضعیت سفارش
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='Pending',
        verbose_name="📊 وضعیت سفارش",
        help_text="وضعیت فعلی سفارش"
    )
    
    # 💳 روش پرداخت
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="💳 روش پرداخت",
        help_text="روش پرداخت انتخاب شده توسط مشتری"
    )
    
    # 💰 مبلغ کل سفارش
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="💰 مبلغ کل (تومان)",
        help_text="مبلغ کل سفارش به تومان"
    )
    
    # 🎯 تخفیف (درصد)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="🎯 تخفیف (%)",
        help_text="درصد تخفیف اعمال شده"
    )
    
    # 💸 مبلغ تخفیف
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="💸 مبلغ تخفیف (تومان)",
        help_text="مبلغ تخفیف به تومان"
    )
    
    # 💵 مبلغ نهایی (پس از تخفیف)
    final_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="💵 مبلغ نهایی (تومان)",
        help_text="مبلغ نهایی پس از اعمال تخفیف"
    )
    
    # 📝 توضیحات سفارش
    notes = models.TextField(
        blank=True,
        verbose_name="📝 توضیحات",
        help_text="توضیحات و یادداشت‌های مربوط به سفارش"
    )
    
    # 🚚 آدرس تحویل
    delivery_address = models.TextField(
        blank=True,
        verbose_name="🚚 آدرس تحویل",
        help_text="آدرس تحویل سفارش (در صورت تفاوت با آدرس مشتری)"
    )
    
    # 📅 تاریخ تحویل مورد انتظار
    expected_delivery_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="📅 تاریخ تحویل مورد انتظار",
        help_text="تاریخ تحویل مورد انتظار سفارش"
    )
    
    # 📅 تاریخ تحویل واقعی
    actual_delivery_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="📅 تاریخ تحویل واقعی",
        help_text="تاریخ تحویل واقعی سفارش"
    )
    
    # 👤 کاربر ایجادکننده سفارش
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_orders',
        verbose_name="👤 ایجادکننده",
        help_text="کاربری که سفارش را ایجاد کرده است"
    )
    
    # 📝 لاگ‌های تحلیلی
    logs = models.TextField(
        blank=True,
        default='',
        verbose_name="📝 لاگ‌ها",
        help_text="لاگ‌های تحلیلی برای تیم آنالیتیکس (append only)"
    )
    
    class Meta:
        verbose_name = "🛒 سفارش"
        verbose_name_plural = "🛒 سفارشات"
        ordering = ['-created_at']  # 📅 مرتب‌سازی بر اساس تاریخ ایجاد (جدیدترین ابتدا)
        
        # 📇 ایندکس‌های پایگاه داده برای بهبود عملکرد
        indexes = [
            models.Index(fields=['order_number']),        # 🔍 جستجوی سریع بر اساس شماره سفارش
            models.Index(fields=['customer', 'status']),  # 📊 فیلتر بر اساس مشتری و وضعیت
            models.Index(fields=['status']),              # 📊 فیلتر بر اساس وضعیت
            models.Index(fields=['payment_method']),      # 💳 فیلتر بر اساس روش پرداخت
            models.Index(fields=['created_at']),          # ⏰ مرتب‌سازی زمانی
        ]
    
    def save(self, *args, **kwargs):
        # Ensure unique order_number is set before saving
        if not self.order_number:
            self.order_number = self.generate_order_number()
        from core.models import ActivityLog
        from django.core.management import call_command
        current_user = get_current_user()
        username = None
        if current_user and hasattr(current_user, 'get_full_name'):
            username = current_user.get_full_name() or current_user.username
        elif current_user and hasattr(current_user, 'username'):
            username = current_user.username
        else:
            username = 'system'
        is_new = not self.pk
        now_str = timezone.now().strftime('%Y-%m-%d %H:%M')
        log_entries = []
        if self.logs:
            log_entries = [entry.strip() for entry in self.logs.split(',') if entry.strip()]
        if is_new:
            # Creation log (English only)
            log_entries.append(f"{now_str} Created By {username}")
            log_entries.append(f"{now_str} Status: {self.status} By {username}")
        else:
            try:
                old = Order.objects.get(pk=self.pk)
            except Order.DoesNotExist:
                old = None
            # Update log
            log_entries.append(f"{now_str} Updated By {username}")
            # Check for changed fields
            if old:
                if old.status != self.status:
                    log_entries.append(f"{now_str} Status changed to {self.status} By {username}")
                if old.payment_method != self.payment_method:
                    log_entries.append(f"{now_str} Payment method changed to {self.payment_method} By {username}")
                if old.final_amount != self.final_amount:
                    log_entries.append(f"{now_str} Final amount changed to {self.final_amount} By {username}")
        # Sort logs chronologically (oldest first)
        log_entries = sorted(log_entries, key=lambda x: x[:16])
        self.logs = ', '.join(log_entries) + (',' if log_entries else '')
        super().save(*args, **kwargs)
        # Export logs to CSV after each save
        try:
            call_command('export_logs_to_csv')
        except Exception:
            pass
        # ActivityLog (optional, can be removed if not needed)
        if is_new:
            ActivityLog.log_activity(
                user=current_user,
                action='CREATE',
                description=f'Order created: {self.order_number} - {self.customer.customer_name}',
                content_object=self,
                severity='HIGH',
                extra_data={
                    'order_id': self.id,
                    'order_number': self.order_number,
                    'customer_name': self.customer.customer_name,
                    'status': self.status,
                    'payment_method': self.payment_method,
                    'total_amount': str(self.total_amount),
                    'final_amount': str(self.final_amount),
                    'discount_percentage': str(self.discount_percentage),
                    'items_count': self.get_order_items_count()
                }
            )
        else:
            ActivityLog.log_activity(
                user=current_user,
                action='UPDATE',
                description=f'Order updated: {self.order_number}',
                content_object=self,
                severity='HIGH',
                extra_data={
                    'order_id': self.id,
                    'order_number': self.order_number,
                    'customer_name': self.customer.customer_name,
                }
            )
    
    def generate_order_number(self):
        """
        🏷️ تولید شماره یکتای سفارش
        📋 فرمت: ORD-YYYYMMDD-XXXX
        """
        import random
        import string
        
        today = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # Try to generate a unique order number
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            order_number = f"ORD-{today}-{random_part}"
            if not Order.objects.filter(order_number=order_number).exists():
                return order_number
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            attempt += 1
        
        # If we couldn't generate a unique number after max_attempts, add a timestamp
        timestamp = timezone.now().strftime('%H%M%S')
        return f"ORD-{today}-{timestamp}"

    def calculate_final_amount(self):
        """
        💰 محاسبه مبلغ نهایی سفارش
        🧮 محاسبه تخفیف و مبلغ نهایی
        """
        # محاسبه مبلغ تخفیف
        if self.discount_percentage > 0:
            self.discount_amount = (self.total_amount * self.discount_percentage) / 100
        else:
            self.discount_amount = 0
        
        # محاسبه مبلغ نهایی
        self.final_amount = self.total_amount - self.discount_amount
    
    def clean(self):
        """
        🧹 اعتبارسنجی داده‌های سفارش
        """
        from django.core.exceptions import ValidationError
        
        # بررسی مثبت بودن مبالغ
        if self.total_amount < 0:
            raise ValidationError({
                'total_amount': '💰 مبلغ کل نمی‌تواند منفی باشد'
            })
        
        if self.discount_percentage < 0 or self.discount_percentage > 100:
            raise ValidationError({
                'discount_percentage': '🎯 درصد تخفیف باید بین 0 تا 100 باشد'
            })
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای سفارش
        """
        return f"🛒 {self.order_number} - {self.customer.customer_name} - {self.get_status_display()}"
    
    def get_order_items_count(self):
        """
        📊 تعداد اقلام سفارش
        """
        return self.order_items.count()
    
    def get_total_weight(self):
        """
        ⚖️ محاسبه وزن کل سفارش
        """
        total_weight = 0
        for item in self.order_items.all():
            total_weight += item.get_total_weight()
        return total_weight
    
    def get_order_summary(self):
        """
        📋 خلاصه اطلاعات سفارش
        """
        return {
            'order_number': self.order_number,
            'customer': self.customer.customer_name,
            'status': self.get_status_display(),
            'payment_method': self.get_payment_method_display(),
            'items_count': self.get_order_items_count(),
            'total_amount': f"{self.total_amount:,.0f} تومان",
            'discount': f"{self.discount_percentage}% ({self.discount_amount:,.0f} تومان)",
            'final_amount': f"{self.final_amount:,.0f} تومان",
            'total_weight': f"{self.get_total_weight():.2f} کیلوگرم",
            'created_at': self.created_at.strftime('%Y/%m/%d %H:%M'),
        }
    
    def can_be_cancelled(self):
        """
        ❌ بررسی امکان لغو سفارش
        """
        return self.status in ['Pending', 'Confirmed']
    
    def can_be_modified(self):
        """
        📝 بررسی امکان ویرایش سفارش
        """
        return self.status == 'Pending'

    def delete(self, *args, **kwargs):
        from core.models import ActivityLog
        current_user = get_current_user()
        user_for_log = current_user if current_user and hasattr(current_user, 'username') else None
        ActivityLog.log_activity(
            user=user_for_log,
            action='DELETE',
            description=f'🗑️ سفارش حذف شد: {self.order_number} - مشتری: {self.customer.customer_name} - مبلغ: {self.final_amount:,.0f} تومان',
            content_object=self,
            severity='CRITICAL',
            extra_data={
                'order_id': self.id,
                'order_number': self.order_number,
                'customer_name': self.customer.customer_name,
                'status': self.status,
                'payment_method': self.payment_method,
                'total_amount': str(self.total_amount),
                'final_amount': str(self.final_amount),
                'discount_percentage': str(self.discount_percentage),
                'items_count': self.get_order_items_count()
            }
        )
        super().delete(*args, **kwargs)


class OrderItem(BaseModel):
    """
    📦 مدل آیتم سفارش - اقلام داخل هر سفارش
    
    🎯 این مدل برای ذخیره جزئیات محصولات داخل هر سفارش استفاده می‌شود
    📋 شامل محصول، تعداد، قیمت واحد، قیمت کل و نوع پرداخت
    ⏰ دارای فیلدهای created_at و updated_at از BaseModel
    """
    
    # 💳 روش پرداخت برای این آیتم
    PAYMENT_METHOD_CHOICES = [
        ('Cash', '💵 نقدی'),
        ('Terms', '📅 قسطی'),
        ('Bank_Transfer', '🏦 حواله بانکی'),
        ('Check', '📝 چک'),
    ]
    
    # 🛒 سفارش مربوطه
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="🛒 سفارش",
        help_text="سفارش مربوط به این آیتم"
    )
    
    # 📦 محصول
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="📦 محصول",
        help_text="محصول انتخاب شده"
    )
    
    # 🔢 تعداد
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="🔢 تعداد",
        help_text="تعداد محصول درخواستی"
    )
    
    # 💰 قیمت واحد (در زمان سفارش)
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="💰 قیمت واحد (تومان)",
        help_text="قیمت واحد محصول در زمان سفارش"
    )
    
    # 💵 قیمت کل
    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="💵 قیمت کل (تومان)",
        help_text="قیمت کل این آیتم (تعداد × قیمت واحد)"
    )
    
    # 💳 نوع پرداخت این آیتم
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='Cash',
        verbose_name="💳 نوع پرداخت",
        help_text="نوع پرداخت انتخابی برای این محصول"
    )
    
    # 📝 توضیحات آیتم
    notes = models.TextField(
        blank=True,
        verbose_name="📝 توضیحات",
        help_text="توضیحات خاص این آیتم"
    )
    
    class Meta:
        verbose_name = "📦 آیتم سفارش"
        verbose_name_plural = "📦 آیتم‌های سفارش"
        
        # 📇 ایندکس‌های پایگاه داده
        indexes = [
            models.Index(fields=['order', 'product']),  # 🔍 جستجوی ترکیبی
        ]
        
        # 🚫 جلوگیری از تکرار محصول در یک سفارش
        unique_together = ['order', 'product']
    
    def save(self, *args, **kwargs):
        from core.models import ActivityLog
        current_user = get_current_user()
        user_for_log = current_user if current_user and hasattr(current_user, 'username') else None
        is_new = not self.pk
        
        # Calculate total price before saving
        self.total_price = self.quantity * self.unit_price
        
        if not is_new:
            try:
                old = OrderItem.objects.get(pk=self.pk)
                old_data = {
                    'quantity': old.quantity,
                    'unit_price': old.unit_price,
                    'total_price': old.total_price,
                    'payment_method': old.payment_method,
                }
            except OrderItem.DoesNotExist:
                old_data = None
        else:
            old_data = None
            
        # Call the parent class's save method
        super().save(*args, **kwargs)
        
        # Update order's total amount
        self.order.total_amount = sum(item.total_price for item in self.order.order_items.all())
        self.order.save()
        
        # Always log
        if is_new:
            ActivityLog.log_activity(
                user=user_for_log,
                action='CREATE',
                description=f'📦 آیتم سفارش اضافه شد: {self.product.reel_number} × {self.quantity} - سفارش: {self.order.order_number}',
                content_object=self,
                severity='MEDIUM',
                extra_data={
                    'order_item_id': self.id,
                    'order_number': self.order.order_number,
                    'product_reel': self.product.reel_number,
                    'quantity': self.quantity,
                    'unit_price': str(self.unit_price),
                    'total_price': str(self.total_price),
                    'payment_method': self.payment_method,
                    'customer_name': self.order.customer.customer_name
                }
            )
        else:
            changes = []
            if old_data:
                for field, old_val in old_data.items():
                    new_val = getattr(self, field)
                    if old_val != new_val:
                        changes.append(f'{field}: {old_val} → {new_val}')
            ActivityLog.log_activity(
                user=user_for_log,
                action='UPDATE',
                description=f'📝 آیتم سفارش ویرایش شد: {self.product.reel_number} - سفارش: {self.order.order_number} - تغییرات: {", ".join(changes) if changes else "بدون تغییر مهم"}',
                content_object=self,
                severity='MEDIUM',
                extra_data={
                    'order_item_id': self.id,
                    'order_number': self.order.order_number,
                    'product_reel': self.product.reel_number,
                    'changes': changes,
                }
            )

    def delete(self, *args, **kwargs):
        from core.models import ActivityLog
        current_user = get_current_user()
        user_for_log = current_user if current_user and hasattr(current_user, 'username') else None
        ActivityLog.log_activity(
            user=user_for_log,
            action='DELETE',
            description=f'🗑️ آیتم سفارش حذف شد: {self.product.reel_number} × {self.quantity} - سفارش: {self.order.order_number}',
            content_object=self,
            severity='HIGH',
            extra_data={
                'order_item_id': self.id,
                'order_number': self.order.order_number,
                'product_reel': self.product.reel_number,
                'quantity': self.quantity,
                'unit_price': str(self.unit_price),
                'total_price': str(self.total_price),
                'payment_method': self.payment_method,
                'customer_name': self.order.customer.customer_name
            }
        )
        super().delete(*args, **kwargs)


class WorkingHours(BaseModel):
    """
    ⏰ مدل ساعات کاری - مدیریت زمان‌های فعالیت فروشگاه
    
    🎯 این مدل برای تنظیم ساعات کاری فروشگاه توسط Super Admin استفاده می‌شود
    ⏰ مشتریان فقط در ساعات تعریف شده می‌توانند خرید کنند
    👑 فقط Super Admin می‌تواند ساعات کاری را تغییر دهد
    
    🔧 استفاده:
        working_hours = WorkingHours.objects.create(
            start_time="09:00",
            end_time="18:00",
            is_active=True
        )
    """
    
    # ⏰ زمان شروع کار
    start_time = models.TimeField(
        verbose_name="⏰ زمان شروع کار",
        help_text="زمان شروع ساعات کاری (مثال: 09:00)",
        default="09:00"
    )
    
    # 🕐 زمان پایان کار
    end_time = models.TimeField(
        verbose_name="🕐 زمان پایان کار", 
        help_text="زمان پایان ساعات کاری (مثال: 18:00)",
        default="18:00"
    )
    
    # 📅 روزهای کاری
    WEEKDAY_CHOICES = [
        ('monday', '📅 دوشنبه'),
        ('tuesday', '📅 سه‌شنبه'),
        ('wednesday', '📅 چهارشنبه'),
        ('thursday', '📅 پنج‌شنبه'),
        ('friday', '📅 جمعه'),
        ('saturday', '📅 شنبه'),
        ('sunday', '📅 یکشنبه'),
    ]
    
    # 📝 توضیحات ساعات کاری
    description = models.TextField(
        blank=True,
        verbose_name="📝 توضیحات",
        help_text="توضیحات اضافی درباره ساعات کاری"
    )
    
    # ✅ وضعیت فعال/غیرفعال
    is_active = models.BooleanField(
        default=True,
        verbose_name="✅ فعال",
        help_text="آیا این ساعت کاری فعال است؟"
    )
    
    # 👑 کاربری که ساعات کاری را تنظیم کرده
    set_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='set_working_hours',
        verbose_name="👑 تنظیم‌کننده",
        help_text="کاربری که ساعات کاری را تنظیم کرده است"
    )
    
    class Meta:
        verbose_name = "⏰ ساعات کاری"
        verbose_name_plural = "⏰ ساعات کاری"
        ordering = ['-created_at']
        
        # 📇 ایندکس‌های پایگاه داده
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['start_time', 'end_time']),
        ]
    
    def clean(self):
        """
        🧹 اعتبارسنجی ساعات کاری
        """
        from django.core.exceptions import ValidationError
        
        # بررسی زمان شروع کمتر از زمان پایان باشد
        if self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': '⏰ زمان پایان کار باید بعد از زمان شروع کار باشد'
            })
    
    def save(self, *args, **kwargs):
        """
        💾 ذخیره ساعات کاری
        📋 اگر این ساعت کاری فعال می‌شود، بقیه را غیرفعال کن
        """
        if self.is_active:
            # غیرفعال کردن سایر ساعات کاری
            WorkingHours.objects.filter(is_active=True).update(is_active=False)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای ساعات کاری
        """
        status = "🟢 فعال" if self.is_active else "🔴 غیرفعال"
        return f"⏰ {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} ({status})"
    
    def get_duration_hours(self):
        """
        ⏱️ محاسبه مدت زمان کاری (ساعت)
        """
        from datetime import datetime, timedelta
        
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        
        # اگر زمان پایان از نیمه‌شب رد شود
        if end < start:
            end += timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600
    
    def is_currently_open(self):
        """
        🕐 بررسی باز بودن فروشگاه در زمان فعلی
        """
        if not self.is_active:
            return False
        
        import pytz
        
        # تنظیم timezone تهران
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = timezone.now().astimezone(tehran_tz)
        current_time = now.time()
        
        # بررسی آیا زمان فعلی در بازه ساعات کاری است
        if self.start_time <= self.end_time:
            # ساعات کاری در همان روز
            return self.start_time <= current_time <= self.end_time
        else:
            # ساعات کاری از نیمه‌شب رد می‌شود
            return current_time >= self.start_time or current_time <= self.end_time
    
    def time_until_open(self):
        """
        ⏰ محاسبه زمان باقی‌مانده تا باز شدن فروشگاه
        """
        if self.is_currently_open():
            return None
        
        import pytz
        from datetime import datetime, timedelta
        
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = timezone.now().astimezone(tehran_tz)
        
        # محاسبه زمان باز شدن در همین روز یا روز بعد
        today_start = datetime.combine(now.date(), self.start_time)
        today_start = tehran_tz.localize(today_start)
        
        if now.time() < self.start_time:
            # امروز هنوز باز نشده
            return today_start - now
        else:
            # فردا باز می‌شود
            tomorrow_start = today_start + timedelta(days=1)
            return tomorrow_start - now
    
    def time_until_close(self):
        """
        🕐 محاسبه زمان باقی‌مانده تا بسته شدن فروشگاه
        """
        if not self.is_currently_open():
            return None
        
        import pytz
        from datetime import datetime, timedelta
        
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = timezone.now().astimezone(tehran_tz)
        
        # محاسبه زمان بسته شدن
        today_end = datetime.combine(now.date(), self.end_time)
        today_end = tehran_tz.localize(today_end)
        
        if self.start_time <= self.end_time:
            # ساعات کاری در همان روز
            if now.time() <= self.end_time:
                return today_end - now
        else:
            # ساعات کاری از نیمه‌شب رد می‌شود
            if now.time() >= self.start_time:
                # امشب بسته می‌شود
                tomorrow_end = today_end + timedelta(days=1)
                return tomorrow_end - now
            else:
                # امروز بسته می‌شود
                return today_end - now
        
        return None
    
    @classmethod
    def get_current_working_hours(cls):
        """
        🕐 دریافت ساعات کاری فعال فعلی
        """
        return cls.objects.filter(is_active=True).first()
    
    @classmethod
    def is_shop_open(cls):
        """
        🏪 بررسی باز بودن فروشگاه
        """
        current_hours = cls.get_current_working_hours()
        if not current_hours:
            return False
        return current_hours.is_currently_open()
    
    def get_working_hours_info(self):
        """
        📋 دریافت اطلاعات کامل ساعات کاری
        """
        return {
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'duration_hours': f"{self.get_duration_hours():.1f}",
            'is_active': self.is_active,
            'is_currently_open': self.is_currently_open(),
            'time_until_open': self.time_until_open(),
            'time_until_close': self.time_until_close(),
            'set_by': str(self.set_by) if self.set_by else 'تعیین نشده',
            'created_at': self.created_at.strftime('%Y/%m/%d %H:%M'),
            'description': self.description or 'بدون توضیحات'
        }
