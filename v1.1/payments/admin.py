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
        icon = icons.get(obj.gateway, '🌐')
        return format_html(
            '<span style="font-size: 1.2em;">{} {}</span>',
            icon,
            obj.get_gateway_display_persian()
        )
    gateway_badge.short_description = 'درگاه'
    
    def amount_display(self, obj):
        """نمایش مبلغ با فرمت مناسب"""
        formatted_amount = f"{obj.display_amount:,}"
        return format_html(
            '<span style="font-weight: bold; color: #27ae60;">{} تومان</span>',
            formatted_amount
        )
    amount_display.short_description = 'مبلغ'
    
    def customer_name(self, obj):
        """نام مشتری با لینک"""
        if obj.order and obj.order.customer:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:core_customer_change', args=[obj.order.customer.id]),
                obj.order.customer.customer_name
            )
        return '-'
    customer_name.short_description = 'مشتری'
    
    def order_number(self, obj):
        """شماره سفارش با لینک"""
        if obj.order:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:core_order_change', args=[obj.order.id]),
                obj.order.order_number
            )
        return '-'
    order_number.short_description = 'شماره سفارش'
    
    def completed_at(self, obj):
        """زمان تکمیل با فرمت مناسب"""
        if obj.completed_at:
            return obj.completed_at.strftime('%Y/%m/%d %H:%M')
        return '-'
    completed_at.short_description = 'زمان تکمیل'
    
    actions = ['mark_as_success', 'mark_as_failed', 'mark_as_cancelled']
    
    def mark_as_success(self, request, queryset):
        """علامت‌گذاری پرداخت‌ها به عنوان موفق"""
        count = 0
        for payment in queryset:
            if payment.status not in ['SUCCESS', 'REFUNDED']:
                payment.mark_as_success()
                count += 1
        
        self.message_user(
            request,
            f'{count} پرداخت با موفقیت علامت‌گذاری شد.'
        )
    mark_as_success.short_description = 'علامت‌گذاری به عنوان موفق'
    
    def mark_as_failed(self, request, queryset):
        """علامت‌گذاری پرداخت‌ها به عنوان ناموفق"""
        count = 0
        for payment in queryset:
            if payment.status not in ['SUCCESS', 'REFUNDED']:
                payment.mark_as_failed('تغییر دستی توسط ادمین')
                count += 1
        
        self.message_user(
            request,
            f'{count} پرداخت به عنوان ناموفق علامت‌گذاری شد.'
        )
    mark_as_failed.short_description = 'علامت‌گذاری به عنوان ناموفق'
    
    def mark_as_cancelled(self, request, queryset):
        """علامت‌گذاری پرداخت‌ها به عنوان لغو شده"""
        count = 0
        for payment in queryset:
            if payment.status not in ['SUCCESS', 'REFUNDED']:
                payment.status = 'CANCELLED'
                payment.completed_at = timezone.now()
                payment.error_message = 'لغو شده توسط ادمین'
                payment.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} پرداخت به عنوان لغو شده علامت‌گذاری شد.'
        )
    mark_as_cancelled.short_description = 'علامت‌گذاری به عنوان لغو شده'


@admin.register(PaymentCallback)
class PaymentCallbackAdmin(admin.ModelAdmin):
    """
    📞 مدیریت callback های پرداخت
    """
    
    list_display = [
        'payment_tracking', 'gateway', 'processing_status_badge', 
        'created_at', 'gateway_ip'
    ]
    
    list_filter = [
        'gateway', 'processing_status', 'created_at'
    ]
    
    search_fields = [
        'payment__tracking_code', 'gateway_ip'
    ]
    
    readonly_fields = [
        'payment', 'gateway', 'received_data', 'gateway_ip',
        'processing_logs', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('payment', 'gateway', 'processing_status')
        }),
        ('داده‌های دریافتی', {
            'fields': ('received_data', 'gateway_ip'),
            'classes': ('collapse',)
        }),
        ('پردازش', {
            'fields': ('error_message', 'processing_logs'),
            'classes': ('collapse',)
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def payment_tracking(self, obj):
        """کد پیگیری پرداخت با لینک"""
        if obj.payment:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:payments_payment_change', args=[obj.payment.id]),
                obj.payment.tracking_code
            )
        return '-'
    payment_tracking.short_description = 'کد پیگیری پرداخت'
    
    def processing_status_badge(self, obj):
        """نمایش وضعیت پردازش با رنگ‌بندی"""
        colors = {
            'PENDING': '#FFA500',
            'PROCESSING': '#1E90FF',
            'SUCCESS': '#228B22',
            'FAILED': '#DC143C',
            'ERROR': '#FF0000',
        }
        color = colors.get(obj.processing_status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_processing_status_display()
        )
    processing_status_badge.short_description = 'وضعیت پردازش'


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    """
    💸 مدیریت بازگشت‌های وجه
    """
    
    list_display = [
        'payment_tracking', 'refund_amount_display', 'status_badge',
        'requested_by', 'requested_at', 'completed_at'
    ]
    
    list_filter = [
        'status', 'requested_at', 'completed_at'
    ]
    
    search_fields = [
        'payment__tracking_code', 'refund_transaction_id', 'reason'
    ]
    
    readonly_fields = [
        'payment', 'refund_amount', 'requested_by', 'requested_at',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('payment', 'refund_amount', 'status')
        }),
        ('جزئیات بازگشت', {
            'fields': ('refund_transaction_id', 'reason', 'notes')
        }),
        ('درخواست‌کننده', {
            'fields': ('requested_by', 'requested_at'),
            'classes': ('collapse',)
        }),
        ('زمان‌بندی', {
            'fields': ('completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'requested_at'
    ordering = ['-created_at']
    
    def payment_tracking(self, obj):
        """کد پیگیری پرداخت با لینک"""
        if obj.payment:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:payments_payment_change', args=[obj.payment.id]),
                obj.payment.tracking_code
            )
        return '-'
    payment_tracking.short_description = 'کد پیگیری پرداخت'
    
    def refund_amount_display(self, obj):
        """نمایش مبلغ بازگشت با فرمت مناسب"""
        formatted_amount = f"{obj.refund_amount:,}"
        return format_html(
            '<span style="font-weight: bold; color: #e74c3c;">{} ریال</span>',
            formatted_amount
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
    
    def completed_at(self, obj):
        """زمان تکمیل با فرمت مناسب"""
        if obj.completed_at:
            return obj.completed_at.strftime('%Y/%m/%d %H:%M')
        return '-'
    completed_at.short_description = 'زمان تکمیل'


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
