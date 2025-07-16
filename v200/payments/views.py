from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from datetime import datetime
import json
import logging

from core.models import Order
from accounts.models import User
from .models import Payment, PaymentCallback
from .services import PaymentService, PaymentGatewayError

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """دریافت IP آدرس کاربر"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def payment_summary(request, order_id):
    """
    💰 نمایش خلاصه پرداخت
    📋 نمایش جزئیات سفارش و انتخاب درگاه پرداخت
    """
    try:
        # دریافت سفارش
        order = get_object_or_404(Order, id=order_id)
        
        # بررسی دسترسی - کاربر باید مالک سفارش یا Super Admin باشد
        if not request.user.is_super_admin():
            # بررسی دسترسی بر اساس مشتری
            customer_match = False
            if hasattr(request.user, 'phone') and order.customer.phone:
                customer_match = request.user.phone == order.customer.phone
            
            if not customer_match:
                messages.error(request, "شما اجازه مشاهده این سفارش را ندارید")
                return render(request, 'payments/payment_summary.html', {'order': order})
        
        # بررسی وضعیت سفارش
        if order.status not in ['Pending', 'Processing']:
            messages.warning(request, f"وضعیت سفارش '{order.get_status_display()}' - ممکن است آماده پرداخت نباشد")
        
        # محاسبه اقلام نقدی - اگر سفارش Cash است، همه اقلام را Cash در نظر بگیر
        if order.payment_method == 'Cash':
            # برای سفارش نقدی، همه اقلام قابل پرداخت هستند
            cash_items = order.order_items.all()
        else:
            # برای سفارشات مختلط، فقط اقلام با payment_method='Cash'
            cash_items = order.order_items.filter(payment_method='Cash')
        
        total_cash_amount = sum(item.total_price for item in cash_items)
        
        # Debug information (only show for admins or in development)
        if request.user.is_super_admin():
            logger.info(f"Payment Summary Debug - Order {order.id}: payment_method={order.payment_method}, "
                       f"items_count={order.order_items.count()}, cash_items_count={cash_items.count()}, "
                       f"total_cash_amount={total_cash_amount}")
        
        # محاسبه جزئیات پرداخت
        # برای other_items، اگر سفارش Cash است، هیچ آیتم دیگری نیست
        if order.payment_method == 'Cash':
            other_items = order.order_items.none()  # Empty queryset
        else:
            other_items = order.order_items.exclude(payment_method='Cash')
        
        payment_details = {
            'order': order,
            'cash_items': cash_items,
            'total_cash_amount': total_cash_amount,
            'total_cash_amount_rial': total_cash_amount * 10,
            'other_items': other_items,
            'available_gateways': [
                {'code': 'zarinpal', 'name': 'زرین‌پال', 'icon': '💎'},
                {'code': 'shaparak', 'name': 'شاپرک', 'icon': '🏦'},
            ]
        }
        
        # Add helpful message if no cash items
        if total_cash_amount <= 0:
            if cash_items.count() == 0:
                messages.info(request, "هیچ آیتم نقدی در این سفارش وجود ندارد")
            else:
                messages.warning(request, "مبلغ اقلام نقدی صفر است - لطفاً با پشتیبانی تماس بگیرید")
        else:
            # Welcome message for returning customers
            messages.success(request, f"🎉 خوش آمدید! شما برای تکمیل پرداخت سفارش {order.order_number} بازگشته‌اید.")
        
        context = {
            'payment_details': payment_details,
            'order': order,
        }
        
        return render(request, 'payments/payment_summary.html', context)
        
    except Exception as e:
        logger.error(f"Payment summary error: {e}")
        messages.error(request, "خطا در نمایش خلاصه پرداخت")
        return render(request, 'payments/payment_summary.html', {'order': order})


@login_required
@require_POST
@transaction.atomic
def initiate_payment(request, order_id):
    """
    🚀 شروع فرآیند پرداخت
    🔐 ایجاد پرداخت و هدایت به درگاه انتخابی
    """
    try:
        # Get order with customer matching current user
        order = get_object_or_404(Order, id=order_id)
        
        # Verify customer ownership with robust matching
        user_name = (request.user.get_full_name() or request.user.username).strip().lower()
        user_phone = request.user.phone
        customer_name = order.customer.customer_name.strip().lower()
        customer_phone = order.customer.phone
        
        # Match by phone (primary) or name (secondary)
        phone_match = user_phone and customer_phone and user_phone == customer_phone
        name_match = user_name in customer_name or customer_name in user_name
        customer_match = phone_match or name_match
        
        if not customer_match and not request.user.is_super_admin():
            messages.error(request, "شما اجازه مشاهده این سفارش را ندارید")
            return render(request, 'payments/payment_summary.html', {'order': order})
        
        gateway = request.POST.get('gateway')
        
        # اعتبارسنجی درگاه
        if gateway not in ['zarinpal', 'shaparak']:
            messages.error(request, "درگاه پرداخت انتخابی معتبر نیست")
            return render(request, 'payments/payment_summary.html', {'order': order})
        
        # بررسی وجود پرداخت در حال انجام
        existing_payment = Payment.objects.filter(
            order=order,
            status__in=['INITIATED', 'REDIRECTED', 'PENDING', 'PROCESSING']
        ).first()
        
        if existing_payment:
            # اگر پرداخت منقضی شده، آن را به‌روزرسانی کن
            if existing_payment.is_expired():
                existing_payment.mark_as_expired()
            # اگر کاربر صاحب پرداخت است، اجازه ادامه بده
            elif existing_payment.user == request.user:
                return redirect('payments:payment_status', payment_id=existing_payment.id)
            else:
                messages.warning(request, "پرداخت قبلی هنوز در حال انجام است")
                return redirect('payments:payment_status', payment_id=existing_payment.id)
        
        # ایجاد پرداخت جدید
        payment = PaymentService.create_payment_from_order(
            order=order,
            gateway_name=gateway,
            user=request.user
        )
        payment.user = request.user  # Ensure linkage
        payment.user_ip = get_client_ip(request)
        payment.user_agent = request.META.get('HTTP_USER_AGENT', '')
        payment.save()
        
        # تولید URL callback
        callback_url = request.build_absolute_uri(
            reverse('payments:payment_callback', kwargs={'payment_id': payment.id})
        )
        
        # شروع فرآیند پرداخت
        sandbox = getattr(settings, 'PAYMENT_SANDBOX', True)
        result = PaymentService.initiate_payment(
            payment=payment,
            callback_url=callback_url,
            sandbox=sandbox
        )
        
        if result.get('success'):
            return redirect(result['payment_url'])
        else:
            error_message = result.get('error', 'خطا در ایجاد درخواست پرداخت')
            messages.error(request, f"خطا در پرداخت: {error_message}")
            return render(request, 'payments/payment_summary.html', {'order': order})
            
    except Exception as e:
        logger.error(f"Payment initiation error: {e}")
        messages.error(request, "خطا در شروع فرآیند پرداخت")
        return render(request, 'payments/payment_summary.html', {'order': order})


@csrf_exempt
def payment_callback(request, payment_id):
    """
    📞 پردازش callback از درگاه پرداخت
    🔄 تایید یا رد پرداخت بر اساس پاسخ درگاه
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # ثبت callback - ترکیب پارامترهای GET و POST
        callback_data = {}
        callback_data.update(dict(request.GET))
        callback_data.update(dict(request.POST))

        # Flatten values: if a value is a list, use the first item
        for k, v in callback_data.items():
            if isinstance(v, list):
                callback_data[k] = v[0]
        
        callback = PaymentCallback.objects.create(
            payment=payment,
            gateway=payment.gateway,
            received_data=callback_data,
            gateway_ip=get_client_ip(request)
        )
        
        # پردازش callback بر اساس درگاه
        if payment.gateway == 'zarinpal':
            success, result = PaymentService.verify_payment(
                payment, 
                callback_data,
                sandbox=getattr(settings, 'PAYMENT_SANDBOX', True)
            )
        elif payment.gateway == 'shaparak':
            success, result = PaymentService.verify_payment(
                payment, 
                callback_data,
                sandbox=getattr(settings, 'PAYMENT_SANDBOX', True)
            )
        else:
            success = False
            result = {'error': 'درگاه پرداخت پشتیبانی نمی‌شود'}
        
        # به‌روزرسانی وضعیت callback
        if success:
            callback.processing_status = 'SUCCESS'
            callback.processing_logs = f"پرداخت تایید شد: {result}"
        else:
            callback.processing_status = 'FAILED'
            callback.error_message = result.get('error', 'خطای نامشخص')
            callback.processing_logs = f"پرداخت ناموفق: {result}"
        
        callback.save()
        
        # 🔄 UPDATE ORDER STATUS BASED ON PAYMENT RESULT
        try:
            order = payment.order
            from core.models import ActivityLog
            
            if success:
                # Update order status to Confirmed when payment is successful
                if order.status == 'Pending':
                    order.status = 'Confirmed'
                    order.save()
                    
                    # Log the order status update
                    ActivityLog.log_activity(
                        user=payment.user,
                        action='ORDER_STATUS_UPDATE',
                        description=f'وضعیت سفارش {order.order_number} به "تایید شده" تغییر یافت پس از پرداخت موفق',
                        content_object=order,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        severity='MEDIUM',
                        extra_data={
                            'order_number': order.order_number,
                            'payment_tracking_code': payment.tracking_code,
                            'payment_amount': str(payment.display_amount),
                            'gateway': payment.gateway
                        }
                    )
            else:
                # Update order status to Cancelled when payment fails
                if order.status == 'Pending':
                    order.status = 'Cancelled'
                    order.save()

                    # Restore all products in the order to 'In-stock'
                    for item in order.order_items.all():
                        product = item.product
                        product.status = 'In-stock'
                        product.save()

                    # Log the order cancellation
                    ActivityLog.log_activity(
                        user=payment.user,
                        action='CANCEL',
                        description=f'سفارش {order.order_number} لغو شد به دلیل عدم موفقیت در پرداخت',
                        content_object=order,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        severity='HIGH',
                        extra_data={
                            'order_number': order.order_number,
                            'payment_tracking_code': payment.tracking_code,
                            'payment_amount': str(payment.display_amount),
                            'gateway': payment.gateway,
                            'failure_reason': result.get('error', 'خطای نامشخص')
                        }
                    )
                    
        except Exception as order_error:
            # Don't fail the payment if order update fails
            pass
        
        # هدایت به صفحه مناسب
        if success:
            return redirect('payments:payment_success', payment_id=payment.id)
        else:
            return redirect('payments:payment_failed', payment_id=payment.id)
            
    except Exception as e:
        return HttpResponse("خطا در پردازش callback", status=500)


def payment_success(request, payment_id):
    """
    ✅ نمایش صفحه موفقیت پرداخت
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, status='SUCCESS')
        
        # Allow if user is payment.user or order's customer
        is_owner = (payment.user and payment.user == request.user)
        user_name = (request.user.get_full_name() or request.user.username).strip().lower()
        user_phone = getattr(request.user, 'phone', None)
        customer_name = payment.order.customer.customer_name.strip().lower()
        customer_phone = payment.order.customer.phone
        phone_match = user_phone and customer_phone and user_phone == customer_phone
        name_match = user_name in customer_name or customer_name in user_name
        customer_match = phone_match or name_match
        if request.user.is_authenticated:
            if is_owner or customer_match or request.user.is_super_admin():
                pass  # allow
            else:
                messages.error(request, "شما دسترسی به مشاهده این پرداخت را ندارید")
                return redirect('accounts:customer_dashboard')
        else:
            messages.error(request, "برای مشاهده جزئیات پرداخت، لطفاً وارد شوید")
            return redirect('accounts:customer_sms_login')
        
        context = {
            'payment': payment,
            'order': payment.order,
        }
        
        return render(request, 'payments/payment_success.html', context)
        
    except Exception as e:
        messages.error(request, "خطا در نمایش صفحه موفقیت")
        if request.user.role == User.UserRole.CUSTOMER:
            return redirect('core:customer_orders')
        else:
            return redirect('core:products_landing')


def payment_failed(request, payment_id):
    """
    ❌ نمایش صفحه عدم موفقیت پرداخت
    نمایش پیام خطا و فقط یک دکمه بازگشت به صفحه اصلی
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        context = {
            'payment': payment,
            'order': payment.order,
        }
        return render(request, 'payments/payment_failed.html', context)
    except Exception as e:
        messages.error(request, "خطا در نمایش صفحه عدم موفقیت")
        return redirect('core:products_landing')


def payment_status(request, payment_id):
    """
    📊 نمایش وضعیت فعلی پرداخت
    🔒 دسترسی به پرداخت‌های ناموفق مسدود شده است
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # 🔒 SECURITY: Block access to failed payments
        if payment.status == 'FAILED':
            messages.warning(request, "دسترسی به پرداخت‌های ناموفق مسدود شده است")
            return redirect('core:products_landing')
        
        # Allow if user is payment.user or order's customer
        is_owner = (payment.user and payment.user == request.user)
        user_name = (request.user.get_full_name() or request.user.username).strip().lower()
        user_phone = getattr(request.user, 'phone', None)
        customer_name = payment.order.customer.customer_name.strip().lower()
        customer_phone = payment.order.customer.phone
        phone_match = user_phone and customer_phone and user_phone == customer_phone
        name_match = user_name in customer_name or customer_name in user_name
        customer_match = phone_match or name_match
        if request.user.is_authenticated:
            if is_owner or customer_match or request.user.is_super_admin():
                pass  # allow
            else:
                messages.error(request, "شما دسترسی به مشاهده این پرداخت را ندارید")
                return redirect('core:products_landing')
        else:
            messages.error(request, "برای مشاهده جزئیات پرداخت، لطفاً وارد شوید")
            return redirect('accounts:customer_sms_login')
        
        # بررسی انقضا
        if payment.is_expired():
            payment.mark_as_expired()
        
        context = {
            'payment': payment,
            'order': payment.order,
        }
        
        return render(request, 'payments/payment_status.html', context)
        
    except Exception as e:
        messages.error(request, "خطا در نمایش وضعیت پرداخت")
        return redirect('core:products_landing')


@login_required
def payment_history(request):
    """
    📋 تاریخچه پرداخت‌های کاربر
    """
    try:
        # Get all payments for the user (excluding failed payments)
        payments = Payment.objects.filter(
            user=request.user
        ).exclude(status='FAILED').select_related('order', 'order__customer').order_by('-created_at')
        
        # Get filter parameters
        search_query = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '').strip()
        gateway_filter = request.GET.get('gateway', '').strip()
        date_from = request.GET.get('date_from', '').strip()
        date_to = request.GET.get('date_to', '').strip()
        
        # Apply filters
        if search_query:
            payments = payments.filter(
                Q(tracking_code__icontains=search_query) |
                Q(order__order_number__icontains=search_query) |
                Q(bank_reference_number__icontains=search_query)
            )
        
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        if gateway_filter:
            payments = payments.filter(gateway=gateway_filter)
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                payments = payments.filter(created_at__date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                payments = payments.filter(created_at__date__lte=to_date)
            except ValueError:
                pass
        
        # Calculate statistics (excluding failed payments)
        total_payments = payments.count()
        completed_payments = payments.filter(status='SUCCESS').count()
        failed_payments = 0  # Failed payments are excluded from view
        total_amount = payments.filter(status='SUCCESS').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Pagination
        paginator = Paginator(payments, 15)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'status_filter': status_filter,
            'gateway_filter': gateway_filter,
            'date_from': date_from,
            'date_to': date_to,
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'failed_payments': failed_payments,
            'total_amount': total_amount,
        }
        
        return render(request, 'payments/payment_history.html', context)
        
    except Exception as e:
        messages.error(request, "خطا در نمایش تاریخچه پرداخت‌ها")
        if request.user.role == User.UserRole.CUSTOMER:
            return redirect('core:customer_orders')
        else:
            return redirect('core:products_landing')


@login_required
@require_POST
def retry_payment(request, payment_id):
    """
    🔄 تلاش مجدد برای پرداخت
    🔒 دسترسی به پرداخت‌های ناموفق مسدود شده است
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        # 🔒 SECURITY: Block retrying failed payments
        if payment.status == 'FAILED':
            messages.warning(request, "دسترسی به پرداخت‌های ناموفق مسدود شده است")
            return redirect('core:products_landing')
        
        if not payment.can_retry():
            messages.error(request, "امکان تلاش مجدد برای این پرداخت وجود ندارد")
            return redirect('core:products_landing')
        
        # افزایش تعداد تلاش
        payment.retry_count += 1
        payment.status = 'INITIATED'
        payment.error_message = ''
        payment.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        payment.save()
        
        # شروع مجدد فرآیند پرداخت
        callback_url = request.build_absolute_uri(
            reverse('payments:payment_callback', kwargs={'payment_id': payment.id})
        )
        
        sandbox = getattr(settings, 'PAYMENT_SANDBOX', True)
        result = PaymentService.initiate_payment(
            payment=payment,
            callback_url=callback_url,
            sandbox=sandbox
        )
        
        if result.get('success'):
            return redirect(result['payment_url'])
        else:
            error_message = result.get('error', 'خطا در تلاش مجدد')
            messages.error(request, f"خطا در تلاش مجدد: {error_message}")
            return redirect('payments:payment_failed', payment_id=payment_id)
            
    except Exception as e:
        messages.error(request, "خطا در تلاش مجدد پرداخت")
        return redirect('payments:payment_failed', payment_id=payment_id)


def payment_status_api(request, payment_id):
    """
    📊 API وضعیت پرداخت
    🔒 دسترسی به پرداخت‌های ناموفق مسدود شده است
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # 🔒 SECURITY: Block access to failed payments
        if payment.status == 'FAILED':
            return JsonResponse({'error': 'دسترسی به پرداخت‌های ناموفق مسدود شده است'}, status=403)
        
        # بررسی دسترسی
        if request.user.is_authenticated:
            if not ((payment.user and payment.user == request.user) or request.user.is_super_admin()):
                customer_match = False
                if hasattr(request.user, 'phone') and payment.order.customer.phone:
                    customer_match = request.user.phone == payment.order.customer.phone
                
                if not customer_match:
                    return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)
        
        # بررسی انقضا
        if payment.is_expired():
            payment.mark_as_expired()
        
        return JsonResponse({
            'tracking_code': payment.tracking_code,
            'status': payment.status,
            'status_display': payment.get_status_display_persian(),
            'amount': str(payment.display_amount),
            'gateway': payment.gateway,
            'gateway_display': payment.get_gateway_display_persian(),
            'created_at': payment.created_at.isoformat(),
            'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
            'can_retry': payment.can_retry(),
            'is_expired': payment.is_expired(),
        })
        
    except Exception as e:
        return JsonResponse({'error': 'خطا در دریافت وضعیت پرداخت'}, status=500)


@csrf_exempt
def mock_payment_gateway(request):
    """
    🧪 شبیه‌ساز درگاه پرداخت برای حالت تست
    🎯 صفحه‌ای ساده برای شبیه‌سازی پرداخت در محیط توسعه
    """
    try:
        gateway = request.GET.get('gateway')
        payment_id = request.GET.get('payment_id')
        authority = request.GET.get('authority')
        token = request.GET.get('token')
        
        if not payment_id:
            return HttpResponse("❌ پارامتر payment_id الزامی است", status=400)
        
        # دریافت پرداخت
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return HttpResponse("❌ پرداخت یافت نشد", status=404)
        
        # اگر POST است، پرداخت را پردازش کن
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'success':
                # شبیه‌سازی پرداخت موفق
                callback_url = reverse('payments:payment_callback', kwargs={'payment_id': payment.id})
                
                if gateway == 'zarinpal':
                    callback_params = f"?Status=OK&Authority={authority or payment.gateway_transaction_id}"
                else:  # shaparak
                    callback_params = f"?status=success&token={token or payment.gateway_transaction_id}"
                
                return redirect(f"{callback_url}{callback_params}")
            
            elif action == 'cancel':
                # شبیه‌سازی لغو پرداخت
                callback_url = reverse('payments:payment_callback', kwargs={'payment_id': payment.id})
                
                if gateway == 'zarinpal':
                    callback_params = f"?Status=NOK&Authority={authority or payment.gateway_transaction_id}"
                else:  # shaparak
                    callback_params = f"?status=cancelled&token={token or payment.gateway_transaction_id}"
                
                return redirect(f"{callback_url}{callback_params}")
        
        # نمایش صفحه شبیه‌ساز
        context = {
            'payment': payment,
            'gateway': gateway,
            'authority': authority,
            'token': token,
            'gateway_display': {
                'zarinpal': '💎 زرین‌پال',
                'shaparak': '🏦 شاپرک'
            }.get(gateway, gateway)
        }
        
        return render(request, 'payments/mock_gateway.html', context)
        
    except Exception as e:
        return HttpResponse(f"❌ خطا در شبیه‌ساز: {str(e)}", status=500)
