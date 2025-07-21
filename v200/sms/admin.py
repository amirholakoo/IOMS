"""
📱 Admin interface for SMS management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SMSTemplate, SMSMessage, SMSVerification, SMSSettings


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    """
    📝 Admin interface for SMS templates
    """
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('محتوای قالب', {
            'fields': ('content', 'variables'),
            'description': 'از متغیرهای {variable} برای قالب استفاده کنید'
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    """
    📱 Admin interface for SMS messages
    """
    list_display = [
        'phone_number', 
        'message_type', 
        'status', 
        'created_at', 
        'sent_at',
        'tracking_link'
    ]
    list_filter = ['status', 'message_type', 'created_at', 'sent_at']
    search_fields = ['phone_number', 'message_content', 'tracking_id']
    readonly_fields = [
        'tracking_id', 'created_at', 'sent_at', 'delivered_at', 
        'api_response', 'extra_data'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('tracking_id', 'phone_number', 'message_type', 'status')
        }),
        ('محتوای پیام', {
            'fields': ('message_content', 'template', 'user')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'sent_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('اطلاعات فنی', {
            'fields': ('api_response', 'error_message', 'extra_data'),
            'classes': ('collapse',)
        }),
    )
    
    def tracking_link(self, obj):
        """لینک ردیابی پیام"""
        if obj.tracking_id:
            return format_html(
                '<a href="{}" target="_blank">🔍 ردیابی</a>',
                reverse('sms:message_detail', args=[obj.tracking_id])
            )
        return '-'
    tracking_link.short_description = 'ردیابی'
    
    def has_add_permission(self, request):
        """غیرفعال کردن افزودن دستی پیام‌ها"""
        return False


@admin.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    """
    🔐 Admin interface for SMS verifications
    """
    list_display = [
        'phone_number', 
        'verification_code', 
        'is_used', 
        'attempts', 
        'created_at', 
        'expires_at',
        'is_valid_display'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['phone_number', 'verification_code']
    readonly_fields = ['created_at', 'expires_at', 'sms_message']
    
    fieldsets = (
        ('اطلاعات کد تایید', {
            'fields': ('phone_number', 'verification_code', 'is_used', 'attempts')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('مرتبط', {
            'fields': ('sms_message',),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid_display(self, obj):
        """نمایش وضعیت اعتبار کد"""
        if obj.is_valid():
            return mark_safe('<span style="color: green;">✅ معتبر</span>')
        else:
            return mark_safe('<span style="color: red;">❌ نامعتبر</span>')
    is_valid_display.short_description = 'وضعیت اعتبار'
    
    def has_add_permission(self, request):
        """غیرفعال کردن افزودن دستی کدهای تایید"""
        return False


@admin.register(SMSSettings)
class SMSSettingsAdmin(admin.ModelAdmin):
    """
    ⚙️ Admin interface for SMS settings
    """
    list_display = ['__str__', 'sms_server_url', 'api_key', 'default_sender']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('تنظیمات سرور', {
            'fields': ('sms_server_url', 'api_key')
        }),
        ('تنظیمات ارسال', {
            'fields': ('default_sender', 'verification_code_expiry', 'max_verification_attempts')
        }),
        ('تنظیمات اعلان‌ها', {
            'fields': ('enable_order_notifications', 'enable_payment_notifications')
        }),
        ('تنظیمات پیشرفته', {
            'fields': ('retry_attempts', 'timeout_seconds'),
            'classes': ('collapse',)
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """فقط یک رکورد تنظیمات مجاز است"""
        return not SMSSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """غیرفعال کردن حذف تنظیمات"""
        return False 