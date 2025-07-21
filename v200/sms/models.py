"""
📱 SMS Models for HomayOMS
مدل‌های سیستم پیامک برای ردیابی و مدیریت
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from HomayOMS.baseModel import BaseModel
import uuid


class SMSTemplate(BaseModel):
    """
    📝 قالب‌های پیامک
    """
    TEMPLATE_TYPE_CHOICES = [
        ('VERIFICATION', '🔐 کد تایید'),
        ('ORDER_STATUS', '📦 وضعیت سفارش'),
        ('PAYMENT', '💳 پرداخت'),
        ('NOTIFICATION', '🔔 اطلاع‌رسانی'),
        ('MARKETING', '📢 بازاریابی'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="نام قالب",
        help_text="نام قالب پیامک"
    )
    
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPE_CHOICES,
        verbose_name="نوع قالب",
        help_text="نوع قالب پیامک"
    )
    
    content = models.TextField(
        verbose_name="محتوای قالب",
        help_text="محتوای قالب با متغیرهای {variable}"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="آیا این قالب فعال است"
    )
    
    variables = models.JSONField(
        default=dict,
        verbose_name="متغیرها",
        help_text="متغیرهای مورد نیاز قالب"
    )
    
    class Meta:
        verbose_name = "قالب پیامک"
        verbose_name_plural = "قالب‌های پیامک"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def format_message(self, **kwargs):
        """فرمت کردن پیام با متغیرهای داده شده"""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            return f"خطا در فرمت قالب: متغیر {e} یافت نشد"


class SMSMessage(BaseModel):
    """
    📱 پیام‌های ارسالی
    """
    STATUS_CHOICES = [
        ('PENDING', '⏳ در انتظار'),
        ('SENT', '✅ ارسال شده'),
        ('DELIVERED', '📨 تحویل داده شده'),
        ('FAILED', '❌ ناموفق'),
        ('CANCELLED', '🚫 لغو شده'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('VERIFICATION', '🔐 کد تایید'),
        ('ORDER_STATUS', '📦 وضعیت سفارش'),
        ('PAYMENT', '💳 پرداخت'),
        ('NOTIFICATION', '🔔 اطلاع‌رسانی'),
        ('MARKETING', '📢 بازاریابی'),
    ]
    
    # شناسه یکتا برای ردیابی
    tracking_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name="شناسه ردیابی",
        help_text="شناسه یکتای ردیابی پیام"
    )
    
    # اطلاعات گیرنده
    phone_number = models.CharField(
        max_length=20,
        verbose_name="شماره تلفن",
        help_text="شماره تلفن گیرنده"
    )
    
    # محتوای پیام
    message_content = models.TextField(
        verbose_name="محتوای پیام",
        help_text="محتوای پیام ارسالی"
    )
    
    # نوع پیام
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        verbose_name="نوع پیام",
        help_text="نوع پیام ارسالی"
    )
    
    # قالب استفاده شده
    template = models.ForeignKey(
        SMSTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="قالب",
        help_text="قالب استفاده شده"
    )
    
    # وضعیت پیام
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="وضعیت",
        help_text="وضعیت فعلی پیام"
    )
    
    # اطلاعات ارسال
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ارسال",
        help_text="زمان ارسال پیام"
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تحویل",
        help_text="زمان تحویل پیام"
    )
    
    # اطلاعات خطا
    error_message = models.TextField(
        blank=True,
        verbose_name="پیام خطا",
        help_text="پیام خطا در صورت عدم موفقیت"
    )
    
    # اطلاعات API
    api_response = models.JSONField(
        default=dict,
        verbose_name="پاسخ API",
        help_text="پاسخ دریافتی از سرور SMS"
    )
    
    # کاربر مرتبط
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کاربر",
        help_text="کاربر مرتبط با پیام"
    )
    
    # اطلاعات اضافی
    extra_data = models.JSONField(
        default=dict,
        verbose_name="اطلاعات اضافی",
        help_text="اطلاعات اضافی مرتبط با پیام"
    )
    
    class Meta:
        verbose_name = "پیام پیامک"
        verbose_name_plural = "پیام‌های پیامک"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
            models.Index(fields=['message_type']),
            models.Index(fields=['tracking_id']),
        ]
    
    def __str__(self):
        return f"{self.phone_number} - {self.get_message_type_display()} ({self.get_status_display()})"
    
    def mark_as_sent(self, api_response=None):
        """علامت‌گذاری پیام به عنوان ارسال شده"""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        if api_response:
            self.api_response = api_response
        self.save()
    
    def mark_as_delivered(self):
        """علامت‌گذاری پیام به عنوان تحویل داده شده"""
        self.status = 'DELIVERED'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message, api_response=None):
        """علامت‌گذاری پیام به عنوان ناموفق"""
        self.status = 'FAILED'
        self.error_message = error_message
        if api_response:
            self.api_response = api_response
        self.save()


class SMSVerification(BaseModel):
    """
    🔐 کدهای تایید SMS
    """
    phone_number = models.CharField(
        max_length=20,
        verbose_name="شماره تلفن",
        help_text="شماره تلفن دریافت‌کننده"
    )
    
    verification_code = models.CharField(
        max_length=6,
        verbose_name="کد تایید",
        help_text="کد تایید 6 رقمی"
    )
    
    expires_at = models.DateTimeField(
        verbose_name="زمان انقضا",
        help_text="زمان انقضای کد تایید"
    )
    
    is_used = models.BooleanField(
        default=False,
        verbose_name="استفاده شده",
        help_text="آیا کد تایید استفاده شده است"
    )
    
    attempts = models.IntegerField(
        default=0,
        verbose_name="تعداد تلاش",
        help_text="تعداد تلاش‌های ناموفق"
    )
    
    sms_message = models.ForeignKey(
        SMSMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="پیام SMS",
        help_text="پیام SMS مرتبط"
    )
    
    class Meta:
        verbose_name = "کد تایید SMS"
        verbose_name_plural = "کدهای تایید SMS"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['verification_code']),
        ]
    
    def __str__(self):
        return f"{self.phone_number} - {self.verification_code}"
    
    def is_valid(self):
        """بررسی اعتبار کد تایید"""
        return (
            not self.is_used and
            timezone.now() <= self.expires_at and
            self.attempts < 3
        )
    
    def increment_attempts(self):
        """افزایش تعداد تلاش‌های ناموفق"""
        self.attempts += 1
        self.save()
    
    def mark_as_used(self):
        """علامت‌گذاری کد به عنوان استفاده شده"""
        self.is_used = True
        self.save()


class SMSSettings(BaseModel):
    """
    ⚙️ تنظیمات سیستم SMS
    """
    # تنظیمات سرور SMS
    sms_server_url = models.URLField(
        default="http://192.168.1.60:5003",
        verbose_name="آدرس سرور SMS",
        help_text="آدرس سرور SMS"
    )
    
    api_key = models.CharField(
        max_length=100,
        default="ioms_sms_server_2025",
        verbose_name="کلید API",
        help_text="کلید API برای دسترسی به سرور SMS"
    )
    
    # تنظیمات ارسال
    default_sender = models.CharField(
        max_length=20,
        default="HomayOMS",
        verbose_name="فرستنده پیش‌فرض",
        help_text="نام فرستنده پیش‌فرض"
    )
    
    verification_code_expiry = models.IntegerField(
        default=10,
        verbose_name="زمان انقضای کد تایید (دقیقه)",
        help_text="زمان انقضای کد تایید به دقیقه"
    )
    
    max_verification_attempts = models.IntegerField(
        default=3,
        verbose_name="حداکثر تلاش‌های تایید",
        help_text="حداکثر تعداد تلاش‌های ناموفق"
    )
    
    # تنظیمات اعلان‌ها
    enable_order_notifications = models.BooleanField(
        default=True,
        verbose_name="اعلان‌های سفارش",
        help_text="فعال‌سازی اعلان‌های وضعیت سفارش"
    )
    
    enable_payment_notifications = models.BooleanField(
        default=True,
        verbose_name="اعلان‌های پرداخت",
        help_text="فعال‌سازی اعلان‌های پرداخت"
    )
    
    # تنظیمات پیشرفته
    retry_attempts = models.IntegerField(
        default=3,
        verbose_name="تعداد تلاش‌های مجدد",
        help_text="تعداد تلاش‌های مجدد در صورت شکست"
    )
    
    timeout_seconds = models.IntegerField(
        default=30,
        verbose_name="زمان انتظار (ثانیه)",
        help_text="زمان انتظار برای پاسخ API"
    )
    
    class Meta:
        verbose_name = "تنظیمات SMS"
        verbose_name_plural = "تنظیمات SMS"
    
    def __str__(self):
        return "تنظیمات سیستم SMS"
    
    @classmethod
    def get_settings(cls):
        """دریافت تنظیمات SMS (تنظیمات پیش‌فرض اگر وجود نداشته باشد)"""
        settings_obj, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'sms_server_url': getattr(settings, 'SMS_SERVER_URL', "http://192.168.1.60:5003"),
                'api_key': getattr(settings, 'SMS_API_KEY', "ioms_sms_server_2025"),
                'default_sender': "HomayOMS",
                'verification_code_expiry': 10,
                'max_verification_attempts': 3,
                'enable_order_notifications': True,
                'enable_payment_notifications': True,
                'retry_attempts': getattr(settings, 'SMS_RETRY_ATTEMPTS', 3),
                'timeout_seconds': getattr(settings, 'SMS_TIMEOUT', 30),
            }
        )
        return settings_obj 