from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.management import call_command
import json

from HomayOMS.baseModel import BaseModel


def get_current_user():
    """Get current user from thread local storage"""
    try:
        from core.middleware import get_current_user as _get_current_user
        return _get_current_user()
    except ImportError:
        return None


class Payment(BaseModel):
    """
    💳 مدل پرداخت - مدیریت پرداخت‌های آنلاین
    
    🎯 این مدل برای مدیریت فرآیند پرداخت از طریق درگاه‌های ایرانی استفاده می‌شود
    🔐 شامل پیگیری کامل وضعیت پرداخت و لاگ‌های دقیق
    ⏰ دارای فیلدهای created_at و updated_at از BaseModel
    
    🔧 استفاده:
        payment = Payment.objects.create(
            order=order,
            amount=100000,
            gateway='zarinpal'
        )
    """
    
    # 🌐 درگاه‌های پرداخت ایرانی
    GATEWAY_CHOICES = [
        ('zarinpal', '💎 زرین‌پال'),
        ('shaparak', '🏦 شاپرک'),
        ('mellat', '🟢 ملت'),
        ('parsian', '🔵 پارسیان'),
        ('pasargad', '🟡 پاسارگاد'),
        ('saderat', '🟠 صادرات'),
    ]
    
    # 📊 وضعیت‌های پرداخت (جامع و دقیق)
    STATUS_CHOICES = [
        ('INITIATED', '🟡 آغاز شده'),           # Payment created, waiting for user action
        ('REDIRECTED', '🔄 هدایت شده'),         # User redirected to gateway
        ('PENDING', '⏳ در انتظار پرداخت'),      # At payment gateway, waiting for payment
        ('PROCESSING', '🔄 در حال پردازش'),     # Payment being processed by gateway
        ('VERIFYING', '🔍 در حال تایید'),       # Verifying payment with gateway
        ('SUCCESS', '✅ موفق'),                 # Payment completed successfully
        ('FAILED', '❌ ناموفق'),                # Payment failed
        ('CANCELLED', '🚫 لغو شده'),            # User cancelled payment
        ('TIMEOUT', '⏰ منقضی شده'),            # Payment session expired
        ('REFUNDED', '💸 بازگشت داده شده'),     # Payment refunded
        ('PARTIALLY_REFUNDED', '💰 بازگشت جزئی'), # Partial refund
        ('DISPUTED', '⚖️ مورد اختلاف'),         # Payment disputed
        ('ERROR', '⚠️ خطا'),                   # Technical error occurred
    ]
    
    # 💳 نوع پرداخت
    PAYMENT_TYPE_CHOICES = [
        ('FULL', '💰 پرداخت کامل'),
        ('PARTIAL', '💵 پرداخت جزئی'),
        ('INSTALLMENT', '💳 قسطی'),
    ]
    
    # 🛒 سفارش مرتبط
    order = models.ForeignKey(
        'core.Order',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="🛒 سفارش",
        help_text="سفارش مرتبط با این پرداخت"
    )
    
    # 👤 کاربر پرداخت‌کننده
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name="👤 کاربر",
        help_text="کاربری که پرداخت را انجام می‌دهد"
    )
    
    # 🏷️ شماره پیگیری منحصر به فرد
    tracking_code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="🏷️ کد پیگیری",
        help_text="شماره پیگیری منحصر به فرد پرداخت"
    )
    
    # 💰 مبلغ پرداخت (ریال)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="💰 مبلغ (ریال)",
        help_text="مبلغ پرداخت به ریال"
    )
    
    # 💵 مبلغ نمایشی (تومان)
    display_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="💵 مبلغ نمایشی (تومان)",
        help_text="مبلغ نمایشی به تومان"
    )
    
    # 🌐 درگاه پرداخت
    gateway = models.CharField(
        max_length=20,
        choices=GATEWAY_CHOICES,
        verbose_name="🌐 درگاه پرداخت",
        help_text="درگاه پرداخت انتخابی"
    )
    
    # 📊 وضعیت پرداخت
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='INITIATED',
        verbose_name="📊 وضعیت پرداخت",
        help_text="وضعیت فعلی پرداخت"
    )
    
    # 💳 نوع پرداخت
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default='FULL',
        verbose_name="💳 نوع پرداخت",
        help_text="نوع پرداخت (کامل/جزئی/قسطی)"
    )
    
    # 🆔 شماره تراکنش درگاه
    gateway_transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="🆔 شماره تراکنش درگاه",
        help_text="شماره تراکنش ارائه شده توسط درگاه"
    )
    
    # 🏦 شماره مرجع بانک
    bank_reference_number = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="🏦 شماره مرجع بانک",
        help_text="شماره مرجع ارائه شده توسط بانک"
    )
    
    # 💳 شماره کارت (ماسک شده)
    masked_card_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="💳 شماره کارت (ماسک)",
        help_text="شماره کارت ماسک شده (مثال: ****-****-****-1234)"
    )
    
    # 🌐 IP آدرس کاربر
    user_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="🌐 IP کاربر",
        help_text="آدرس IP کاربر در زمان پرداخت"
    )
    
    # 🖥️ اطلاعات مرورگر
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="🖥️ اطلاعات مرورگر",
        help_text="اطلاعات مرورگر و سیستم‌عامل کاربر"
    )
    
    # 📅 زمان شروع پرداخت
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="📅 زمان شروع",
        help_text="زمان شروع فرآیند پرداخت"
    )
    
    # 📅 زمان اتمام پرداخت
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="📅 زمان اتمام",
        help_text="زمان اتمام یا لغو پرداخت"
    )
    
    # ⏰ زمان انقضا
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="⏰ زمان انقضا",
        help_text="زمان انقضای جلسه پرداخت"
    )
    
    # 📄 داده‌های اضافی درگاه (JSON)
    gateway_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="📄 داده‌های درگاه",
        help_text="اطلاعات اضافی دریافتی از درگاه (JSON)"
    )
    
    # 📝 پیام خطا (در صورت وجود)
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="📝 پیام خطا",
        help_text="پیام خطا در صورت عدم موفقیت پرداخت"
    )
    
    # 🔄 تعداد تلاش‌های انجام شده
    retry_count = models.PositiveIntegerField(
        default=0,
        verbose_name="🔄 تعداد تلاش",
        help_text="تعداد تلاش‌های انجام شده برای پرداخت"
    )
    
    # 📱 شماره تلفن پرداخت‌کننده
    payer_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="📱 شماره تلفن پرداخت‌کننده",
        help_text="شماره تلفن فرد پرداخت‌کننده"
    )
    
    # 📧 ایمیل پرداخت‌کننده
    payer_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="📧 ایمیل پرداخت‌کننده",
        help_text="ایمیل فرد پرداخت‌کننده"
    )
    
    # 📝 توضیحات پرداخت
    description = models.TextField(
        blank=True,
        verbose_name="📝 توضیحات",
        help_text="توضیحات اضافی درباره پرداخت"
    )
    
    # 📝 لاگ‌های تحلیلی (مشابه Customer و Order)
    logs = models.TextField(
        blank=True,
        verbose_name="📝 لاگ‌های پرداخت",
        help_text="لاگ‌های کامل فرآیند پرداخت"
    )
    
    class Meta:
        verbose_name = "💳 پرداخت"
        verbose_name_plural = "💳 پرداخت‌ها"
        ordering = ['-created_at']
        
        indexes = [
            models.Index(fields=['tracking_code']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['status']),
            models.Index(fields=['gateway']),
            models.Index(fields=['order']),
            models.Index(fields=['user']),
            models.Index(fields=['started_at']),
        ]
    
    def clean(self):
        """
        🧹 اعتبارسنجی داده‌های پرداخت
        """
        # بررسی مثبت بودن مبلغ
        if self.amount <= 0:
            raise ValidationError({
                'amount': '💰 مبلغ پرداخت باید مثبت باشد'
            })
        
        # بررسی حداقل مبلغ پرداخت (1000 ریال)
        if self.amount < 1000:
            raise ValidationError({
                'amount': '💰 حداقل مبلغ پرداخت 1000 ریال است'
            })
    
    def save(self, *args, **kwargs):
        """
        💾 ذخیره پرداخت با تولید کد پیگیری
        """
        # تولید کد پیگیری در صورت عدم وجود
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        
        # تنظیم مبلغ نمایشی (تومان)
        if not self.display_amount:
            self.display_amount = self.amount / 10  # تبدیل ریال به تومان
        
        # تنظیم زمان انقضا در صورت عدم وجود
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        
        # ثبت لاگ تغییرات
        self.log_activity('SAVE', f'پرداخت {self.tracking_code} ذخیره شد - وضعیت: {self.get_status_display_persian()}')
        
        super().save(*args, **kwargs)
    
    def generate_tracking_code(self):
        """
        🏷️ تولید کد پیگیری منحصر به فرد
        """
        import uuid
        import time
        
        # ترکیب timestamp و uuid برای اطمینان از یکتا بودن
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        return f"PAY{timestamp}{unique_id}"
    
    def log_activity(self, action, description, extra_data=None):
        """
        📝 ثبت لاگ فعالیت پرداخت
        """
        try:
            from core.models import ActivityLog
            
            # تبدیل extra_data به JSON
            extra_json = {}
            if extra_data:
                if isinstance(extra_data, dict):
                    extra_json = extra_data
                else:
                    extra_json = {'data': str(extra_data)}
            
            # ثبت لاگ
            ActivityLog.log_activity(
                user=get_current_user(),
                action=action,
                description=description,
                content_object=self,
                ip_address=None,  # در مدل پرداخت IP جداگانه داریم
                user_agent=None,  # در مدل پرداخت user_agent جداگانه داریم
                severity='MEDIUM',
                extra_data=extra_json
            )
            
            # اضافه کردن به لاگ‌های داخلی
            log_entry = f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] {action}: {description}\n"
            self.logs = (self.logs or '') + log_entry
            
        except Exception as e:
            # در صورت خطا در ثبت لاگ، فقط در لاگ‌های داخلی ذخیره کن
            log_entry = f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] LOG_ERROR: {str(e)} - {action}: {description}\n"
            self.logs = (self.logs or '') + log_entry
    
    def mark_as_success(self, verification_data=None):
        """
        ✅ علامت‌گذاری پرداخت به عنوان موفق
        """
        self.status = 'SUCCESS'
        self.completed_at = timezone.now()
        
        if verification_data:
            self.gateway_data.update(verification_data)
        
        self.log_activity('SUCCESS', f'پرداخت {self.tracking_code} با موفقیت انجام شد')
        self.save()
    
    def mark_as_failed(self, error_message=None):
        """
        ❌ علامت‌گذاری پرداخت به عنوان ناموفق
        """
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save()
    
    def mark_as_expired(self):
        """
        ⏰ علامت‌گذاری پرداخت به عنوان منقضی شده
        """
        self.status = 'TIMEOUT'
        self.completed_at = timezone.now()
        self.error_message = '⏰ جلسه پرداخت منقضی شده است'
        self.log_activity('TIMEOUT', f'پرداخت {self.tracking_code} منقضی شد')
        self.save()
    
    def mask_card_number(self, card_number):
        """
        🔒 ماسک کردن شماره کارت
        """
        if not card_number or len(card_number) < 16:
            return card_number
        
        cleaned = ''.join(filter(str.isdigit, card_number))
        if len(cleaned) >= 16:
            return f"****-****-****-{cleaned[-4:]}"
        return card_number
    
    def can_retry(self):
        """
        🔄 بررسی امکان تلاش مجدد
        """
        return (
            self.status in ['FAILED', 'TIMEOUT', 'CANCELLED'] and 
            self.retry_count < 3 and
            timezone.now() < (self.started_at + timezone.timedelta(hours=24))
        )
    
    def is_expired(self):
        """
        ⏰ بررسی انقضای پرداخت
        """
        return (
            self.expires_at and 
            timezone.now() > self.expires_at and 
            self.status in ['INITIATED', 'REDIRECTED', 'PENDING']
        )
    
    def get_status_display_persian(self):
        """
        📊 نمایش وضعیت به فارسی
        """
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, self.status)
    
    def get_gateway_display_persian(self):
        """
        🌐 نمایش درگاه به فارسی
        """
        gateway_map = dict(self.GATEWAY_CHOICES)
        return gateway_map.get(self.gateway, self.gateway)
    
    def __str__(self):
        """
        📄 نمایش رشته‌ای پرداخت
        """
        return f"💳 {self.tracking_code} - {self.display_amount:,.0f} تومان - {self.get_status_display_persian()}"


class PaymentCallback(BaseModel):
    """
    📞 مدل callback پرداخت - ثبت پاسخ‌های درگاه
    
    🎯 این مدل برای ثبت و پیگیری callback های دریافتی از درگاه‌های پرداخت استفاده می‌شود
    🔐 شامل تمام پارامترهای دریافتی و وضعیت پردازش
    """
    
    # 💳 پرداخت مرتبط
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='callbacks',
        verbose_name="💳 پرداخت",
        help_text="پرداخت مرتبط با این callback"
    )
    
    # 🌐 درگاه پرداخت
    gateway = models.CharField(
        max_length=20,
        choices=Payment.GATEWAY_CHOICES,
        verbose_name="🌐 درگاه پرداخت"
    )
    
    # 📄 داده‌های دریافتی (JSON)
    received_data = models.JSONField(
        verbose_name="📄 داده‌های دریافتی",
        help_text="تمام پارامترهای دریافتی از درگاه (JSON)"
    )
    
    # 📊 وضعیت پردازش
    PROCESSING_STATUS_CHOICES = [
        ('PENDING', '⏳ در انتظار پردازش'),
        ('PROCESSING', '🔄 در حال پردازش'),
        ('SUCCESS', '✅ پردازش موفق'),
        ('FAILED', '❌ پردازش ناموفق'),
        ('ERROR', '⚠️ خطا در پردازش'),
    ]
    
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='PENDING',
        verbose_name="📊 وضعیت پردازش"
    )
    
    # 📝 پیام خطا (در صورت وجود)
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="📝 پیام خطا"
    )
    
    # 🌐 IP آدرس درگاه
    gateway_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="🌐 IP درگاه"
    )
    
    # 📝 لاگ‌های پردازش
    processing_logs = models.TextField(
        blank=True,
        verbose_name="📝 لاگ‌های پردازش"
    )
    
    class Meta:
        verbose_name = "📞 Callback پرداخت"
        verbose_name_plural = "📞 Callback های پرداخت"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"📞 {self.payment.tracking_code} - {self.gateway} - {self.get_processing_status_display()}"


class PaymentRefund(BaseModel):
    """
    💸 مدل بازگشت وجه - مدیریت استرداد پرداخت‌ها
    
    🎯 این مدل برای مدیریت فرآیند بازگشت وجه استفاده می‌شود
    """
    
    # 💳 پرداخت اصلی
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name="💳 پرداخت اصلی",
        help_text="پرداخت اصلی که بازگشت وجه آن درخواست شده"
    )
    
    # 💰 مبلغ بازگشت (ریال)
    refund_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="💰 مبلغ بازگشت (ریال)",
        help_text="مبلغ بازگشت وجه به ریال"
    )
    
    # 📊 وضعیت بازگشت وجه
    REFUND_STATUS_CHOICES = [
        ('INITIATED', '🟡 درخواست شده'),
        ('PROCESSING', '🔄 در حال پردازش'),
        ('SUCCESS', '✅ موفق'),
        ('FAILED', '❌ ناموفق'),
        ('CANCELLED', '🚫 لغو شده'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='INITIATED',
        verbose_name="📊 وضعیت بازگشت وجه"
    )
    
    # 🆔 شماره تراکنش بازگشت
    refund_transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="🆔 شماره تراکنش بازگشت"
    )
    
    # 📝 دلیل بازگشت وجه
    reason = models.TextField(
        verbose_name="📝 دلیل بازگشت وجه",
        help_text="دلیل درخواست بازگشت وجه"
    )
    
    # 👤 درخواست‌کننده بازگشت وجه
    requested_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="👤 درخواست‌کننده"
    )
    
    # 📅 زمان درخواست بازگشت
    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="📅 زمان درخواست"
    )
    
    # 📅 زمان تکمیل بازگشت
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="📅 زمان تکمیل"
    )
    
    # 📝 توضیحات اضافی
    notes = models.TextField(
        blank=True,
        verbose_name="📝 توضیحات"
    )
    
    class Meta:
        verbose_name = "💸 بازگشت وجه"
        verbose_name_plural = "💸 بازگشت‌های وجه"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"💸 {self.payment.tracking_code} - {self.refund_amount:,.0f} ریال - {self.get_status_display()}"
