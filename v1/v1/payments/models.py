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
        ('INSTALLMENT', '�� قسطی'),
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
        💾 ذخیره پرداخت با لاگ‌گذاری کامل
        """
        # تولید کد پیگیری منحصر به فرد
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        
        # محاسبه مبلغ نمایشی (تومان)
        self.display_amount = self.amount / 10
        
        # تنظیم زمان انقضا (30 دقیقه)
        if not self.expires_at and self.status in ['INITIATED', 'REDIRECTED', 'PENDING']:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        
        # لاگ‌گذاری
        current_user = get_current_user()
        username = self._get_username(current_user)
        is_new = not self.pk
        now_str = timezone.now().strftime('%Y-%m-%d %H:%M')
        
        log_entries = []
        if self.logs:
            log_entries = [entry.strip() for entry in self.logs.split(',') if entry.strip()]
        
        if is_new:
            # لاگ ایجاد پرداخت
            log_entries.append(f"{now_str} Payment initiated By {username}")
            log_entries.append(f"{now_str} Gateway: {self.gateway} By {username}")
            log_entries.append(f"{now_str} Amount: {self.display_amount:,.0f} Toman By {username}")
        else:
            try:
                old = Payment.objects.get(pk=self.pk)
                if old.status != self.status:
                    log_entries.append(f"{now_str} Status changed from {old.status} to {self.status} By {username}")
                if old.gateway_transaction_id != self.gateway_transaction_id and self.gateway_transaction_id:
                    log_entries.append(f"{now_str} Transaction ID: {self.gateway_transaction_id} By {username}")
                if self.error_message and old.error_message != self.error_message:
                    log_entries.append(f"{now_str} Error: {self.error_message[:100]} By {username}")
            except Payment.DoesNotExist:
                pass
        
        # مرتب‌سازی زمانی لاگ‌ها
        log_entries = sorted(log_entries, key=lambda x: x[:16])
        self.logs = ', '.join(log_entries) + (',' if log_entries else '')
        
        super().save(*args, **kwargs)
        
        # خروجی لاگ‌ها به CSV
        try:
            call_command('export_payments_logs_to_csv')
        except Exception:
            pass
    
    def _get_username(self, user):
        """دریافت نام کاربری"""
        if user and hasattr(user, 'get_full_name'):
            return user.get_full_name() or user.username
        elif user and hasattr(user, 'username'):
            return user.username
        else:
            return 'system'
    
    def generate_tracking_code(self):
        """
        🏷️ تولید کد پیگیری منحصر به فرد
        📋 فرمت: PAY-YYYYMMDD-XXXXXX
        """
        import random
        import string
        
        today = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            tracking_code = f"PAY-{today}-{random_part}"
            if not Payment.objects.filter(tracking_code=tracking_code).exists():
                return tracking_code
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            attempt += 1
        
        # اگر کد منحصر به فرد تولید نشد، از timestamp استفاده کن
        timestamp = timezone.now().strftime('%H%M%S%f')[:8]
        return f"PAY-{today}-{timestamp}"
    
    def mark_as_expired(self):
        """
        ⏰ علامت‌گذاری پرداخت به عنوان منقضی شده
        """
        if self.status in ['INITIATED', 'REDIRECTED', 'PENDING']:
            self.status = 'TIMEOUT'
            self.completed_at = timezone.now()
            self.error_message = 'جلسه پرداخت منقضی شده است'
            self.save()
    
    def mark_as_successful(self, transaction_id=None, reference_number=None, card_number=None):
        """
        ✅ علامت‌گذاری پرداخت به عنوان موفق
        """
        self.status = 'SUCCESS'
        self.completed_at = timezone.now()
        if transaction_id:
            self.gateway_transaction_id = transaction_id
        if reference_number:
            self.bank_reference_number = reference_number
        if card_number:
            self.masked_card_number = self.mask_card_number(card_number)
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
    📞 مدل کال‌بک پرداخت - ثبت پاسخ‌های درگاه
    
    🎯 این مدل برای ثبت تمام پاسخ‌های دریافتی از درگاه‌های پرداخت استفاده می‌شود
    🔐 حفظ اطلاعات کامل برای رفع اختلاف و بررسی‌های امنیتی
    """
    
    # 💳 پرداخت مرتبط
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='callbacks',
        verbose_name="💳 پرداخت",
        help_text="پرداخت مرتبط با این کال‌بک"
    )
    
    # 📞 نوع کال‌بک
    CALLBACK_TYPE_CHOICES = [
        ('VERIFY', '✅ تایید پرداخت'),
        ('RETURN', '🔙 بازگشت کاربر'),
        ('WEBHOOK', '🔗 وب‌هوک'),
        ('ERROR', '⚠️ خطا'),
    ]
    
    callback_type = models.CharField(
        max_length=20,
        choices=CALLBACK_TYPE_CHOICES,
        verbose_name="📞 نوع کال‌بک",
        help_text="نوع کال‌بک دریافتی"
    )
    
    # 📄 داده‌های خام دریافتی
    raw_data = models.JSONField(
        default=dict,
        verbose_name="📄 داده‌های خام",
        help_text="داده‌های خام دریافتی از درگاه"
    )
    
    # 🌐 IP آدرس ارسال‌کننده
    sender_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="🌐 IP ارسال‌کننده",
        help_text="آدرس IP ارسال‌کننده کال‌بک"
    )
    
    # 📝 پیام پاسخ
    response_message = models.TextField(
        blank=True,
        verbose_name="📝 پیام پاسخ",
        help_text="پیام پاسخ ارسال شده به درگاه"
    )
    
    # ✅ موفق بودن پردازش
    is_processed = models.BooleanField(
        default=False,
        verbose_name="✅ پردازش شده",
        help_text="آیا این کال‌بک با موفقیت پردازش شده است؟"
    )
    
    class Meta:
        verbose_name = "📞 کال‌بک پرداخت"
        verbose_name_plural = "📞 کال‌بک‌های پرداخت"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"📞 {self.callback_type} - {self.payment.tracking_code} - {self.created_at}"


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
    
    # 📅 زمان تکمیل بازگشت وجه
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="📅 زمان تکمیل"
    )
    
    class Meta:
        verbose_name = "💸 بازگشت وجه"
        verbose_name_plural = "💸 بازگشت‌های وجه"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"💸 {self.payment.tracking_code} - {self.refund_amount/10:,.0f} تومان - {self.get_status_display()}"
