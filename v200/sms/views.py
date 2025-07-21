"""
📱 Views for SMS app
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from accounts.permissions import super_admin_permission_required
from .models import SMSMessage, SMSVerification, SMSTemplate, SMSSettings
from .services import get_sms_service, get_sms_notification_service
from core.models import ActivityLog
import logging

logger = logging.getLogger(__name__)


@login_required
@super_admin_permission_required('sms.view_sms_dashboard')
def sms_dashboard_view(request):
    """
    📊 داشبورد SMS
    """
    try:
        # آمار کلی
        sms_service = get_sms_service()
        stats = sms_service.get_statistics()
        
        # پیام‌های اخیر
        recent_messages = SMSMessage.objects.select_related('user', 'template').order_by('-created_at')[:10]
        
        # کدهای تایید اخیر
        recent_verifications = SMSVerification.objects.select_related('sms_message').order_by('-created_at')[:10]
        
        # وضعیت سرور
        server_healthy, server_status = sms_service.check_server_health()
        
        context = {
            'stats': stats,
            'recent_messages': recent_messages,
            'recent_verifications': recent_verifications,
            'server_healthy': server_healthy,
            'server_status': server_status,
        }
        
        return render(request, 'sms/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"SMS dashboard error: {e}")
        messages.error(request, 'خطا در بارگذاری داشبورد SMS')
        return redirect('core:admin_dashboard')


@login_required
@super_admin_permission_required('sms.view_sms_messages')
def message_list_view(request):
    """
    📱 لیست پیام‌های SMS
    """
    try:
        # فیلترها
        status_filter = request.GET.get('status', '')
        message_type_filter = request.GET.get('message_type', '')
        phone_filter = request.GET.get('phone', '')
        
        # کوئری پایه
        messages_qs = SMSMessage.objects.select_related('user', 'template').order_by('-created_at')
        
        # اعمال فیلترها
        if status_filter:
            messages_qs = messages_qs.filter(status=status_filter)
        if message_type_filter:
            messages_qs = messages_qs.filter(message_type=message_type_filter)
        if phone_filter:
            messages_qs = messages_qs.filter(phone_number__icontains=phone_filter)
        
        # صفحه‌بندی
        paginator = Paginator(messages_qs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'message_type_filter': message_type_filter,
            'phone_filter': phone_filter,
            'status_choices': SMSMessage.STATUS_CHOICES,
            'message_type_choices': SMSMessage.MESSAGE_TYPE_CHOICES,
        }
        
        return render(request, 'sms/message_list.html', context)
        
    except Exception as e:
        logger.error(f"SMS message list error: {e}")
        messages.error(request, 'خطا در بارگذاری لیست پیام‌ها')
        return redirect('sms:dashboard')


@login_required
@super_admin_permission_required('sms.view_sms_messages')
def message_detail_view(request, tracking_id):
    """
    📱 جزئیات پیام SMS
    """
    try:
        message = get_object_or_404(SMSMessage, tracking_id=tracking_id)
        
        context = {
            'message': message,
        }
        
        return render(request, 'sms/message_detail.html', context)
        
    except Exception as e:
        logger.error(f"SMS message detail error: {e}")
        messages.error(request, 'خطا در بارگذاری جزئیات پیام')
        return redirect('sms:message_list')


@login_required
@super_admin_permission_required('sms.view_sms_templates')
def template_list_view(request):
    """
    📝 لیست قالب‌های SMS
    """
    try:
        templates = SMSTemplate.objects.order_by('-created_at')
        
        context = {
            'templates': templates,
        }
        
        return render(request, 'sms/template_list.html', context)
        
    except Exception as e:
        logger.error(f"SMS template list error: {e}")
        messages.error(request, 'خطا در بارگذاری لیست قالب‌ها')
        return redirect('sms:dashboard')


@login_required
@super_admin_permission_required('sms.add_sms_template')
def template_add_view(request):
    """
    📝 افزودن قالب جدید
    """
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            template_type = request.POST.get('template_type', '')
            content = request.POST.get('content', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            # اعتبارسنجی
            if not name or not template_type or not content:
                messages.error(request, 'لطفاً تمام فیلدهای اجباری را پر کنید')
                return render(request, 'sms/template_form.html', {
                    'template_types': SMSTemplate.TEMPLATE_TYPE_CHOICES,
                    'form_data': request.POST
                })
            
            # ایجاد قالب
            template = SMSTemplate.objects.create(
                name=name,
                template_type=template_type,
                content=content,
                is_active=is_active
            )
            
            # ثبت لاگ
            ActivityLog.log_activity(
                user=request.user,
                action='CREATE',
                description=f'قالب SMS جدید "{name}" ایجاد شد',
                content_object=template,
                severity='MEDIUM'
            )
            
            messages.success(request, f'قالب "{name}" با موفقیت ایجاد شد')
            return redirect('sms:template_list')
            
        except Exception as e:
            logger.error(f"SMS template add error: {e}")
            messages.error(request, 'خطا در ایجاد قالب')
    
    context = {
        'template_types': SMSTemplate.TEMPLATE_TYPE_CHOICES,
    }
    
    return render(request, 'sms/template_form.html', context)


@login_required
@super_admin_permission_required('sms.change_sms_template')
def template_edit_view(request, template_id):
    """
    📝 ویرایش قالب
    """
    template = get_object_or_404(SMSTemplate, id=template_id)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            template_type = request.POST.get('template_type', '')
            content = request.POST.get('content', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            # اعتبارسنجی
            if not name or not template_type or not content:
                messages.error(request, 'لطفاً تمام فیلدهای اجباری را پر کنید')
                return render(request, 'sms/template_form.html', {
                    'template': template,
                    'template_types': SMSTemplate.TEMPLATE_TYPE_CHOICES,
                    'form_data': request.POST
                })
            
            # به‌روزرسانی قالب
            template.name = name
            template.template_type = template_type
            template.content = content
            template.is_active = is_active
            template.save()
            
            # ثبت لاگ
            ActivityLog.log_activity(
                user=request.user,
                action='UPDATE',
                description=f'قالب SMS "{name}" ویرایش شد',
                content_object=template,
                severity='MEDIUM'
            )
            
            messages.success(request, f'قالب "{name}" با موفقیت ویرایش شد')
            return redirect('sms:template_list')
            
        except Exception as e:
            logger.error(f"SMS template edit error: {e}")
            messages.error(request, 'خطا در ویرایش قالب')
    
    context = {
        'template': template,
        'template_types': SMSTemplate.TEMPLATE_TYPE_CHOICES,
    }
    
    return render(request, 'sms/template_form.html', context)


@login_required
@super_admin_permission_required('sms.delete_sms_template')
@require_http_methods(["POST"])
def template_delete_view(request, template_id):
    """
    📝 حذف قالب
    """
    try:
        template = get_object_or_404(SMSTemplate, id=template_id)
        template_name = template.name
        
        # بررسی استفاده از قالب
        if SMSMessage.objects.filter(template=template).exists():
            messages.error(request, f'قالب "{template_name}" در پیام‌ها استفاده شده و قابل حذف نیست')
            return redirect('sms:template_list')
        
        template.delete()
        
        # ثبت لاگ
        ActivityLog.log_activity(
            user=request.user,
            action='DELETE',
            description=f'قالب SMS "{template_name}" حذف شد',
            severity='MEDIUM'
        )
        
        messages.success(request, f'قالب "{template_name}" با موفقیت حذف شد')
        
    except Exception as e:
        logger.error(f"SMS template delete error: {e}")
        messages.error(request, 'خطا در حذف قالب')
    
    return redirect('sms:template_list')


@login_required
@super_admin_permission_required('sms.view_sms_verifications')
def verification_list_view(request):
    """
    🔐 لیست کدهای تایید
    """
    try:
        # فیلترها
        is_used_filter = request.GET.get('is_used', '')
        phone_filter = request.GET.get('phone', '')
        
        # کوئری پایه
        verifications_qs = SMSVerification.objects.select_related('sms_message').order_by('-created_at')
        
        # اعمال فیلترها
        if is_used_filter != '':
            verifications_qs = verifications_qs.filter(is_used=is_used_filter == 'true')
        if phone_filter:
            verifications_qs = verifications_qs.filter(phone_number__icontains=phone_filter)
        
        # صفحه‌بندی
        paginator = Paginator(verifications_qs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'is_used_filter': is_used_filter,
            'phone_filter': phone_filter,
        }
        
        return render(request, 'sms/verification_list.html', context)
        
    except Exception as e:
        logger.error(f"SMS verification list error: {e}")
        messages.error(request, 'خطا در بارگذاری لیست کدهای تایید')
        return redirect('sms:dashboard')


@login_required
@super_admin_permission_required('sms.change_sms_settings')
def settings_view(request):
    """
    ⚙️ تنظیمات SMS
    """
    try:
        settings_obj = SMSSettings.get_settings()
        
        if request.method == 'POST':
            # به‌روزرسانی تنظیمات
            settings_obj.sms_server_url = request.POST.get('sms_server_url', '').strip()
            settings_obj.api_key = request.POST.get('api_key', '').strip()
            settings_obj.default_sender = request.POST.get('default_sender', '').strip()
            settings_obj.verification_code_expiry = int(request.POST.get('verification_code_expiry', 10))
            settings_obj.max_verification_attempts = int(request.POST.get('max_verification_attempts', 3))
            settings_obj.enable_order_notifications = request.POST.get('enable_order_notifications') == 'on'
            settings_obj.enable_payment_notifications = request.POST.get('enable_payment_notifications') == 'on'
            settings_obj.retry_attempts = int(request.POST.get('retry_attempts', 3))
            settings_obj.timeout_seconds = int(request.POST.get('timeout_seconds', 30))
            
            settings_obj.save()
            
            # ثبت لاگ
            ActivityLog.log_activity(
                user=request.user,
                action='UPDATE',
                description='تنظیمات SMS به‌روزرسانی شد',
                content_object=settings_obj,
                severity='MEDIUM'
            )
            
            messages.success(request, 'تنظیمات SMS با موفقیت به‌روزرسانی شد')
            return redirect('sms:settings')
        
        context = {
            'settings': settings_obj,
        }
        
        return render(request, 'sms/settings.html', context)
        
    except Exception as e:
        logger.error(f"SMS settings error: {e}")
        messages.error(request, 'خطا در بارگذاری تنظیمات')
        return redirect('sms:dashboard')


@login_required
@super_admin_permission_required('sms.view_sms_statistics')
def statistics_view(request):
    """
    📊 آمار SMS
    """
    try:
        # آمار کلی
        sms_service = get_sms_service()
        stats = sms_service.get_statistics()
        
        # آمار روزانه (7 روز گذشته)
        from datetime import timedelta
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        daily_stats = []
        for i in range(7):
            date = start_date + timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_messages = SMSMessage.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            )
            
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'total': day_messages.count(),
                'successful': day_messages.filter(status='SENT').count(),
                'failed': day_messages.filter(status='FAILED').count(),
            })
        
        # آمار بر اساس نوع پیام
        message_type_stats = []
        for message_type, display_name in SMSMessage.MESSAGE_TYPE_CHOICES:
            count = SMSMessage.objects.filter(message_type=message_type).count()
            message_type_stats.append({
                'type': display_name,
                'count': count,
            })
        
        context = {
            'stats': stats,
            'daily_stats': daily_stats,
            'message_type_stats': message_type_stats,
        }
        
        return render(request, 'sms/statistics.html', context)
        
    except Exception as e:
        logger.error(f"SMS statistics error: {e}")
        messages.error(request, 'خطا در بارگذاری آمار')
        return redirect('sms:dashboard')


@login_required
@super_admin_permission_required('sms.view_sms_notifications')
def notification_list_view(request):
    """
    🔔 لیست اعلان‌ها
    """
    try:
        # فیلترها
        message_type_filter = request.GET.get('message_type', '')
        
        # کوئری پایه (فقط اعلان‌ها)
        notifications_qs = SMSMessage.objects.filter(
            message_type__in=['ORDER_STATUS', 'PAYMENT', 'NOTIFICATION']
        ).select_related('user').order_by('-created_at')
        
        # اعمال فیلترها
        if message_type_filter:
            notifications_qs = notifications_qs.filter(message_type=message_type_filter)
        
        # صفحه‌بندی
        paginator = Paginator(notifications_qs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'message_type_filter': message_type_filter,
            'notification_types': [
                ('ORDER_STATUS', '📦 وضعیت سفارش'),
                ('PAYMENT', '💳 پرداخت'),
                ('NOTIFICATION', '🔔 اطلاع‌رسانی'),
            ],
        }
        
        return render(request, 'sms/notification_list.html', context)
        
    except Exception as e:
        logger.error(f"SMS notification list error: {e}")
        messages.error(request, 'خطا در بارگذاری لیست اعلان‌ها')
        return redirect('sms:dashboard')


@login_required
@super_admin_permission_required('sms.test_sms')
def test_sms_view(request):
    """
    🧪 تست ارسال SMS
    """
    if request.method == 'POST':
        try:
            phone_number = request.POST.get('phone_number', '').strip()
            message = request.POST.get('message', '').strip()
            
            if not phone_number or not message:
                messages.error(request, 'لطفاً شماره تلفن و پیام را وارد کنید')
                return render(request, 'sms/test_sms.html')
            
            # ارسال پیام تست
            sms_service = get_sms_service()
            success, sms_message, result = sms_service.send_sms(
                phone_number=phone_number,
                message=message,
                message_type='NOTIFICATION',
                user=request.user,
                extra_data={'test': True}
            )
            
            if success:
                messages.success(request, f'پیام تست با موفقیت ارسال شد: {result}')
            else:
                messages.error(request, f'خطا در ارسال پیام تست: {result}')
            
            return render(request, 'sms/test_sms.html', {
                'test_result': {
                    'success': success,
                    'message': result,
                    'sms_message': sms_message
                }
            })
            
        except Exception as e:
            logger.error(f"SMS test error: {e}")
            messages.error(request, f'خطا در تست SMS: {str(e)}')
    
    return render(request, 'sms/test_sms.html')


@login_required
@super_admin_permission_required('sms.view_sms_health')
def health_check_view(request):
    """
    🔍 بررسی سلامت سرور SMS
    """
    try:
        # بررسی سلامت سرور
        sms_service = get_sms_service()
        server_healthy, server_status = sms_service.check_server_health()
        
        # آمار کلی
        stats = sms_service.get_statistics()
        
        context = {
            'server_healthy': server_healthy,
            'server_status': server_status,
            'stats': stats,
        }
        
        return render(request, 'sms/health_check.html', context)
        
    except Exception as e:
        logger.error(f"SMS health check error: {e}")
        messages.error(request, 'خطا در بررسی سلامت سرور SMS')
        return redirect('sms:dashboard') 