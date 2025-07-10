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
import json
import logging

from core.models import Order
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
    💰 نمایش خلاصه پرداخت قبل از انتقال به درگاه
    🎯 محاسبه و نمایش مبلغ قابل پرداخت نقدی با جزئیات کامل
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
        
        if not customer_match:
            messages.error(request, "شما اجازه مشاهده این سفارش را ندارید")
            return redirect('core:orders_list')
        
        # محاسبه مبلغ قابل پرداخت نقدی
        cash_items = order.order_items.filter(payment_method='Cash')
        total_cash_amount = sum(item.total_price for item in cash_items)
        
        if total_cash_amount <= 0:
            messages.error(request, "هیچ آیتم نقدی برای پرداخت وجود ندارد")
            return redirect('core:orders_list')
        
        # محاسبه جزئیات پرداخت
        payment_details = {
            'order': order,
            'cash_items': cash_items,
            'total_cash_amount': total_cash_amount,
            'total_cash_amount_rial': total_cash_amount * 10,
            'other_items': order.order_items.exclude(payment_method='Cash'),
            'available_gateways': [
                {'code': 'zarinpal', 'name': 'زرین‌پال', 'icon': '💎'},
                {'code': 'shaparak', 'name': 'شاپرک', 'icon': '🏦'},
            ]
        }
        
        context = {
            'payment_details': payment_details,
            'order': order,
        }
        
        return render(request, 'payments/payment_summary.html', context)
        
    except Exception as e:
        logger.error(f"Payment summary error: {e}")
        messages.error(request, "خطا در نمایش خلاصه پرداخت")
        return redirect('core:orders_list')


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
        
        if not customer_match:
            messages.error(request, "شما اجازه مشاهده این سفارش را ندارید")
            return redirect('core:orders_list')
        
        gateway = request.POST.get('gateway')
        
        # اعتبارسنجی درگاه
        if gateway not in ['zarinpal', 'shaparak']:
            messages.error(request, "درگاه پرداخت انتخابی معتبر نیست")
            return redirect('payments:payment_summary', order_id=order_id)
        
        # بررسی وجود پرداخت در حال انجام
        existing_payment = Payment.objects.filter(
            order=order,
            status__in=['INITIATED', 'REDIRECTED', 'PENDING', 'PROCESSING']
        ).first()
        
        if existing_payment:
            # اگر پرداخت منقضی شده، آن را به‌روزرسانی کن
            if existing_payment.is_expired():
                existing_payment.mark_as_expired()
            else:
                messages.warning(request, "پرداخت قبلی هنوز در حال انجام است")
                return redirect('payments:payment_status', payment_id=existing_payment.id)
        
        # ایجاد پرداخت جدید
        payment = PaymentService.create_payment_from_order(
            order=order,
            gateway_name=gateway,
            user=request.user
        )
        
        # تنظیم اطلاعات اضافی
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
            # ثبت لاگ موفقیت
            logger.info(f"Payment initiated successfully: {payment.tracking_code}")
            
            # هدایت به درگاه پرداخت
            return redirect(result['payment_url'])
        else:
            # مدیریت خطا
            error_message = result.get('error', 'خطا در ایجاد درخواست پرداخت')
            messages.error(request, f"خطا در پرداخت: {error_message}")
            
            logger.error(f"Payment initiation failed: {result}")
            return redirect('payments:payment_summary', order_id=order_id)
            
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('payments:payment_summary', order_id=order_id)
    except Exception as e:
        logger.error(f"Payment initiation error: {e}")
        messages.error(request, "خطای غیرمنتظره در شروع پرداخت")
        return redirect('payments:payment_summary', order_id=order_id)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def payment_callback(request, payment_id):
    """
    📞 پردازش کال‌بک درگاه پرداخت
    🔐 تایید پرداخت و به‌روزرسانی وضعیت
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # دریافت داده‌های callback
        if request.method == 'POST':
            callback_data = request.POST.dict()
        else:
            callback_data = request.GET.dict()
        
        # اضافه کردن IP address
        callback_data['ip_address'] = get_client_ip(request)
        
        logger.info(f"Payment callback received for {payment.tracking_code}: {callback_data}")
        
        # ثبت کال‌بک
        PaymentCallback.objects.create(
            payment=payment,
            callback_type='RETURN',
            raw_data=callback_data,
            sender_ip=callback_data.get('ip_address')
        )
        
        # تایید پرداخت
        sandbox = getattr(settings, 'PAYMENT_SANDBOX', True)
        success, result = PaymentService.verify_payment(
            payment=payment,
            verification_data=callback_data,
            sandbox=sandbox
        )
        
        if success:
            messages.success(request, "🎉 پرداخت شما با موفقیت انجام شد")
            return redirect('payments:payment_success', payment_id=payment.id)
        else:
            error_message = result.get('message', 'خطا در تایید پرداخت')
            messages.error(request, f"❌ {error_message}")
            return redirect('payments:payment_failed', payment_id=payment.id)
            
    except Exception as e:
        logger.error(f"Payment callback error: {e}")
        messages.error(request, "خطای غیرمنتظره در پردازش پرداخت")
        return redirect('core:orders_list')


def payment_success(request, payment_id):
    """
    ✅ نمایش صفحه موفقیت پرداخت
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, status='SUCCESS')
        
        # بررسی دسترسی - کاربر باید مالک پرداخت یا Super Admin باشد
        if request.user.is_authenticated:
            if (payment.user and payment.user == request.user) or request.user.is_super_admin():
                # کاربر مالک پرداخت یا Super Admin است
                pass
            else:
                # بررسی دسترسی بر اساس مشتری
                customer_match = False
                if hasattr(request.user, 'phone') and payment.order.customer.phone:
                    customer_match = request.user.phone == payment.order.customer.phone
                
                if not customer_match:
                    messages.error(request, "شما دسترسی به مشاهده این پرداخت را ندارید")
                    return redirect('core:orders_list')
        else:
            # کاربر guest - بررسی بر اساس session یا redirect به login
            messages.error(request, "برای مشاهده جزئیات پرداخت، لطفاً وارد شوید")
            return redirect('accounts:customer_sms_login')
        
        context = {
            'payment': payment,
            'order': payment.order,
        }
        
        return render(request, 'payments/payment_success.html', context)
        
    except Exception as e:
        logger.error(f"Payment success page error: {e}")
        messages.error(request, "خطا در نمایش صفحه موفقیت")
        return redirect('core:orders_list')


def payment_failed(request, payment_id):
    """
    ❌ نمایش صفحه شکست پرداخت
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # بررسی دسترسی - کاربر باید مالک پرداخت یا Super Admin باشد
        if request.user.is_authenticated:
            if (payment.user and payment.user == request.user) or request.user.is_super_admin():
                # کاربر مالک پرداخت یا Super Admin است
                pass
            else:
                # بررسی دسترسی بر اساس مشتری
                customer_match = False
                if hasattr(request.user, 'phone') and payment.order.customer.phone:
                    customer_match = request.user.phone == payment.order.customer.phone
                
                if not customer_match:
                    messages.error(request, "شما دسترسی به مشاهده این پرداخت را ندارید")
                    return redirect('core:orders_list')
        else:
            # کاربر guest - بررسی بر اساس session یا redirect به login
            messages.error(request, "برای مشاهده جزئیات پرداخت، لطفاً وارد شوید")
            return redirect('accounts:customer_sms_login')
        
        context = {
            'payment': payment,
            'order': payment.order,
            'can_retry': payment.can_retry(),
        }
        
        return render(request, 'payments/payment_failed.html', context)
        
    except Exception as e:
        logger.error(f"Payment failed page error: {e}")
        messages.error(request, "خطا در نمایش صفحه شکست پرداخت")
        return redirect('core:orders_list')


def payment_status(request, payment_id):
    """
    📊 نمایش وضعیت فعلی پرداخت
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # بررسی دسترسی - کاربر باید مالک پرداخت یا Super Admin باشد
        if request.user.is_authenticated:
            if (payment.user and payment.user == request.user) or request.user.is_super_admin():
                # کاربر مالک پرداخت یا Super Admin است
                pass
            else:
                # بررسی دسترسی بر اساس مشتری
                customer_match = False
                if hasattr(request.user, 'phone') and payment.order.customer.phone:
                    customer_match = request.user.phone == payment.order.customer.phone
                
                if not customer_match:
                    messages.error(request, "شما دسترسی به مشاهده این پرداخت را ندارید")
                    return redirect('core:orders_list')
        else:
            # کاربر guest - بررسی بر اساس session یا redirect به login
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
        logger.error(f"Payment status error: {e}")
        messages.error(request, "خطا در نمایش وضعیت پرداخت")
        return redirect('core:orders_list')


@login_required
def payment_history(request):
    """
    📋 تاریخچه پرداخت‌های کاربر
    """
    try:
        payments = Payment.objects.filter(
            user=request.user
        ).select_related('order', 'order__customer').order_by('-created_at')
        
        context = {
            'payments': payments,
        }
        
        return render(request, 'payments/payment_history.html', context)
        
    except Exception as e:
        logger.error(f"Payment history error: {e}")
        messages.error(request, "خطا در نمایش تاریخچه پرداخت‌ها")
        return redirect('core:orders_list')


@login_required
@require_POST
def retry_payment(request, payment_id):
    """
    🔄 تلاش مجدد برای پرداخت
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        if not payment.can_retry():
            messages.error(request, "امکان تلاش مجدد برای این پرداخت وجود ندارد")
            return redirect('payments:payment_failed', payment_id=payment_id)
        
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
        logger.error(f"Payment retry error: {e}")
        messages.error(request, "خطا در تلاش مجدد پرداخت")
        return redirect('payments:payment_failed', payment_id=payment_id)


# API Views for AJAX requests

@login_required
def payment_status_api(request, payment_id):
    """
    🔌 API برای بررسی وضعیت پرداخت (AJAX)
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        # بررسی انقضا
        if payment.is_expired():
            payment.mark_as_expired()
        
        return JsonResponse({
            'success': True,
            'status': payment.status,
            'status_display': payment.get_status_display_persian(),
            'tracking_code': payment.tracking_code,
            'amount': str(payment.display_amount),
            'gateway': payment.get_gateway_display_persian(),
            'created_at': payment.created_at.strftime('%Y/%m/%d %H:%M'),
            'expires_at': payment.expires_at.strftime('%Y/%m/%d %H:%M') if payment.expires_at else None,
            'can_retry': payment.can_retry(),
            'is_final': payment.status in ['SUCCESS', 'FAILED', 'CANCELLED', 'TIMEOUT', 'ERROR']
        })
        
    except Exception as e:
        logger.error(f"Payment status API error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'خطا در دریافت وضعیت پرداخت'
        }, status=500)


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
        
        # ساخت HTML ساده برای شبیه‌ساز
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🧪 شبیه‌ساز درگاه پرداخت</title>
            <style>
                body {{
                    font-family: 'Vazir', Tahoma, Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .container {{
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                }}
                .header {{
                    margin-bottom: 20px;
                }}
                .logo {{
                    font-size: 3rem;
                    margin-bottom: 10px;
                }}
                .gateway-name {{
                    font-size: 1.5rem;
                    color: #333;
                    margin-bottom: 10px;
                }}
                .test-badge {{
                    background: #ff9800;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    display: inline-block;
                }}
                .payment-info {{
                    background: #f5f5f5;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .amount {{
                    font-size: 2rem;
                    color: #4caf50;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .detail {{
                    margin: 10px 0;
                    color: #666;
                }}
                .actions {{
                    margin-top: 30px;
                }}
                .btn {{
                    padding: 15px 30px;
                    margin: 10px;
                    border: none;
                    border-radius: 8px;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: inline-block;
                    text-decoration: none;
                }}
                .btn-success {{
                    background: #4caf50;
                    color: white;
                }}
                .btn-success:hover {{
                    background: #45a049;
                    transform: translateY(-2px);
                }}
                .btn-danger {{
                    background: #f44336;
                    color: white;
                }}
                .btn-danger:hover {{
                    background: #da190b;
                    transform: translateY(-2px);
                }}
                .countdown {{
                    color: #ff9800;
                    font-weight: bold;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{'💎' if gateway == 'zarinpal' else '🏦'}</div>
                    <div class="gateway-name">{context['gateway_display']}</div>
                    <div class="test-badge">🧪 محیط تست</div>
                </div>
                
                <div class="payment-info">
                    <div class="amount">{payment.display_amount:,.0f} تومان</div>
                    <div class="detail">شماره سفارش: {payment.order.order_number}</div>
                    <div class="detail">کد پیگیری: {payment.tracking_code}</div>
                    <div class="detail">مشتری: {payment.order.customer.customer_name}</div>
                </div>
                
                <form method="post" class="actions">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                    <button type="submit" name="action" value="success" class="btn btn-success">
                        ✅ تایید پرداخت
                        </button>
                    <button type="submit" name="action" value="cancel" class="btn btn-danger">
                            ❌ لغو پرداخت
                        </button>
                    </form>
                
                <div class="countdown" id="countdown">
                    این صفحه به صورت خودکار در 60 ثانیه بسته می‌شود
                </div>
            </div>
            
            <script>
                let timeLeft = 60;
                const countdownElement = document.getElementById('countdown');
                
                const timer = setInterval(function() {{
                    timeLeft--;
                    countdownElement.textContent = `این صفحه به صورت خودکار در ${{timeLeft}} ثانیه بسته می‌شود`;
                    
                    if (timeLeft <= 0) {{
                        clearInterval(timer);
                        // Auto-cancel after timeout
                        document.querySelector('button[value="cancel"]').click();
                    }}
                }}, 1000);
                
                // تست اتوماتیک در محیط توسعه
                if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
                    setTimeout(function() {{
                        // Auto-success for testing
                        document.querySelector('button[value="success"]').click();
                    }}, 3000);
                }}
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html_content)
        
    except Exception as e:
        logger.error(f"Mock gateway error: {e}")
        return HttpResponse(f"❌ خطا در شبیه‌ساز: {str(e)}", status=500)
