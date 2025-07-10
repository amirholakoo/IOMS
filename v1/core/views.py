"""
🏢 ویوهای اصلی کسب‌وکار - HomayOMS
📊 داشبوردها و عملیات اصلی سیستم
📦 مدیریت محصولات و سیستم لاگ‌گیری
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from accounts.permissions import check_user_permission, super_admin_permission_required
from .models import Customer, Product, ActivityLog, Order, OrderItem, WorkingHours
from accounts.models import User
from payments.models import Payment
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.urls import reverse
from django.contrib.auth import authenticate, login
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import base64
import requests


def get_client_ip(request):
    """🌐 دریافت آدرس IP کلاینت"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def admin_dashboard_view(request):
    """📊 داشبورد مدیریت"""
    
    # 🔐 بررسی دسترسی - Super Admin دسترسی کامل دارد، Admin محدود
    if not (request.user.is_super_admin() or request.user.is_admin()):
        return render(request, 'accounts/permission_denied.html', {
            'title': '🚫 عدم دسترسی',
            'message': 'این صفحه فقط برای مدیران سیستم قابل دسترسی است.'
        })
    
    # 📜 ثبت لاگ مشاهده داشبورد
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده داشبورد مدیریت',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # 📊 آمار کلی
    stats = {
        'total_customers': Customer.objects.count(),
        'total_products': Product.objects.count(),
        'available_products': Product.objects.filter(status='In-stock').count(),
        'sold_products': Product.objects.filter(status='Sold').count(),
        'recent_activities': ActivityLog.objects.select_related('user')[:10]
    }
    
    # 💰 Super Admin هیچ محدودیتی ندارد
    products_for_price_management = None
    if request.user.is_super_admin():  # Super Admin همیشه دسترسی دارد
        products_for_price_management = Product.objects.filter(
            status='In-stock'
        ).order_by('-created_at')[:20]  # آخرین 20 محصول
    
    context = {
        'title': '📊 داشبورد مدیریت',
        'user': request.user,
        'stats': stats,
        'products_for_price_management': products_for_price_management,
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required  
@check_user_permission('is_finance')
def finance_dashboard_view(request):
    """💰 داشبورد مالی"""
    
    # 📜 ثبت لاگ مشاهده داشبورد مالی
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده داشبورد مالی',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # 💰 آمار مالی
    financial_stats = {
        'total_products_value': Product.objects.aggregate(Sum('price'))['price__sum'] or 0,
        'in_stock_products': Product.objects.filter(status='In-stock').count(),
        'sold_products_count': Product.objects.filter(status='Sold').count(),
        'total_orders': Order.objects.count(),
    }
    
    context = {
        'title': '💰 داشبورد مالی',
        'user': request.user,
        'financial_stats': financial_stats,
    }
    return render(request, 'core/finance_dashboard.html', context)


@login_required
@super_admin_permission_required('manage_inventory')
def inventory_list_view(request):
    """📦 لیست موجودی"""
    
    # 📜 ثبت لاگ مشاهده موجودی
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لیست موجودی',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    context = {'title': '📦 مدیریت موجودی'}
    return render(request, 'core/inventory_list.html', context)


@login_required
@super_admin_permission_required('manage_orders')
def orders_list_view(request):
    """📋 لیست سفارشات با فیلتر و جستجو"""
    
    # 📜 ثبت لاگ مشاهده سفارشات
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لیست سفارشات',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # شروع با تمام سفارشات
    orders = Order.objects.select_related('customer', 'created_by').prefetch_related('order_items')
    
    # دریافت پارامترهای فیلتر از URL
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    payment_filter = request.GET.get('payment', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    
    # اعمال فیلتر جستجو
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer__customer_name__icontains=search_query) |
            Q(customer__phone__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # اعمال فیلتر وضعیت
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # اعمال فیلتر نوع پرداخت
    if payment_filter:
        orders = orders.filter(payment_method=payment_filter)
    
    # اعمال فیلتر تاریخ
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=to_date)
        except ValueError:
            pass
    
    # مرتب‌سازی
    orders = orders.order_by('-created_at')
    
    # 📄 صفحه‌بندی
    paginator = Paginator(orders, 25)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # 💳 اضافه کردن اطلاعات پرداخت برای هر سفارش
    for order in page_obj:
        # دریافت آخرین پرداخت مربوط به این سفارش
        order.latest_payment = Payment.objects.filter(order=order).order_by('-created_at').first()
    
    context = {
        'title': '📋 مدیریت سفارشات',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_METHOD_CHOICES,
        'total_orders': orders.count(),
    }
    return render(request, 'core/orders_list.html', context)


@login_required
@super_admin_permission_required('manage_customers')
def customers_list_view(request):
    """👥 لیست مشتریان با فیلتر و جستجو"""
    
    # 📜 ثبت لاگ مشاهده مشتریان
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لیست مشتریان',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # شروع با تمام مشتریان
    customers = Customer.objects.all()
    
    # دریافت پارامترهای فیلتر از URL
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # اعمال فیلتر جستجو
    if search_query:
        customers = customers.filter(
            Q(customer_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(national_id__icontains=search_query) |
            Q(economic_code__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # اعمال فیلتر وضعیت
    if status_filter:
        customers = customers.filter(status=status_filter)
    
    # مرتب‌سازی
    customers = customers.order_by('-created_at')
    
    # 📄 صفحه‌بندی
    paginator = Paginator(customers, 25)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'title': '👥 مدیریت مشتریان',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Customer.STATUS_CHOICES,
        'total_customers': customers.count(),
    }
    return render(request, 'core/customers_list.html', context)


@login_required
@check_user_permission('is_finance')
def finance_overview_view(request):
    """💰 نمای کلی مالی"""
    
    # 📜 ثبت لاگ مشاهده نمای کلی مالی
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده نمای کلی مالی',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    context = {'title': '💰 نمای کلی مالی'}
    return render(request, 'core/finance_overview.html', context)


@login_required
@super_admin_permission_required('manage_inventory')
def products_list_view(request):
    """📦 لیست محصولات"""
    
    # 📜 ثبت لاگ مشاهده محصولات
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لیست محصولات',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # 🔍 فیلترها و جستجو
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    status_filter = request.GET.get('status', '')
    
    products = Product.objects.all()
    
    # 🔍 اعمال فیلترها
    if search_query:
        products = products.filter(
            Q(reel_number__icontains=search_query) |
            Q(grade__icontains=search_query) |
            Q(qr_code__icontains=search_query)
        )
    
    if location_filter:
        products = products.filter(location=location_filter)
    
    if status_filter:
        products = products.filter(status=status_filter)
    
    # 📊 آمار محصولات
    products_stats = {
        'total_count': products.count(),
        'total_area': sum(p.get_total_area() for p in products),
        'total_weight': sum(p.get_total_weight() for p in products),
        'location_stats': products.values('location').annotate(count=Count('id')),
        'status_stats': products.values('status').annotate(count=Count('id')),
    }
    
    # 📄 صفحه‌بندی
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'title': '📦 مدیریت محصولات',
        'products': products,
        'products_stats': products_stats,
        'search_query': search_query,
        'location_filter': location_filter,
        'status_filter': status_filter,
        'location_choices': Product.LOCATION_CHOICES,
        'status_choices': Product.STATUS_CHOICES,
    }
    return render(request, 'core/products_list.html', context)


@login_required
@super_admin_permission_required('manage_inventory')
def product_detail_view(request, product_id):
    """📦 جزئیات محصول"""
    
    product = get_object_or_404(Product, id=product_id)
    
    # 📜 ثبت لاگ مشاهده جزئیات محصول
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description=f'مشاهده جزئیات محصول {product.reel_number}',
        content_object=product,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # 📜 تاریخچه فعالیت‌های این محصول
    product_logs = ActivityLog.objects.filter(
        content_type__model='product',
        object_id=product.id
    ).select_related('user')[:20]
    
    context = {
        'title': f'📦 جزئیات محصول {product.reel_number}',
        'product': product,
        'product_info': product.get_product_info(),
        'product_logs': product_logs,
    }
    return render(request, 'core/product_detail.html', context)


@login_required
@check_user_permission('is_admin')
def activity_logs_view(request):
    """📜 مشاهده لاگ‌های فعالیت"""
    
    # 📜 ثبت لاگ مشاهده لاگ‌ها
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لاگ‌های فعالیت سیستم',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='MEDIUM'
    )
    
    # 🔍 فیلترها
    action_filter = request.GET.get('action', '')
    severity_filter = request.GET.get('severity', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # شروع با تمام لاگ‌ها
    logs = ActivityLog.objects.select_related('user', 'content_type').order_by('-created_at')
    
    # 🔍 اعمال فیلترها
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if severity_filter:
        logs = logs.filter(severity=severity_filter)
    
    if user_filter:
        logs = logs.filter(
            Q(user__username__icontains=user_filter) |
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter)
        )
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__lte=to_date)
        except ValueError:
            pass
    
    if search_query:
        logs = logs.filter(
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(ip_address__icontains=search_query) |
            Q(user_agent__icontains=search_query)
        )
    
    # 📊 آمار لاگ‌ها
    total_logs = logs.count()
    today_logs = logs.filter(created_at__date=timezone.now().date()).count()
    
    logs_stats = {
        'total_count': total_logs,
        'today_count': today_logs,
        'action_stats': logs.values('action').annotate(count=Count('id')).order_by('-count')[:10],
        'severity_stats': logs.values('severity').annotate(count=Count('id')).order_by('-count'),
        'user_stats': logs.values('user__username').annotate(count=Count('id')).order_by('-count')[:10],
        'daily_stats': logs.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('-day')[:7],
        'recent_actions': logs.values('action', 'description', 'created_at')[:5]
    }
    
    # 📄 صفحه‌بندی
    paginator = Paginator(logs, 25)  # 25 لاگ در هر صفحه
    page = request.GET.get('page')
    logs_page = paginator.get_page(page)
    
    context = {
        'title': '📜 لاگ‌های فعالیت سیستم',
        'logs': logs_page,
        'logs_stats': logs_stats,
        'action_filter': action_filter,
        'severity_filter': severity_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'action_choices': ActivityLog.ACTION_CHOICES,
        'severity_choices': ActivityLog.SEVERITY_CHOICES,
        'total_pages': paginator.num_pages,
        'current_page': logs_page.number,
    }
    return render(request, 'core/activity_logs.html', context)


@login_required
def dashboard_stats_api(request):
    """📊 API آمار داشبورد"""
    
    # 📜 ثبت لاگ استفاده از API
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='درخواست آمار داشبورد از API',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # 📊 محاسبه آمار
    stats = {
        'customers': {
            'total': Customer.objects.count(),
            'active': Customer.objects.filter(status='Active').count(),
        },
        'products': {
            'total': Product.objects.count(),
            'in_stock': Product.objects.filter(status='In-stock').count(),
            'sold': Product.objects.filter(status='Sold').count(),
            'pre_order': Product.objects.filter(status='Pre-order').count(),
        },
        'activities': {
            'today': ActivityLog.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
            'total': ActivityLog.objects.count(),
        }
    }
    
    # اگر درخواست برای مدیریت قیمت باشد، اطلاعات محصولات را اضافه کن
    search = request.GET.get('search', '')
    location = request.GET.get('location', '')
    
    products_query = Product.objects.all().order_by('-created_at')
    
    if search:
        products_query = products_query.filter(
            Q(reel_number__icontains=search) |
            Q(grade__icontains=search)
        )
    
    if location:
        products_query = products_query.filter(location=location)
    
    # محدود کردن به 20 محصول برای عملکرد بهتر
    products_data = []
    for product in products_query[:20]:
        products_data.append({
            'id': product.id,
            'reel_number': product.reel_number,
            'grade': product.grade,
            'location': product.location,
            'location_display': product.get_location_display(),
            'status': product.status,
            'status_display': product.get_status_display(),
            'price': float(product.price),
            'price_updated_at': product.price_updated_at.strftime('%Y/%m/%d %H:%M') if product.price_updated_at else 'نامشخص',
            'payment_status': product.payment_status,
        })
    
    stats['products_list'] = products_data
    
    return JsonResponse(stats)


@login_required
@check_user_permission('is_super_admin')
@require_http_methods(["POST"])
def update_price_api(request):
    """💰 API بروزرسانی قیمت محصول (فقط Super Admin)"""
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        new_price = data.get('new_price')
        
        if not product_id or new_price is None:
            return JsonResponse({
                'success': False,
                'message': 'اطلاعات ناقص ارسال شده است'
            })
        
        if new_price < 0:
            return JsonResponse({
                'success': False,
                'message': 'قیمت نمی‌تواند منفی باشد'
            })
        
        # دریافت محصول
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'محصول مورد نظر یافت نشد'
            })
        
        # ذخیره قیمت قبلی برای لاگ
        old_price = product.price
        
        # بروزرسانی قیمت
        product.price = new_price
        product.price_updated_at = timezone.now()
        product.price_updated_by = request.user
        product.save()
        
        # ثبت لاگ تغییر قیمت
        ActivityLog.log_activity(
            user=request.user,
            action='PRICE_UPDATE',
            description=f'تغییر قیمت محصول {product.reel_number} از {old_price:,.0f} به {new_price:,.0f} تومان',
            content_object=product,
            severity='HIGH',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            old_price=float(old_price),
            new_price=float(new_price),
            price_change=float(new_price - old_price)
        )
        
        return JsonResponse({
            'success': True,
            'message': f'قیمت محصول {product.reel_number} با موفقیت به {new_price:,.0f} تومان بروزرسانی شد',
            'product': {
                'id': product.id,
                'reel_number': product.reel_number,
                'old_price': float(old_price),
                'new_price': float(new_price),
                'updated_at': product.price_updated_at.strftime('%Y/%m/%d %H:%M')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'فرمت داده‌های ارسالی نامعتبر است'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'خطای داخلی سرور'
        })


# 📱 API endpoint برای دریافت اطلاعات محصول با QR کد
@login_required
def product_qr_api(request, qr_code):
    """📱 API دریافت اطلاعات محصول با QR کد"""
    
    try:
        product = Product.objects.get(qr_code=qr_code)
        
        # 📜 ثبت لاگ اسکن QR کد
        ActivityLog.log_activity(
            user=request.user,
            action='VIEW',
            description=f'اسکن QR کد محصول {product.reel_number}',
            content_object=product,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='LOW',
            scan_method='QR_CODE'
        )
        
        return JsonResponse({
            'success': True,
            'product': product.get_product_info()
        })
        
    except Product.DoesNotExist:
        # 📜 ثبت لاگ QR کد نامعتبر
        ActivityLog.log_activity(
            user=request.user,
            action='ERROR',
            description=f'تلاش برای اسکن QR کد نامعتبر: {qr_code}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='MEDIUM',
            invalid_qr_code=qr_code
        )
        
        return JsonResponse({
            'success': False,
            'error': 'محصول با این QR کد یافت نشد'
        }, status=404)


@login_required
@check_user_permission('is_super_admin')
def working_hours_management_view(request):
    """
    ⏰ مدیریت ساعات کاری فروشگاه - فقط Super Admin
    
    👑 این صفحه فقط برای Super Admin قابل دسترسی است
    🕐 امکان تنظیم ساعات شروع و پایان کار
    📋 نمایش وضعیت فعلی فروشگاه
    """
    
    # 📜 ثبت لاگ دسترسی
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده پنل مدیریت ساعات کاری',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='MEDIUM'
    )
    
    # ⏰ دریافت ساعات کاری فعلی
    current_working_hours = WorkingHours.get_current_working_hours()
    
    # 📊 آمار ساعات کاری
    working_hours_stats = {
        'total_working_hours': WorkingHours.objects.count(),
        'active_working_hours': WorkingHours.objects.filter(is_active=True).count(),
        'is_shop_open': WorkingHours.is_shop_open(),
        'current_hours': current_working_hours.get_working_hours_info() if current_working_hours else None
    }
    
    # 📋 تاریخچه ساعات کاری
    working_hours_history = WorkingHours.objects.all().order_by('-created_at')[:10]
    
    context = {
        'title': '⏰ مدیریت ساعات کاری',
        'current_working_hours': current_working_hours,
        'working_hours_stats': working_hours_stats,
        'working_hours_history': working_hours_history,
        'user': request.user,
    }
    
    return render(request, 'core/working_hours_management.html', context)


@login_required
@check_user_permission('is_super_admin')
@require_http_methods(["POST"])
def set_working_hours_view(request):
    """
    ⏰ تنظیم ساعات کاری جدید - فقط Super Admin
    
    🎯 این API برای تنظیم ساعات کاری فروشگاه استفاده می‌شود
    ✅ فقط یک ساعت کاری می‌تواند فعال باشد
    """
    
    try:
        # 📥 دریافت داده‌ها از درخواست
        data = json.loads(request.body)
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        description = data.get('description', '')
        
        # 🧹 اعتبارسنجی داده‌ها
        if not start_time or not end_time:
            return JsonResponse({
                'success': False,
                'error': '⏰ زمان شروع و پایان کار الزامی است'
            }, status=400)
        
        # 🕐 تبدیل به فرمت زمان
        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': '⏰ فرمت زمان نامعتبر است (HH:MM)'
            }, status=400)
        
        # 🔍 بررسی منطقی بودن زمان‌ها
        if start_time_obj >= end_time_obj:
            return JsonResponse({
                'success': False,
                'error': '⏰ زمان پایان کار باید بعد از زمان شروع کار باشد'
            }, status=400)
        
        # 💾 ایجاد ساعات کاری جدید
        working_hours = WorkingHours.objects.create(
            start_time=start_time_obj,
            end_time=end_time_obj,
            description=description,
            set_by=request.user,
            is_active=True
        )
        
        # 📜 ثبت لاگ
        ActivityLog.log_activity(
            user=request.user,
            action='CREATE',
            description=f'تنظیم ساعات کاری جدید: {start_time} - {end_time}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='HIGH'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'✅ ساعات کاری با موفقیت تنظیم شد: {working_hours}',
            'working_hours': working_hours.get_working_hours_info()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '📄 فرمت JSON نامعتبر است'
        }, status=400)
    
    except Exception as e:
        # 📜 ثبت خطا
        ActivityLog.log_activity(
            user=request.user,
            action='ERROR',
            description=f'خطا در تنظیم ساعات کاری: {str(e)}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='HIGH'
        )
        
        return JsonResponse({
            'success': False,
            'error': f'❌ خطا در تنظیم ساعات کاری: {str(e)}'
        }, status=500)


def check_working_hours_middleware(view_func):
    """
    🕐 میدل‌ویر بررسی ساعات کاری
    
    🎯 این دکوریتر برای بررسی ساعات کاری فروشگاه استفاده می‌شود
    🔒 اگر فروشگاه بسته باشد، کاربران عادی نمی‌توانند به صفحات مشتری دسترسی داشته باشند
    👑 Super Admin و Admin همیشه دسترسی دارند
    """
    def wrapper(request, *args, **kwargs):
        # 👑 Super Admin و Admin همیشه دسترسی دارند
        if request.user.is_authenticated and (request.user.is_super_admin() or request.user.is_admin()):
            return view_func(request, *args, **kwargs)
        
        # 🕐 بررسی ساعات کاری برای سایر کاربران
        if not WorkingHours.is_shop_open():
            current_hours = WorkingHours.get_current_working_hours()
            
            context = {
                'title': '🔒 فروشگاه بسته است',
                'current_working_hours': current_hours,
                'time_until_open': current_hours.time_until_open() if current_hours else None,
            }
            
            return render(request, 'core/shop_closed.html', context)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# اعمال میدل‌ویر ساعات کاری به صفحات مشتری
@check_working_hours_middleware
def products_landing_view(request):
    """🛍️ صفحه اصلی محصولات"""
    
    # فقط محصولات موجود در انبار
    available_products = Product.objects.filter(status='In-stock').order_by('-created_at')
    
    # فیلترهای جستجو
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    # اعمال فیلترها
    if search_query:
        available_products = available_products.filter(
            Q(reel_number__icontains=search_query) |
            Q(grade__icontains=search_query)
        )
    
    if location_filter:
        available_products = available_products.filter(location=location_filter)
    
    if min_price:
        try:
            available_products = available_products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            available_products = available_products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # آمار کلی
    stats = {
        'total_products': available_products.count(),
        'in_stock_count': available_products.count(),
        'avg_price': available_products.aggregate(Avg('price'))['price__avg'] or 0,
        'warehouses_count': len(Product.LOCATION_CHOICES),
        'locations': Product.LOCATION_CHOICES,
    }
    
    # ثبت لاگ بازدید
    if request.user.is_authenticated:
        ActivityLog.log_activity(
            user=request.user,
            action='VIEW',
            description=f'مشاهده صفحه محصولات - {available_products.count()} محصول',
            severity='LOW',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            page='products_landing',
            products_count=available_products.count(),
            filters_applied={
                'search': search_query,
                'location': location_filter,
                'price_range': f"{min_price}-{max_price}"
            }
        )
    
    context = {
        'products': available_products,
        'stats': stats,
        'search_query': search_query,
        'location_filter': location_filter,
        'min_price': min_price,
        'max_price': max_price,
    }
    
    return render(request, 'core/products_landing.html', context)


@check_working_hours_middleware
@require_http_methods(["POST"])
def add_to_cart_view(request):
    """🛒 افزودن به سبد خرید"""
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '🔐 برای خرید محصول ابتدا وارد حساب کاربری خود شوید',
            'redirect_url': '/accounts/customer/sms-login/'
        })
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        # بررسی محصول
        try:
            product = Product.objects.get(id=product_id, status='In-stock')
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '❌ محصول مورد نظر یافت نشد یا موجود نیست'
            })
        
        # دریافت سبد خرید از session
        cart = request.session.get('cart', {})
        
        # اضافه کردن به سبد (بدون payment_method - آن را در checkout انتخاب می‌کنیم)
        cart_key = str(product_id)
        if cart_key in cart:
            cart[cart_key]['quantity'] += quantity
        else:
            cart[cart_key] = {
                'product_id': product_id,
                'product_name': product.reel_number,
                'quantity': quantity,
                'unit_price': float(product.price),
                'added_at': timezone.now().isoformat()
            }
        
        # ذخیره سبد در session
        request.session['cart'] = cart
        
        # محاسبه تعداد کل اقلام
        total_items = sum(item['quantity'] for item in cart.values())
        total_amount = sum(item['quantity'] * item['unit_price'] for item in cart.values())
        
        # ثبت لاگ
        ActivityLog.log_activity(
            user=request.user,
            action='ORDER',
            description=f'اضافه کردن {product.reel_number} به سبد خرید - تعداد: {quantity}',
            content_object=product,
            severity='LOW',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            product_id=product_id,
            quantity=quantity
        )
        
        return JsonResponse({
            'success': True,
            'message': f'✅ {product.reel_number} به سبد خرید اضافه شد',
            'cart_count': total_items,
            'cart_total': f"{total_amount:,.0f} تومان"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '❌ خطا در اضافه کردن به سبد خرید'
        })


@check_working_hours_middleware
@login_required
def cart_view(request):
    """🛒 نمایش سبد خرید"""
    
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    for cart_key, item in cart.items():
        try:
            product = Product.objects.get(id=item['product_id'])
            item_total = item['quantity'] * item['unit_price']
            cart_items.append({
                'cart_key': cart_key,
                'product': product,
                'quantity': item['quantity'],
                'unit_price': item['unit_price'],
                'total_price': item_total,
                'payment_method': item.get('payment_method', 'Cash')  # Default to Cash
            })
            total_amount += item_total
        except Product.DoesNotExist:
            # حذف محصولات غیر موجود از سبد
            del cart[cart_key]
    
    # بروزرسانی سبد
    request.session['cart'] = cart
    
    # بررسی وجود پروفایل مشتری
    try:
        # استفاده از first() به جای get() برای جلوگیری از MultipleObjectsReturned
        customer = Customer.objects.filter(
            customer_name=request.user.get_full_name() or request.user.username
        ).first()
        
        # اگر مشتری پیدا نشد، سعی کن با شماره تلفن پیدا کن
        if not customer and request.user.phone:
            customer = Customer.objects.filter(phone=request.user.phone).first()
            
    except Exception as e:
        customer = None
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_count': len(cart_items),
        'customer': customer,
        'payment_methods': Order.PAYMENT_METHOD_CHOICES,
    }
    
    return render(request, 'core/cart.html', context)


@check_working_hours_middleware
@login_required
@require_http_methods(["POST"])
def checkout_view(request):
    """💳 تکمیل خرید"""
    
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, '🛒 سبد خرید شما خالی است')
        return redirect('core:products_landing')
    
    try:
        # پیدا کردن یا ایجاد پروفایل مشتری با استفاده از نام و شماره تلفن
        customer_name = request.user.get_full_name() or request.user.username
        customer_phone = request.user.phone
        
        # ابتدا سعی کن با نام و شماره تلفن پیدا کن
        if customer_phone:
            customer = Customer.objects.filter(
                customer_name=customer_name,
                phone=customer_phone
            ).first()
        else:
            # اگر شماره تلفن نبود، فقط با نام پیدا کن
            customer = Customer.objects.filter(customer_name=customer_name).first()
        
        # اگر مشتری پیدا نشد، ایجاد کن
        if not customer:
            try:
                customer = Customer.objects.create(
                    customer_name=customer_name,
                    phone=customer_phone or '',
                    status='Active',
                    comments=f'🔵 پروفایل خودکار ایجاد شده برای کاربر: {request.user.username}'
                )
            except Exception as e:
                # اگر خطای unique constraint رخ داد، سعی کن مشتری موجود را پیدا کن
                if 'UNIQUE constraint failed' in str(e):
                    customer = Customer.objects.filter(customer_name=customer_name).first()
                    if not customer:
                        raise e
                else:
                    raise e
        
        # محاسبه مبلغ کل سفارش
        total_amount = 0
        for cart_key, item in cart.items():
            total_amount += item['quantity'] * item['unit_price']
        
        # ایجاد سفارش
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',  # پیش‌فرض - حالا در OrderItem نوع واقعی ذخیره می‌شود
            total_amount=total_amount,  # تنظیم مبلغ کل
            notes=request.POST.get('notes', ''),
            delivery_address=request.POST.get('delivery_address', ''),
            created_by=request.user
        )
        
        # اضافه کردن اقلام به سفارش
        for cart_key, item in cart.items():
            try:
                product = Product.objects.get(id=item['product_id'], status='In-stock')
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    payment_method=item.get('payment_method', 'Cash')  # استفاده از payment_method آیتم
                )
                
                # تغییر وضعیت محصول به فروخته شده
                product.status = 'Sold'
                product.save()
                
            except Product.DoesNotExist:
                continue
        
        # پاک کردن سبد خرید
        request.session['cart'] = {}
        request.session.save()  # اطمینان از ذخیره session
        
        # ثبت لاگ
        ActivityLog.log_activity(
            user=request.user,
            action='ORDER',
            description=f'ایجاد سفارش جدید {order.order_number} - مبلغ: {order.final_amount:,.0f} تومان',
            content_object=order,
            severity='HIGH',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            order_number=order.order_number,
            total_amount=float(order.final_amount),
            items_count=order.get_order_items_count()
        )
        
        # Check if order has cash items - redirect to payment instead of waiting for confirmation
        cash_items = order.order_items.filter(payment_method='Cash')
        has_cash_items = cash_items.exists()
        
        if has_cash_items:
            # Calculate cash amount
            cash_amount = sum(item.total_price for item in cash_items)
            
            # Change order status to Confirmed (no manager confirmation needed)
            order.status = 'Confirmed'
            order.save()
            
            messages.success(request, f'🎉 سفارش شما با شماره {order.order_number} ثبت شد')
            messages.info(request, f'💰 لطفاً برای پرداخت مبلغ {cash_amount:,.0f} تومان ادامه دهید')
            
            # Redirect to payment summary for cash items
            return redirect('payments:payment_summary', order_id=order.id)
        else:
            # No cash items - keep existing behavior 
            messages.success(request, f'🎉 سفارش شما با شماره {order.order_number} ثبت شد')
            return redirect('core:order_detail', order_id=order.id)
        
    except Exception as e:
        import traceback
        print(f"❌ خطا در checkout_view: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        messages.error(request, f'❌ خطا در ثبت سفارش: {str(e)}')
        return redirect('core:cart')


@login_required
def order_detail_view(request, order_id):
    """
    📋 جزئیات سفارش
    👁️ نمایش اطلاعات کامل سفارش
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # بررسی دسترسی
        if request.user.role == User.UserRole.CUSTOMER:
            # مشتریان فقط سفارشات خودشان را ببینند
            # استفاده از نام کاربری یا نام کامل برای مقایسه
            user_identifier = request.user.get_full_name() or request.user.username
            if order.customer.customer_name != user_identifier:
                # اگر نام مطابقت نداشت، سعی کن با شماره تلفن چک کن
                if order.customer.phone != request.user.phone:
                    messages.error(request, '❌ شما اجازه مشاهده این سفارش را ندارید')
                    return redirect('accounts:customer_dashboard')
        
        # ثبت لاگ مشاهده
        ActivityLog.log_activity(
            user=request.user,
            action='VIEW',
            description=f'مشاهده جزئیات سفارش {order.order_number}',
            content_object=order,
            severity='LOW',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            order_number=order.order_number
        )
        
        context = {
            'order': order,
            'order_items': order.order_items.all(),
            'can_cancel': order.can_be_cancelled(),
            'can_modify': order.can_be_modified(),
            'user': request.user,
        }
        
        return render(request, 'core/order_detail.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, '❌ سفارش مورد نظر یافت نشد')
        return redirect('accounts:customer_dashboard')


@login_required
@require_http_methods(["POST"])
def update_cart_quantity_view(request):
    """
    🔄 تغییر تعداد محصول در سبد خرید
    """
    try:
        data = json.loads(request.body)
        cart_key = data.get('cart_key')
        change = int(data.get('change', 0))
        
        cart = request.session.get('cart', {})
        
        if cart_key in cart:
            new_quantity = cart[cart_key]['quantity'] + change
            
            if new_quantity <= 0:
                # Remove item if quantity becomes 0 or negative
                del cart[cart_key]
                message = '❌ محصول از سبد خرید حذف شد'
            else:
                cart[cart_key]['quantity'] = new_quantity
                message = '✅ تعداد محصول به‌روزرسانی شد'
            
            request.session['cart'] = cart
            
            return JsonResponse({
                'success': True,
                'message': message
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '❌ محصول در سبد خرید یافت نشد'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '❌ خطا در به‌روزرسانی سبد خرید'
        })


@login_required
@require_http_methods(["POST"])
def remove_from_cart_view(request):
    """
    🗑️ حذف محصول از سبد خرید
    """
    try:
        data = json.loads(request.body)
        cart_key = data.get('cart_key')
        
        cart = request.session.get('cart', {})
        
        if cart_key in cart:
            del cart[cart_key]
            request.session['cart'] = cart
            
            return JsonResponse({
                'success': True,
                'message': '✅ محصول از سبد خرید حذف شد'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '❌ محصول در سبد خرید یافت نشد'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '❌ خطا در حذف محصول'
        })


@login_required
@require_http_methods(["POST"])
def update_cart_payment_method_view(request):
    """
    💳 تغییر نوع پرداخت محصول در سبد خرید
    """
    try:
        data = json.loads(request.body)
        cart_key = data.get('cart_key')
        payment_method = data.get('payment_method')
        
        if not cart_key or not payment_method:
            return JsonResponse({
                'success': False,
                'message': '❌ اطلاعات ناقص ارسال شده است'
            })
        
        # بررسی معتبر بودن payment method
        valid_methods = [choice[0] for choice in OrderItem.PAYMENT_METHOD_CHOICES]
        if payment_method not in valid_methods:
            return JsonResponse({
                'success': False,
                'message': '❌ نوع پرداخت انتخابی معتبر نیست'
            })
        
        cart = request.session.get('cart', {})
        
        if cart_key in cart:
            cart[cart_key]['payment_method'] = payment_method
            request.session['cart'] = cart
            
            return JsonResponse({
                'success': True,
                'message': '✅ نوع پرداخت به‌روزرسانی شد'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '❌ محصول در سبد خرید یافت نشد'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '❌ فرمت داده‌های ارسالی نامعتبر است'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': '❌ خطا در به‌روزرسانی نوع پرداخت'
        })


@login_required
@super_admin_permission_required('manage_orders')
@require_http_methods(["POST"])
def confirm_order_view(request, order_id):
    """✅ تایید سفارش توسط Super Admin"""
    
    try:
        order = Order.objects.get(id=order_id)
        
        # بررسی اینکه سفارش در وضعیت "در انتظار تایید" باشد
        if order.status != 'Pending':
            messages.error(request, f'❌ سفارش {order.order_number} در وضعیت قابل تایید نیست.')
            return JsonResponse({
                'success': False,
                'message': f'سفارش {order.order_number} در وضعیت قابل تایید نیست.'
            })
        
        # تغییر وضعیت به "تایید شده"
        old_status = order.status
        order.status = 'Confirmed'
        order.save()
        
        # 📜 ثبت لاگ تایید سفارش
        ActivityLog.log_activity(
            user=request.user,
            action='APPROVE',
            description=f'تایید سفارش {order.order_number} توسط {request.user.username}',
            content_object=order,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='MEDIUM',
            extra_data={
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': order.status,
                'customer_name': order.customer.customer_name,
                'final_amount': str(order.final_amount)
            }
        )
        
        messages.success(request, f'✅ سفارش {order.order_number} با موفقیت تایید شد.')
        
        return JsonResponse({
            'success': True,
            'message': f'سفارش {order.order_number} با موفقیت تایید شد.',
            'new_status': order.get_status_display(),
            'order_id': order.id
        })
        
    except Order.DoesNotExist:
        messages.error(request, '❌ سفارش مورد نظر یافت نشد.')
        return JsonResponse({
            'success': False,
            'message': 'سفارش مورد نظر یافت نشد.'
        })
    except Exception as e:
        messages.error(request, f'❌ خطا در تایید سفارش: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'خطا در تایید سفارش: {str(e)}'
        })


@login_required
@super_admin_permission_required('manage_orders')
@require_http_methods(["POST"])
def cancel_order_view(request, order_id):
    """❌ لغو سفارش توسط Super Admin"""
    
    try:
        order = Order.objects.get(id=order_id)
        
        # بررسی اینکه سفارش قابل لغو باشد
        if order.status in ['Delivered', 'Cancelled', 'Returned']:
            messages.error(request, f'❌ سفارش {order.order_number} قابل لغو نیست.')
            return JsonResponse({
                'success': False,
                'message': f'سفارش {order.order_number} قابل لغو نیست.'
            })
        
        # تغییر وضعیت به "لغو شده"
        old_status = order.status
        order.status = 'Cancelled'
        order.save()
        
        # 📜 ثبت لاگ لغو سفارش
        ActivityLog.log_activity(
            user=request.user,
            action='CANCEL',
            description=f'لغو سفارش {order.order_number} توسط {request.user.username}',
            content_object=order,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='HIGH',
            extra_data={
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': order.status,
                'customer_name': order.customer.customer_name,
                'final_amount': str(order.final_amount)
            }
        )
        
        messages.success(request, f'❌ سفارش {order.order_number} با موفقیت لغو شد.')
        
        return JsonResponse({
            'success': True,
            'message': f'سفارش {order.order_number} با موفقیت لغو شد.',
            'new_status': order.get_status_display(),
            'order_id': order.id
        })
        
    except Order.DoesNotExist:
        messages.error(request, '❌ سفارش مورد نظر یافت نشد.')
        return JsonResponse({
            'success': False,
            'message': 'سفارش مورد نظر یافت نشد.'
        })
    except Exception as e:
        messages.error(request, f'❌ خطا در لغو سفارش: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'خطا در لغو سفارش: {str(e)}'
        })


@login_required
@super_admin_permission_required('manage_orders')
@require_http_methods(["POST"])
def update_order_status_view(request, order_id):
    """📊 تغییر وضعیت سفارش توسط Super Admin"""
    
    try:
        order = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        
        if not new_status:
            return JsonResponse({
                'success': False,
                'message': 'وضعیت جدید مشخص نشده است.'
            })
        
        # بررسی معتبر بودن وضعیت جدید
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'message': 'وضعیت نامعتبر است.'
            })
        
        # تغییر وضعیت
        old_status = order.status
        order.status = new_status
        order.save()
        
        # 📜 ثبت لاگ تغییر وضعیت
        ActivityLog.log_activity(
            user=request.user,
            action='UPDATE',
            description=f'تغییر وضعیت سفارش {order.order_number} از {old_status} به {new_status} توسط {request.user.username}',
            content_object=order,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='MEDIUM',
            extra_data={
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': new_status,
                'customer_name': order.customer.customer_name,
                'final_amount': str(order.final_amount)
            }
        )
        
        messages.success(request, f'📊 وضعیت سفارش {order.order_number} به {order.get_status_display()} تغییر یافت.')
        
        return JsonResponse({
            'success': True,
            'message': f'وضعیت سفارش {order.order_number} با موفقیت تغییر یافت.',
            'new_status': order.get_status_display(),
            'order_id': order.id
        })
        
    except Order.DoesNotExist:
        messages.error(request, '❌ سفارش مورد نظر یافت نشد.')
        return JsonResponse({
            'success': False,
            'message': 'سفارش مورد نظر یافت نشد.'
        })
    except Exception as e:
        messages.error(request, f'❌ خطا در تغییر وضعیت سفارش: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'خطا در تغییر وضعیت سفارش: {str(e)}'
        })


@login_required
def customer_orders_view(request):
    """📋 لیست سفارشات مشتری با جزئیات پرداخت"""
    
    # فقط کاربران با نقش مشتری می‌توانند دسترسی داشته باشند
    if request.user.role != User.UserRole.CUSTOMER:
        messages.error(request, '❌ دسترسی مجاز نیست')
        return redirect('accounts:dashboard')
    
    # 📜 ثبت لاگ مشاهده سفارشات
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لیست سفارشات توسط مشتری',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
    # دریافت سفارشات مربوط به مشتری فعلی
    user_name = request.user.get_full_name() or request.user.username
    user_phone = request.user.phone
    
    # جستجوی سفارشات بر اساس نام یا شماره تلفن
    orders = Order.objects.select_related('customer', 'created_by').prefetch_related('order_items')
    
    if user_phone:
        orders = orders.filter(
            Q(customer__phone=user_phone) |
            Q(customer__customer_name__icontains=user_name.strip())
        )
    else:
        orders = orders.filter(customer__customer_name__icontains=user_name.strip())
    
    # دریافت پارامترهای فیلتر از URL
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    payment_filter = request.GET.get('payment', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    
    # اعمال فیلترها
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if payment_filter:
        orders = orders.filter(payment_method=payment_filter)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=to_date)
        except ValueError:
            pass
    
    # مرتب‌سازی
    orders = orders.order_by('-created_at')
    
    # 📄 صفحه‌بندی
    paginator = Paginator(orders, 10)  # کمتر برای مشتریان
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # 💳 اضافه کردن اطلاعات پرداخت برای هر سفارش
    for order in page_obj:
        order.latest_payment = Payment.objects.filter(order=order).order_by('-created_at').first()
        order.all_payments = Payment.objects.filter(order=order).order_by('-created_at')
        # Add flag for cash items
        order.has_cash_items = order.order_items.filter(payment_method='Cash').exists()
    
    context = {
        'title': '📋 سفارشات من',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_METHOD_CHOICES,
        'total_orders': orders.count(),
    }
    return render(request, 'core/customer_orders.html', context)
