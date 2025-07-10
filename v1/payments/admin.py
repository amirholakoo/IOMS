from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Payment, PaymentCallback, PaymentRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    💳 مدیریت پرداخت‌ها در پنل ادمین
    """
    
    list_display = [
        'tracking_code', 'status_badge', 'gateway_badge', 'amount_display', 
        'customer_name', 'order_number', 'created_at', 'completed_at'
    ]
    
    list_filter = [
        'status', 'gateway', 'payment_type', 'created_at', 'completed_at'
    ]
    
    search_fields = [
        'tracking_code', 'order__order_number', 'order__customer__customer_name',
        'gateway_transaction_id', 'bank_reference_number', 'payer_phone'
    ]
    
    readonly_fields = [
        'tracking_code', 'display_amount', 'gateway_data', 'logs',
        'created_at', 'updated_at', 'started_at', 'completed_at'
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('tracking_code', 'order', 'user', 'status', 'gateway')
        }),
        ('مبلغ پرداخت', {
            'fields': ('amount', 'display_amount', 'payment_type')
        }),
        ('اطلاعات درگاه', {
            'fields': ('gateway_transaction_id', 'bank_reference_number', 'masked_card_number')
        }),
        ('اطلاعات پرداخت‌کننده', {
            'fields': ('payer_phone', 'payer_email', 'user_ip', 'user_agent')
        }),
        ('زمان‌بندی', {
            'fields': ('started_at', 'expires_at', 'completed_at', 'created_at', 'updated_at')
        }),
        ('جزئیات تکمیلی', {
            'fields': ('description', 'error_message', 'retry_count'),
            'classes': ('collapse',)
        }),
        ('داده‌های فنی', {
            'fields': ('gateway_data', 'logs'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        """نمایش وضعیت با رنگ‌بندی"""
        colors = {
            'INITIATED': '#FFA500',
            'REDIRECTED': '#1E90FF',
            'PENDING': '#FFD700',
            'PROCESSING': '#9370DB',
            'VERIFYING': '#4682B4',
            'SUCCESS': '#228B22',
            'FAILED': '#DC143C',
            'CANCELLED': '#696969',
            'TIMEOUT': '#B22222',
            'REFUNDED': '#20B2AA',
            'ERROR': '#FF0000',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display_persian()
        )
    status_badge.short_description = 'وضعیت'
    
    def gateway_badge(self, obj):
        """نمایش درگاه با آیکون"""
        icons = {
            'zarinpal': '💎',
            'shaparak': '🏦',
            'mellat': '🟢',
            'parsian': '🔵',
            'pasargad': '🟡',
            'saderat': '🟠',
        }
        icon = icons.get(obj.gateway, '💳')
        return format_html(
            '{} {}',
            icon,
            obj.get_gateway_display_persian()
        )
    gateway_badge.short_description = 'درگاه'
    
    def amount_display(self, obj):
        """نمایش مبلغ با فرمت‌بندی"""
        return format_html(
            '<strong>{:,.0f}</strong> تومان',
            obj.display_amount
        )
    amount_display.short_description = 'مبلغ'
    
    def customer_name(self, obj):
        """نام مشتری"""
        return obj.order.customer.customer_name
    customer_name.short_description = 'مشتری'
    
    def order_number(self, obj):
        """شماره سفارش با لینک"""
        url = reverse('admin:core_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_number.short_description = 'شماره سفارش'
    
    actions = ['mark_as_failed', 'check_status']
    
    def mark_as_failed(self, request, queryset):
        """علامت‌گذاری پرداخت‌ها به عنوان ناموفق"""
        updated = 0
        for payment in queryset:
            if payment.status in ['INITIATED', 'REDIRECTED', 'PENDING', 'PROCESSING']:
                payment.mark_as_failed('علامت‌گذاری دستی توسط ادمین')
                updated += 1
        
        self.message_user(request, f'{updated} پرداخت به عنوان ناموفق علامت‌گذاری شد.')
    mark_as_failed.short_description = 'علامت‌گذاری به عنوان ناموفق'
    
    def check_status(self, request, queryset):
        """بررسی وضعیت پرداخت‌ها"""
        expired_count = 0
        for payment in queryset:
            if payment.is_expired():
                payment.mark_as_expired()
                expired_count += 1
        
        self.message_user(request, f'{expired_count} پرداخت منقضی علامت‌گذاری شد.')
    check_status.short_description = 'بررسی وضعیت و انقضا'


@admin.register(PaymentCallback)
class PaymentCallbackAdmin(admin.ModelAdmin):
    """
    📞 مدیریت کال‌بک‌های پرداخت در پنل ادمین
    """
    
    list_display = [
        'payment_tracking_code', 'callback_type', 'is_processed', 
        'sender_ip', 'created_at'
    ]
    
    list_filter = ['callback_type', 'is_processed', 'created_at']
    
    search_fields = [
        'payment__tracking_code', 'sender_ip', 'raw_data'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'raw_data']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('payment', 'callback_type', 'is_processed')
        }),
        ('اطلاعات ارسال‌کننده', {
            'fields': ('sender_ip', 'response_message')
        }),
        ('داده‌های خام', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def payment_tracking_code(self, obj):
        """کد پیگیری پرداخت"""
        return obj.payment.tracking_code
    payment_tracking_code.short_description = 'کد پیگیری پرداخت'


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    """
    💸 مدیریت بازگشت وجه در پنل ادمین
    """
    
    list_display = [
        'payment_tracking_code', 'refund_amount_display', 'status_badge',
        'requested_by', 'created_at', 'completed_at'
    ]
    
    list_filter = ['status', 'created_at', 'completed_at']
    
    search_fields = [
        'payment__tracking_code', 'refund_transaction_id', 
        'reason', 'requested_by__username'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('payment', 'refund_amount', 'status')
        }),
        ('جزئیات بازگشت وجه', {
            'fields': ('refund_transaction_id', 'reason', 'requested_by')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'completed_at', 'updated_at')
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def payment_tracking_code(self, obj):
        """کد پیگیری پرداخت اصلی"""
        return obj.payment.tracking_code
    payment_tracking_code.short_description = 'کد پیگیری پرداخت'
    
    def refund_amount_display(self, obj):
        """نمایش مبلغ بازگشت"""
        return format_html(
            '<strong>{:,.0f}</strong> تومان',
            obj.refund_amount / 10
        )
    refund_amount_display.short_description = 'مبلغ بازگشت'
    
    def status_badge(self, obj):
        """نمایش وضعیت با رنگ‌بندی"""
        colors = {
            'INITIATED': '#FFA500',
            'PROCESSING': '#1E90FF',
            'SUCCESS': '#228B22',
            'FAILED': '#DC143C',
            'CANCELLED': '#696969',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'


# Inline admins for related models
class PaymentInline(admin.TabularInline):
    """
    نمایش پرداخت‌ها در صفحه سفارش
    """
    model = Payment
    extra = 0
    readonly_fields = ['tracking_code', 'status', 'gateway', 'amount', 'created_at']
    fields = ['tracking_code', 'status', 'gateway', 'amount', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class PaymentCallbackInline(admin.TabularInline):
    """
    نمایش کال‌بک‌ها در صفحه پرداخت
    """
    model = PaymentCallback
    extra = 0
    readonly_fields = ['callback_type', 'sender_ip', 'is_processed', 'created_at']
    fields = ['callback_type', 'sender_ip', 'is_processed', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
