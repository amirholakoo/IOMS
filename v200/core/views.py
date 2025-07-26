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
from payments.models import Payment
from accounts.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods, require_POST
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
from django.forms import ModelForm
from django.utils.decorators import method_decorator
import logging
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import transaction
from decimal import Decimal
import re

from HomayOMS.form_mixins import NumberValidationMixin
from HomayOMS.utils import normalize_number_input, validate_number_input, NumberValidationError

logger = logging.getLogger(__name__)


class CustomerForm(ModelForm, NumberValidationMixin):
    """📝 فرم مدیریت مشتریان با اعتبارسنجی کامل"""
    class Meta:
        model = Customer
        fields = [
            'customer_name', 'phone', 'address', 'national_id', 
            'economic_code', 'postcode', 'status', 'comments'
        ]
        
    def clean_customer_name(self):
        """🔍 اعتبارسنجی یکتا بودن نام مشتری"""
        customer_name = self.cleaned_data.get('customer_name')
        if not customer_name:
            raise ValidationError('نام مشتری الزامی است')
        
        # بررسی یکتا بودن (به جز خود مشتری در صورت ویرایش)
        if self.instance.pk:
            if Customer.objects.filter(customer_name=customer_name).exclude(pk=self.instance.pk).exists():
                raise ValidationError('مشتری با این نام قبلاً ثبت شده است')
        else:
            if Customer.objects.filter(customer_name=customer_name).exists():
                raise ValidationError('مشتری با این نام قبلاً ثبت شده است')
        
        return customer_name
    
    def clean_phone(self):
        """📞 اعتبارسنجی شماره تلفن با تبدیل خودکار اعداد فارسی"""
        return self.clean_phone_field('phone', allow_empty=True)
    
    def clean_national_id(self):
        """🆔 اعتبارسنجی شناسه ملی با تبدیل خودکار اعداد فارسی"""
        return self.clean_number_field('national_id', allow_empty=True)
    
    def clean_economic_code(self):
        """💼 اعتبارسنجی کد اقتصادی با تبدیل خودکار اعداد فارسی"""
        return self.clean_number_field('economic_code', allow_empty=True)
    
    def clean_postcode(self):
        """📮 اعتبارسنجی کد پستی با تبدیل خودکار اعداد فارسی"""
        return self.clean_number_field('postcode', allow_empty=True)


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
    
    # 🚨 Check for un-priced products (for super admin alarm)
    un_priced_products_count = 0
    if request.user.is_super_admin():
        un_priced_products_count = Product.objects.filter(
            status='In-stock',
            price=0
        ).count()
    
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
        'un_priced_products_count': un_priced_products_count,
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
    
    # 📊 محاسبه آمار کلی موجودی
    total_products = Product.objects.count()
    in_stock_count = Product.objects.filter(status='In-stock').count()
    sold_count = Product.objects.filter(status='Sold').count()
    pre_order_count = Product.objects.filter(status='Pre-order').count()
    
    # محاسبه درصد ظرفیت انبار (بر اساس محصولات موجود)
    warehouse_capacity_percentage = round((in_stock_count / max(total_products, 1)) * 100)
    
    # تعداد انبارها
    warehouses_count = len(Product.LOCATION_CHOICES)
    
    # آمار بر اساس مکان انبار
    location_stats = {}
    for location_code, location_name in Product.LOCATION_CHOICES:
        location_products = Product.objects.filter(location=location_code)
        location_in_stock = location_products.filter(status='In-stock').count()
        location_total = location_products.count()
        location_sold = location_products.filter(status='Sold').count()
        location_pre_order = location_products.filter(status='Pre-order').count()
        
        # فقط انبارهایی که حداقل یک محصول دارند را نمایش بده
        if location_total > 0:
            location_stats[location_code] = {
                'name': location_name,
                'total': location_total,
                'in_stock': location_in_stock,
                'sold': location_sold,
                'pre_order': location_pre_order,
                'capacity_percentage': round((location_in_stock / max(location_total, 1)) * 100),
                'products': location_products.order_by('-created_at')[:4]  # آخرین 4 محصول برای نمایش
            }
    
    # آمار کلی
    inventory_stats = {
        'total_products': total_products,
        'in_stock_count': in_stock_count,
        'sold_count': sold_count,
        'pre_order_count': pre_order_count,
        'warehouse_capacity_percentage': warehouse_capacity_percentage,
        'warehouses_count': warehouses_count,
        'low_stock_count': 0,  # می‌توانید منطق کم موجودی را اضافه کنید
        'out_of_stock_count': 0,  # می‌توانید منطق ناموجودی را اضافه کنید
        'location_stats': location_stats,
    }
    
    context = {
        'title': '📦 مدیریت موجودی',
        'inventory_stats': inventory_stats,
    }
    return render(request, 'core/inventory_list.html', context)


@login_required
@super_admin_permission_required('manage_orders')
def orders_list_view(request):
    """📋 لیست سفارشات با فیلتر و جستجو"""
    user = request.user
    ActivityLog.log_activity(
        user=user,
        action='VIEW',
        description='مشاهده لیست سفارشات',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    # Superadmin: see all orders
    if user.is_super_admin():
        orders = Order.objects.select_related('customer', 'created_by').prefetch_related('order_items')
        logger.info(f"[DEBUG] orders_list_view: superadmin, all orders")
    else:
        # Customer: see only their own orders (by phone or name match)
        user_name = (user.get_full_name() or user.username).strip().lower()
        user_phone = getattr(user, 'phone', None)
        orders = Order.objects.select_related('customer', 'created_by').prefetch_related('order_items')
        orders = orders.filter(
            Q(customer__phone=user_phone) |
            Q(customer__customer_name__icontains=user_name)
        )
        logger.info(f"[DEBUG] orders_list_view: customer, user_phone={user_phone}, user_name={user_name}")

    # --- Add this block for customer_id filtering ---
    customer_id = request.GET.get('customer_id')
    customer = None
    if customer_id:
        try:
            customer = Customer.objects.get(id=int(customer_id))
            orders = orders.filter(customer_id=int(customer_id))
        except (ValueError, Customer.DoesNotExist):
            pass
    # --- End block ---

    # دریافت پارامترهای فیلتر از URL
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    payment_filter = request.GET.get('payment', '').strip()
    filter_by = request.GET.get('filter_by', 'date').strip()
    
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
    
    # مرتب‌سازی بر اساس فیلتر انتخاب شده
    if filter_by == 'last_changes':
        # مرتب‌سازی بر اساس آخرین تغییرات (updated_at)
        orders = orders.order_by('-updated_at')
    else:
        # مرتب‌سازی بر اساس تاریخ ایجاد (created_at) - پیش‌فرض
        orders = orders.order_by('-created_at')
    
    # 📄 صفحه‌بندی
    paginator = Paginator(orders, 25)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'title': '📋 مدیریت سفارشات',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'filter_by': filter_by,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_METHOD_CHOICES,
        'total_orders': orders.count(),
        'customer': customer,
    }
    return render(request, 'core/orders_list.html', context)


@login_required
@super_admin_permission_required('manage_customers')
def customers_list_view(request):
    """👥 لیست مشتریان با فیلتر و جستجو - مطابق با Django Admin"""
    
    # 🔍 فیلتر کردن queryset بر اساس نقش کاربر (مثل Django Admin)
    customers = Customer.objects.all()
    
    # 👑 Super Admin همه مشتریان را می‌بیند
    # 🟡 Admin فقط مشتریان فعال و غیرفعال را می‌بیند
    if not request.user.is_super_admin():
        customers = customers.exclude(status='Blocked')
    
    # 📜 ثبت لاگ مشاهده مشتریان
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لیست مشتریان',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )
    
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
        'can_add_customer': request.user.is_super_admin() or request.user.has_perm('core.add_customer'),
        'can_change_customer': request.user.is_super_admin() or request.user.has_perm('core.change_customer'),
        'can_delete_customer': request.user.is_super_admin() or request.user.has_perm('core.delete_customer'),
    }
    return render(request, 'core/customers_list.html', context)


@login_required
@super_admin_permission_required('manage_customers')
def create_customer_view(request):
    """➕ ایجاد مشتری جدید - مطابق با Django Admin"""
    
    # 🔐 بررسی مجوز ایجاد مشتری
    if not (request.user.is_super_admin() or request.user.has_perm('core.add_customer')):
        raise PermissionDenied("شما مجوز ایجاد مشتری جدید را ندارید")
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            if request.user.is_super_admin():
                customer.status = 'Active'
            customer.save()
            
            # 📜 ثبت لاگ ایجاد مشتری
            ActivityLog.log_activity(
                user=request.user,
                action='CREATE',
                description=f'مشتری جدید ایجاد شد: {customer.customer_name}',
                content_object=customer,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                severity='MEDIUM',
                extra_data={
                    'customer_id': customer.id,
                    'customer_name': customer.customer_name,
                    'phone': customer.phone,
                    'status': customer.status
                }
            )
            
            messages.success(request, f'✅ مشتری {customer.customer_name} با موفقیت ایجاد شد')
            return redirect('core:customers_list')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': '➕ ایجاد مشتری جدید',
        'is_create': True
    }
    return render(request, 'core/customer_form.html', context)


@login_required
@super_admin_permission_required('manage_customers')
@require_http_methods(["GET", "POST"])
def edit_customer_view(request, customer_id):
    """✏️ ویرایش مشتری - مطابق با Django Admin"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 🔐 بررسی مجوز ویرایش مشتری
    if not (request.user.is_super_admin() or request.user.has_perm('core.change_customer')):
        raise PermissionDenied("شما مجوز ویرایش این مشتری را ندارید")
    
    # 🔒 بررسی دسترسی به مشتری (Admin نمی‌تواند مشتریان مسدود را ویرایش کند)
    if not request.user.is_super_admin() and customer.status == 'Blocked':
        raise PermissionDenied("شما نمی‌توانید مشتریان مسدود را ویرایش کنید")
    
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            # ذخیره اطلاعات قبلی برای لاگ
            old_data = {
                'customer_name': customer.customer_name,
                'phone': customer.phone,
                'status': customer.status
            }
            
            customer = form.save()
            
            # 📜 ثبت لاگ ویرایش مشتری
            changes = []
            for field, old_value in old_data.items():
                new_value = getattr(customer, field)
                if old_value != new_value:
                    changes.append(f'{field}: {old_value} → {new_value}')
            
            ActivityLog.log_activity(
                user=request.user,
                action='UPDATE',
                description=f'مشتری ویرایش شد: {customer.customer_name} - تغییرات: {", ".join(changes) if changes else "بدون تغییر مهم"}',
                content_object=customer,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                severity='MEDIUM',
                extra_data={
                    'customer_id': customer.id,
                    'customer_name': customer.customer_name,
                    'changes': changes
                }
            )
            
            messages.success(request, '✅ اطلاعات مشتری با موفقیت ویرایش شد.')
            return redirect('core:customers_list')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': '✏️ ویرایش مشتری',
        'is_create': False
    }
    return render(request, 'core/customer_form.html', context)


@login_required
@super_admin_permission_required('manage_customers')
@require_http_methods(["POST"])
def delete_customer_view(request, customer_id):
    """🗑️ حذف مشتری - مطابق با Django Admin"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 🔐 بررسی مجوز حذف مشتری
    if not (request.user.is_super_admin() or request.user.has_perm('core.delete_customer')):
        raise PermissionDenied("شما مجوز حذف این مشتری را ندارید")
    
    # 🔒 بررسی دسترسی به مشتری (Admin نمی‌تواند مشتریان مسدود را حذف کند)
    if not request.user.is_super_admin() and customer.status == 'Blocked':
        raise PermissionDenied("شما نمی‌توانید مشتریان مسدود را حذف کنید")
    
    # 🔍 بررسی وجود سفارشات مرتبط
    related_orders = Order.objects.filter(customer=customer).count()
    if related_orders > 0:
        messages.error(request, f'❌ نمی‌توان این مشتری را حذف کرد زیرا {related_orders} سفارش مرتبط دارد')
        return redirect('core:customers_list')
    
    # ذخیره اطلاعات برای لاگ
    customer_name = customer.customer_name
    customer_phone = customer.phone
    
    # حذف مشتری
    customer.delete()
    
    # 📜 ثبت لاگ حذف مشتری
    ActivityLog.log_activity(
        user=request.user,
        action='DELETE',
        description=f'مشتری حذف شد: {customer_name} - {customer_phone}',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='HIGH',
        extra_data={
            'customer_name': customer_name,
            'phone': customer_phone
        }
    )
    
    messages.success(request, '🗑️ مشتری با موفقیت حذف شد.')
    return redirect('core:customers_list')


@login_required
@super_admin_permission_required('manage_customers')
def customer_detail_modal_view(request, customer_id):
    """👁️ مشاهده جزئیات مشتری - مطابق با Django Admin"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 🔐 بررسی مجوز مشاهده مشتری
    if not (request.user.is_super_admin() or request.user.has_perm('core.view_customer')):
        raise PermissionDenied("شما مجوز مشاهده این مشتری را ندارید")
    
    # 🔒 بررسی دسترسی به مشتری (Admin نمی‌تواند مشتریان مسدود را ببیند)
    if not request.user.is_super_admin() and customer.status == 'Blocked':
        raise PermissionDenied("شما نمی‌توانید مشتریان مسدود را مشاهده کنید")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('modal'):
        html = render_to_string('core/partials/customer_detail_modal.html', {'customer': customer}, request=request)
        return HttpResponse(html)
    return redirect('core:customers_list')


@login_required
@super_admin_permission_required('manage_customers')
@require_http_methods(["GET", "POST"])
def customer_edit_modal_view(request, customer_id):
    """✏️ ویرایش مشتری در مودال - مطابق با Django Admin"""
    
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 🔐 بررسی مجوز ویرایش مشتری
    if not (request.user.is_super_admin() or request.user.has_perm('core.change_customer')):
        raise PermissionDenied("شما مجوز ویرایش این مشتری را ندارید")
    
    # 🔒 بررسی دسترسی به مشتری (Admin نمی‌تواند مشتریان مسدود را ویرایش کند)
    if not request.user.is_super_admin() and customer.status == 'Blocked':
        raise PermissionDenied("شما نمی‌توانید مشتریان مسدود را ویرایش کنید")
    
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            # ذخیره اطلاعات قبلی برای لاگ
            old_data = {
                'customer_name': customer.customer_name,
                'phone': customer.phone,
                'status': customer.status
            }
            
            customer = form.save()
            
            # 📜 ثبت لاگ ویرایش مشتری
            changes = []
            for field, old_value in old_data.items():
                new_value = getattr(customer, field)
                if old_value != new_value:
                    changes.append(f'{field}: {old_value} → {new_value}')
            
            ActivityLog.log_activity(
                user=request.user,
                action='UPDATE',
                description=f'مشتری ویرایش شد (مودال): {customer.customer_name} - تغییرات: {", ".join(changes) if changes else "بدون تغییر مهم"}',
                content_object=customer,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                severity='MEDIUM',
                extra_data={
                    'customer_id': customer.id,
                    'customer_name': customer.customer_name,
                    'changes': changes
                }
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('modal'):
                return JsonResponse({
                    'success': True,
                    'message': '✅ اطلاعات مشتری با موفقیت ویرایش شد',
                    'customer_name': customer.customer_name,
                    'customer_status': customer.get_status_display()
                })
            return redirect('core:customers_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('modal'):
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    
    # GET request
    form = CustomerForm(instance=customer)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('modal'):
        html = render_to_string('core/partials/customer_edit_modal.html', {
            'form': form,
            'customer': customer, 
            'status_choices': Customer.STATUS_CHOICES
        }, request=request)
        return HttpResponse(html)
    return redirect('core:customers_list')


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
    
    # 📅 دریافت فیلتر از پارامترهای URL
    filter_by = request.GET.get('filterBy', 'this_month')
    search_term = request.GET.get('search', '')
    
    # محاسبه تاریخ شروع بر اساس فیلتر
    today = timezone.now().date()
    if filter_by == 'today':
        start_date = today
        end_date = today
    elif filter_by == 'this_week':
        # Start of current week (Monday)
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif filter_by == 'this_month':
        # Start of current month
        start_date = today.replace(day=1)
        end_date = today
    elif filter_by == 'recently_changed':
        # For recently changed, we'll use updated_at field and set a reasonable range
        start_date = today - timedelta(days=30)  # Last 30 days for recent changes
        end_date = today
    else:
        start_date = today.replace(day=1)  # پیش‌فرض: این ماه
        end_date = today
    
    # 📊 محاسبه آمار مالی واقعی
    # درآمد کل (سفارشات تایید شده و تحویل داده شده)
    revenue_query = Order.objects.filter(
        status__in=['Confirmed', 'Delivered']
    )
    
    expenses_query = OrderItem.objects.filter(
        order__status__in=['Confirmed', 'Delivered']
    )
    
    orders_query = Order.objects.all()
    
    # Apply date filtering based on filter type
    if filter_by == 'recently_changed':
        # For recently changed, use updated_at field
        revenue_query = revenue_query.filter(updated_at__date__gte=start_date, updated_at__date__lte=end_date)
        expenses_query = expenses_query.filter(order__updated_at__date__gte=start_date, order__updated_at__date__lte=end_date)
        orders_query = orders_query.filter(updated_at__date__gte=start_date, updated_at__date__lte=end_date)
    else:
        # For other filters, use created_at field
        revenue_query = revenue_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        expenses_query = expenses_query.filter(order__created_at__date__gte=start_date, order__created_at__date__lte=end_date)
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    total_revenue = revenue_query.aggregate(total=Sum('final_amount'))['total'] or 0
    total_expenses = expenses_query.aggregate(total=Sum('total_price'))['total'] or 0
    total_orders = orders_query.count()
    
    # سود خالص (درآمد - هزینه)
    net_profit = total_revenue - total_expenses
    
    # محاسبه درصد تغییر نسبت به دوره قبل
    if filter_by == 'today':
        previous_start_date = start_date - timedelta(days=1)
        previous_end_date = start_date - timedelta(days=1)
    elif filter_by == 'this_week':
        previous_start_date = start_date - timedelta(days=7)
        previous_end_date = start_date - timedelta(days=1)
    elif filter_by == 'this_month':
        # Previous month
        if start_date.month == 1:
            previous_start_date = start_date.replace(year=start_date.year-1, month=12)
        else:
            previous_start_date = start_date.replace(month=start_date.month-1)
        previous_end_date = start_date - timedelta(days=1)
    else:  # recently_changed
        previous_start_date = start_date - timedelta(days=30)
        previous_end_date = start_date - timedelta(days=1)
    
    # آمار دوره قبل
    if filter_by == 'recently_changed':
        prev_revenue = Order.objects.filter(
            status__in=['Confirmed', 'Delivered'],
            updated_at__date__gte=previous_start_date,
            updated_at__date__lte=previous_end_date
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        prev_orders = Order.objects.filter(
            updated_at__date__gte=previous_start_date,
            updated_at__date__lte=previous_end_date
        ).count()
    else:
        prev_revenue = Order.objects.filter(
            status__in=['Confirmed', 'Delivered'],
            created_at__date__gte=previous_start_date,
            created_at__date__lte=previous_end_date
        ).aggregate(total=Sum('final_amount'))['total'] or 0
        
        prev_orders = Order.objects.filter(
            created_at__date__gte=previous_start_date,
            created_at__date__lte=previous_end_date
        ).count()
    
    # محاسبه درصد تغییر
    revenue_change = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    orders_change = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
    
    # 🧾 آخرین تراکنش‌ها (سفارشات اخیر)
    if filter_by == 'recently_changed':
        recent_transactions = Order.objects.select_related('customer').filter(
            updated_at__date__gte=start_date,
            updated_at__date__lte=end_date
        ).order_by('-updated_at')[:10]
    else:
        recent_transactions = Order.objects.select_related('customer').filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).order_by('-created_at')[:10]
    
    # Apply search filter if provided
    if search_term:
        recent_transactions = recent_transactions.filter(
            Q(order_number__icontains=search_term) |
            Q(customer__customer_name__icontains=search_term) |
            Q(status__icontains=search_term)
        )
    
    # اضافه کردن اطلاعات پرداخت به تراکنش‌ها
    for transaction in recent_transactions:
        transaction.latest_payment = Payment.objects.filter(
            order=transaction
        ).order_by('-created_at').first()
    
    # 📋 خلاصه عملکرد مالی
    performance_summary = {
        'positive_points': [],
        'attention_points': []
    }
    
    # نکات مثبت
    if revenue_change > 0:
        performance_summary['positive_points'].append(f'✅ افزایش {revenue_change:.1f}% درآمد نسبت به دوره قبل')
    if total_orders > 0:
        performance_summary['positive_points'].append(f'✅ {total_orders} سفارش در این دوره')
    if net_profit > 0:
        performance_summary['positive_points'].append(f'✅ سود خالص: {net_profit:,.0f} تومان')
    
    # نکات قابل توجه
    pending_orders = Order.objects.filter(status='Pending').count()
    if pending_orders > 0:
        performance_summary['attention_points'].append(f'⚠️ {pending_orders} سفارش در انتظار تایید')
    
    failed_payments = Payment.objects.filter(status='FAILED').count()
    if failed_payments > 0:
        performance_summary['attention_points'].append(f'⚠️ {failed_payments} پرداخت ناموفق')
    
    # فرصت‌های بهینه‌سازی
    if total_revenue > 0 and total_expenses > 0:
        profit_margin = (net_profit / total_revenue) * 100
        if profit_margin < 20:
            performance_summary['attention_points'].append(f'ℹ️ حاشیه سود: {profit_margin:.1f}% - فرصت بهبود')
    
    context = {
        'title': '💰 نمای کلی مالی',
        'financial_stats': {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'total_orders': total_orders,
            'revenue_change': revenue_change,
            'orders_change': orders_change,
        },
        'recent_transactions': recent_transactions,
        'performance_summary': performance_summary,
        'filter_by': filter_by,
        'search_term': search_term,
    }
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
        # جستجو در فیلدهای متنی
        search_filters = (
            Q(reel_number__icontains=search_query) |
            Q(grade__icontains=search_query) |
            Q(qr_code__icontains=search_query)
        )
        
        # جستجو در فیلد عرض (width) اگر ورودی عددی باشد
        if search_query.isdigit():
            width_value = int(search_query)
            search_filters |= Q(width=width_value)
        
        products = products.filter(search_filters)
    
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
    
    # اعمال فیلتر تاریخ با پردازش صحیح
    if date_from:
        try:
            from datetime import datetime
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__gte=from_date)
            print(f"[DEBUG] Activity Logs - Date From: {date_from} -> {from_date}")
        except ValueError as e:
            # اگر تاریخ نامعتبر باشد، فیلتر را نادیده بگیر
            print(f"[DEBUG] Activity Logs - Invalid date_from: {date_from}, Error: {e}")
            pass
    
    if date_to:
        try:
            from datetime import datetime
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date__lte=to_date)
            print(f"[DEBUG] Activity Logs - Date To: {date_to} -> {to_date}")
        except ValueError as e:
            # اگر تاریخ نامعتبر باشد، فیلتر را نادیده بگیر
            print(f"[DEBUG] Activity Logs - Invalid date_to: {date_to}, Error: {e}")
            pass
    
    # اعمال فیلتر جستجو
    if search_query:
        logs = logs.filter(
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(ip_address__icontains=search_query) |
            Q(user_agent__icontains=search_query)
        )
    
    # 📊 آمار لاگ‌ها
    from django.utils import timezone
    from datetime import timedelta
    
    # محاسبه آمار بر اساس سطح اهمیت
    severity_stats = {}
    for severity_code, severity_name in ActivityLog.SEVERITY_CHOICES:
        count = logs.filter(severity=severity_code).count()
        severity_stats[severity_code] = count
    
    # آمار 24 ساعت گذشته
    yesterday = timezone.now() - timedelta(days=1)
    last_24h_count = logs.filter(created_at__gte=yesterday).count()
    
    # آمار کلی
    total_count = logs.count()
    
    logs_stats = {
        'total_count': total_count,
        'last_24h_count': last_24h_count,
        'severity_stats': severity_stats,
        'action_stats': logs.values('action').annotate(count=Count('id')),
        'daily_stats': logs.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id'))[:7]
    }
    
    # 📄 صفحه‌بندی
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    # دریافت لیست کاربران برای فیلتر
    from accounts.models import User
    users_list = User.objects.filter(
        activitylog__isnull=False
    ).distinct().order_by('username')
    
    context = {
        'title': '📜 لاگ‌های فعالیت سیستم',
        'logs': logs,
        'logs_stats': logs_stats,
        'action_filter': action_filter,
        'severity_filter': severity_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'users_list': users_list,
        'action_choices': ActivityLog.ACTION_CHOICES,
        'severity_choices': ActivityLog.SEVERITY_CHOICES,
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
        is_thursday_open = data.get('is_thursday_open', False)
        is_holiday = data.get('is_holiday', False)
        holiday_help_text = data.get('holiday_help_text', '')
        max_selection_limit = data.get('max_selection_limit', 6)
        
        # 🧹 اعتبارسنجی داده‌ها
        if not start_time or not end_time:
            return JsonResponse({
                'success': False,
                'error': '⏰ زمان شروع و پایان کار الزامی است'
            }, status=400)
        
        # 🔢 اعتبارسنجی حداکثر انتخاب
        try:
            max_selection_limit = int(max_selection_limit)
            if max_selection_limit < 1 or max_selection_limit > 50:
                return JsonResponse({
                    'success': False,
                    'error': '🔢 حداکثر انتخاب باید بین 1 تا 50 باشد'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': '🔢 حداکثر انتخاب باید عدد معتبر باشد'
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
        
        # �� بررسی منطقی بودن زمان‌ها
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
            is_thursday_open=is_thursday_open,
            is_holiday=is_holiday,
            holiday_help_text=holiday_help_text,
            max_selection_limit=max_selection_limit,
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
                'holiday_help_text': current_hours.holiday_help_text if current_hours and current_hours.is_holiday else '',
            }
            return render(request, 'core/shop_closed.html', context)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# اعمال میدل‌ویر ساعات کاری به صفحات مشتری
@check_working_hours_middleware
def index_view(request):
    """🏠 صفحه اصلی کارخانه کاغذ و مقوای همایون"""
    
    # 📜 ثبت لاگ مشاهده صفحه اصلی (فقط اگر کاربر لاگین باشد)
    if request.user.is_authenticated:
        ActivityLog.log_activity(
            user=request.user,
            action='VIEW',
            description='مشاهده صفحه اصلی کارخانه',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='LOW'
        )
    
    # دریافت محصولات واقعی از مدل Product
    all_products = Product.objects.filter(status='In-stock').order_by('-created_at')
    
    # جداسازی محصولات با قیمت و بدون قیمت
    products = all_products.filter(price__gt=0).order_by('-created_at')
    un_priced_products = all_products.filter(price=0).order_by('-created_at')
    credit_products = all_products.filter(price__gt=0).order_by('-created_at')
    
    # اگر نوع پرداخت در مدل دارید، می‌توانید فیلتر کنید (مثلاً payment_type='credit')
    # credit_products = Product.objects.filter(status='In-stock', payment_type='credit').order_by('-created_at')

    price_data = {
        'cash': {
            'price': products.first().price if products.exists() else 0,
            'stock': products.count()
        },
        'credit': {
            'price': credit_products.first().price if credit_products.exists() else 0,
            'stock': credit_products.count()
        }
    }
    
    # 🔄 Check for unfinished payment orders (new policy)
    unfinished_payment_orders = []
    if request.user.is_authenticated:
        try:
            # Get customer for the current user
            customer = request.user.customer
            if customer:
                # Find orders that are in 'Pending' or 'Processing' status with cash items but no successful payments
                unfinished_orders = Order.objects.filter(
                    customer=customer,
                    status__in=['Pending', 'Processing'],
                    payment_method='Cash'
                ).prefetch_related('order_items', 'order_items__product')
                
                for order in unfinished_orders:
                    # Check if order has cash items
                    cash_items = order.order_items.filter(payment_method='Cash')
                    if cash_items.exists():
                        # Calculate total cash amount
                        total_cash_amount = sum(item.total_price for item in cash_items)
                        
                        # Check if there are no successful payments for this order
                        from payments.models import Payment
                        successful_payments = Payment.objects.filter(
                            order=order,
                            status='SUCCESS'
                        ).exists()
                        
                        if not successful_payments and total_cash_amount > 0:
                            unfinished_payment_orders.append({
                                'order': order,
                                'total_cash_amount': total_cash_amount,
                                'cash_items_count': cash_items.count(),
                                'order_date': order.created_at,
                                'order_number': order.order_number
                            })
                
                # Sort by most recent first
                unfinished_payment_orders.sort(key=lambda x: x['order_date'], reverse=True)
                
        except Exception as e:
            logger.error(f"Error checking unfinished payment orders: {e}")
            # Continue without unfinished orders if there's an error
    
    context = {
        'title': 'کارخانه کاغذ و مقوای همایون',
        'price_data': price_data,
        'products': products,  # فقط محصولات با قیمت
        'un_priced_products': un_priced_products,
        'credit_products': credit_products,
        'user': request.user,
        'unfinished_payment_orders': unfinished_payment_orders,
    }
    return render(request, 'index.html', context)


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
        customer = Customer.objects.get(customer_name=request.user.get_full_name())
    except Customer.DoesNotExist:
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
@require_http_methods(["POST"])
def checkout_view(request):
    """💳 تکمیل خرید"""
    
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, '🛒 سبد خرید شما خالی است')
        return redirect('core:products_landing')
    
    try:
        # پیدا کردن یا ایجاد پروفایل مشتری
        customer, created = Customer.objects.get_or_create(
            customer_name=request.user.get_full_name(),
            defaults={
                'phone': request.user.phone,
                'status': 'Active'
            }
        )
        
        # ایجاد سفارش - استفاده از پیش‌فرض "Mixed" برای سفارشات با چند نوع پرداخت
        order = Order.objects.create(
            customer=customer,
            payment_method='Cash',  # پیش‌فرض - حالا در OrderItem نوع واقعی ذخیره می‌شود
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
        
        messages.success(request, f'🎉 سفارش شما با شماره {order.order_number} ثبت شد')
        return redirect('core:order_detail', order_id=order.id)
        
    except Exception as e:
        messages.error(request, '❌ خطا در ثبت سفارش. لطفاً مجدداً تلاش کنید')
        return redirect('core:cart')


@login_required
def order_detail_view(request, order_id):
    """
    📋 جزئیات سفارش
    👁️ نمایش اطلاعات کامل سفارش
    🔒 دسترسی به سفارش‌های با پرداخت ناموفق مسدود شده است
    """
    try:
        order = Order.objects.get(id=order_id)
        user = request.user
        
        # 🔒 SECURITY: Block access to orders with failed payments or cancelled orders
        from payments.models import Payment
        failed_payments = Payment.objects.filter(
            order=order, 
            status='FAILED'
        ).exists()
        
        if (failed_payments or order.status == 'Cancelled') and not user.is_super_admin():
            if failed_payments:
                messages.warning(request, 'دسترسی به سفارش‌های با پرداخت ناموفق مسدود شده است')
            else:
                messages.warning(request, 'دسترسی به سفارش‌های لغو شده مسدود شده است')
            return redirect('core:index')
        
        # Access logic
        if not user.is_super_admin():
            user_name = (user.get_full_name() or user.username).strip().lower()
            user_phone = getattr(user, 'phone', None)
            customer_name = order.customer.customer_name.strip().lower()
            customer_phone = order.customer.phone
            phone_match = user_phone and customer_phone and user_phone == customer_phone
            name_match = user_name in customer_name or customer_name in user_name
            customer_match = phone_match or name_match
            logger.info(f"[DEBUG] order_detail_view: user={user}, user_phone={user_phone}, user_name={user_name}, customer_phone={customer_phone}, customer_name={customer_name}, phone_match={phone_match}, name_match={name_match}, customer_match={customer_match}")
            if not customer_match:
                messages.error(request, '❌ شما اجازه مشاهده این سفارش را ندارید')
                return redirect('core:index')
        
        # ثبت لاگ مشاهده
        ActivityLog.log_activity(
            user=user,
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
            'user': user,
        }
        return render(request, 'core/order_detail.html', context)
    except Order.DoesNotExist:
        messages.error(request, '❌ سفارش مورد نظر یافت نشد')
        return redirect('core:index')


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
@super_admin_permission_required('manage_customers')
@require_http_methods(["GET", "POST"])
def edit_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == "POST":
        customer.customer_name = request.POST.get('customer_name', customer.customer_name)
        customer.phone = request.POST.get('phone', customer.phone)
        customer.address = request.POST.get('address', customer.address)
        customer.national_id = request.POST.get('national_id', customer.national_id)
        customer.economic_code = request.POST.get('economic_code', customer.economic_code)
        customer.postcode = request.POST.get('postcode', customer.postcode)
        customer.status = request.POST.get('status', customer.status)
        customer.comments = request.POST.get('comments', customer.comments)
        customer.save()
        messages.success(request, '✅ اطلاعات مشتری با موفقیت ویرایش شد.')
        return redirect('core:customers_list')
    context = {
        'customer': customer,
        'status_choices': Customer.STATUS_CHOICES,
        'title': '✏️ ویرایش مشتری'
    }
    return render(request, 'core/edit_customer.html', context)


@login_required
@super_admin_permission_required('manage_customers')
@require_http_methods(["POST"])
def delete_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    messages.success(request, '🗑️ مشتری با موفقیت حذف شد.')
    return redirect('core:customers_list')


@login_required
@super_admin_permission_required('manage_orders')
def create_order_for_customer_view(request, customer_id):
    """🛒 ایجاد سفارش جدید برای مشتری توسط Admin/Super Admin"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # بررسی وضعیت مشتری
    if customer.status == 'Requested':
        messages.error(request, '❌ نمی‌توان برای مشتریان در انتظار تایید سفارش ایجاد کرد')
        return redirect('core:customers_list')
    
    if customer.status in ['Suspended', 'Blocked']:
        messages.error(request, '❌ نمی‌توان برای مشتریان معلق یا مسدود سفارش ایجاد کرد')
        return redirect('core:customers_list')
    
    # دریافت محصولات موجود
    available_products = Product.objects.filter(status='In-stock').order_by('-created_at')
    
    if request.method == 'POST':
        # پردازش فرم ایجاد سفارش
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)
        payment_method = request.POST.get('payment_method', 'Cash')
        notes = request.POST.get('notes', '')
        
        if not product_id:
            messages.error(request, '❌ لطفاً محصولی انتخاب کنید')
            return render(request, 'core/create_order_for_customer.html', {
                'customer': customer,
                'available_products': available_products,
                'title': f'🛒 ایجاد سفارش برای {customer.customer_name}'
            })
        
        try:
            product = Product.objects.get(id=product_id, status='In-stock')
            # Validate and normalize quantity
            try:
                quantity = normalize_number_input(quantity)
                if not validate_number_input(quantity):
                    messages.error(request, '❌ تعداد وارد شده نامعتبر است')
                    return render(request, 'core/create_order_for_customer.html', {
                        'customer': customer,
                        'available_products': available_products,
                        'title': f'🛒 ایجاد سفارش برای {customer.customer_name}'
                    })
                quantity = int(quantity)
            except Exception:
                messages.error(request, '❌ تعداد وارد شده نامعتبر است')
                return render(request, 'core/create_order_for_customer.html', {
                    'customer': customer,
                    'available_products': available_products,
                    'title': f'🛒 ایجاد سفارش برای {customer.customer_name}'
                })
            if quantity <= 0:
                messages.error(request, '❌ تعداد باید بیشتر از صفر باشد')
                return render(request, 'core/create_order_for_customer.html', {
                    'customer': customer,
                    'available_products': available_products,
                    'title': f'🛒 ایجاد سفارش برای {customer.customer_name}'
                })
            
            # ایجاد سفارش
            from django.db import transaction
            with transaction.atomic():
                # Generate unique order_number
                for _ in range(5):
                    candidate = Order().generate_order_number()
                    if not Order.objects.filter(order_number=candidate).exists():
                        order_number = candidate
                        break
                else:
                    messages.error(request, '❌ خطا در تولید شماره سفارش یکتا. لطفاً مجدداً تلاش کنید.')
                    return render(request, 'core/create_order_for_customer.html', {
                        'customer': customer,
                        'available_products': available_products,
                        'title': f'🛒 ایجاد سفارش برای {customer.customer_name}'
                    })
                order = Order.objects.create(
                    customer=customer,
                    payment_method=payment_method,
                    status='Confirmed',  # سفارش تایید شده
                    notes=notes,
                    created_by=request.user,
                    order_number=order_number
                )
                
                # ایجاد آیتم سفارش
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=product.price * quantity,
                    payment_method=payment_method
                )
                
                # به‌روزرسانی مبلغ سفارش
                order.calculate_final_amount()
                order.save()
                
                # تغییر وضعیت محصول به فروخته شده
                product.status = 'Sold'
                product.save()
                
                # ثبت لاگ
                ActivityLog.log_activity(
                    user=request.user,
                    action='CREATE',
                    description=f'ایجاد سفارش جدید {order.order_number} برای {customer.customer_name} - مبلغ: {order.final_amount:,.0f} تومان',
                    content_object=order,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='MEDIUM'
                )
                
                messages.success(request, 
                    f'✅ سفارش جدید {order.order_number} برای {customer.customer_name} با موفقیت ایجاد شد! 💰 مبلغ: {order.final_amount:,.0f} تومان'
                )
                return redirect('core:order_detail', order_id=order.id)
                
        except Product.DoesNotExist:
            messages.error(request, '❌ محصول انتخاب شده یافت نشد')
        except ValueError:
            messages.error(request, '❌ تعداد وارد شده نامعتبر است')
        except Exception as e:
            messages.error(request, f'❌ خطا در ایجاد سفارش: {str(e)}')
    
    # GET request - نمایش فرم
    return render(request, 'core/create_order_for_customer.html', {
        'customer': customer,
        'available_products': available_products,
        'title': f'🛒 ایجاد سفارش برای {customer.customer_name}'
    })


class ProductForm(ModelForm, NumberValidationMixin):
    class Meta:
        model = Product
        fields = ['reel_number', 'location', 'width', 'gsm', 'length', 'grade', 'breaks', 'price']
    
    def clean_width(self):
        """📏 اعتبارسنجی عرض با تبدیل خودکار اعداد فارسی"""
        return self.clean_number_field('width', allow_empty=False, min_value=1)
    
    def clean_gsm(self):
        """⚖️ اعتبارسنجی GSM با تبدیل خودکار اعداد فارسی"""
        return self.clean_number_field('gsm', allow_empty=False, min_value=1)
    
    def clean_length(self):
        """📐 اعتبارسنجی طول با تبدیل خودکار اعداد فارسی"""
        return self.clean_number_field('length', allow_empty=False, min_value=1)
    
    def clean_breaks(self):
        """💔 اعتبارسنجی تعداد پارگی با تبدیل خودکار اعداد فارسی"""
        return self.clean_number_field('breaks', allow_empty=True, min_value=0)
    
    def clean_price(self):
        """💰 اعتبارسنجی قیمت با تبدیل خودکار اعداد فارسی"""
        return self.clean_price_field('price', allow_empty=False, min_value=0)

@login_required
@super_admin_permission_required('manage_inventory')
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.price_updated_by = request.user
            product.save()
            ActivityLog.log_activity(
                user=request.user,
                action='CREATE',
                description=f'محصول جدید {product.reel_number} ایجاد شد',
                content_object=product,
                severity='HIGH'
            )
            messages.success(request, '✅ محصول جدید با موفقیت ثبت شد.')
            return redirect('core:inventory_list')
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form': form, 'title': '➕ افزودن محصول جدید'})

@login_required
@super_admin_permission_required('manage_inventory')
def edit_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.price_updated_by = request.user
            product.save()
            ActivityLog.log_activity(
                user=request.user,
                action='UPDATE',
                description=f'محصول {product.reel_number} ویرایش شد',
                content_object=product,
                severity='MEDIUM'
            )
            messages.success(request, '✅ اطلاعات محصول با موفقیت بروزرسانی شد.')
            # Stay on the same page instead of redirecting
        else:
            messages.error(request, '❌ خطا در بروزرسانی اطلاعات محصول. لطفاً خطاها را بررسی کنید.')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/edit_product.html', {'form': form, 'product': product, 'title': '✏️ ویرایش محصول'})

@csrf_exempt
@require_http_methods(["POST"])
def save_selected_products_view(request):
    """ذخیره انتخاب‌های کاربر در session (برای مشتریان)"""
    try:
        data = json.loads(request.body)
        selected_products = data.get('selected_products', [])
        request.session['selected_products'] = selected_products
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)




@check_working_hours_middleware
@login_required
def selected_products_view(request):
    
    # Ensure customer exists for the user
    customer = request.user.customer
    if not customer:
        # Try to create or update customer profile automatically
        from accounts.models import User
        customer = request.user._create_customer_profile() if hasattr(request.user, '_create_customer_profile') else None
        if customer:
            messages.warning(request, '⚠️ پروفایل مشتری شما به صورت خودکار ایجاد شد. لطفاً اطلاعات خود را بررسی کنید.')
        else:
            messages.error(request, '❌ اطلاعات مشتری یافت نشد و امکان ایجاد خودکار وجود ندارد. لطفاً با پشتیبانی تماس بگیرید.')
            return redirect('accounts:customer_dashboard')

    # Check customer status
    if customer.status not in ['Active', 'Inactive']:
        messages.error(request, '❌ حساب کاربری شما فعال نیست. لطفاً با پشتیبانی تماس بگیرید.')
        return redirect('accounts:customer_dashboard')

    # Load selected products from session
    selected = request.session.get('selected_products', [])
    if not selected:
        messages.warning(request, '⚠️ هیچ محصولی انتخاب نشده است.')
        return redirect('core:products_landing')

    product_ids = [item['product_id'] for item in selected]
    products = Product.objects.filter(id__in=product_ids, status='In-stock')

    if not products.exists():
        messages.error(request, '❌ محصولات انتخاب شده موجود نیستند.')
        return redirect('core:products_landing')

    # تعداد هر محصول را به دیکشنری تبدیل کن
    quantities = {str(item['product_id']): item['quantity'] for item in selected}
    for p in products:
        p.selected_quantity = quantities.get(str(p.id), 0)

    # Robust default payment method logic
    default_payment_method = request.GET.get('default_payment')
    if default_payment_method:
        request.session['default_payment_method'] = default_payment_method
    else:
        default_payment_method = request.session.get('default_payment_method', 'Cash')

    # Create initial order with Processing status
    from django.db import transaction
    try:
        with transaction.atomic():
            # Check if there's already a processing order for this customer
            existing_order = Order.objects.filter(
                customer=customer,
                status='Processing'
            ).first()

            if not existing_order:
                # Create new processing order with unique order_number
                for _ in range(5):
                    candidate = Order().generate_order_number()
                    if not Order.objects.filter(order_number=candidate).exists():
                        order_number = candidate
                        break
                else:
                    messages.error(request, '❌ خطا در تولید شماره سفارش یکتا. لطفاً مجدداً تلاش کنید.')
                    return redirect('core:products_landing')
                processing_order = Order.objects.create(
                    customer=customer,
                    payment_method='Cash',  # Default, will be updated later
                    status='Processing',
                    notes=f'سفارش در حال پردازش - مرحله انتخاب محصولات و نوع پرداخت',
                    created_by=request.user,
                    order_number=order_number
                )

                # Log the creation of processing order
                ActivityLog.log_activity(
                    user=request.user,
                    action='ORDER',
                    description=f'سفارش در حال پردازش {processing_order.order_number} ایجاد شد',
                    content_object=processing_order,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='MEDIUM',
                    extra_data={
                        'order_number': processing_order.order_number,
                        'customer_name': customer.customer_name,
                        'stage': 'product_selection'
                    }
                )

                # Store order ID in session for later use
                request.session['processing_order_id'] = processing_order.id
            else:
                # Use existing processing order
                request.session['processing_order_id'] = existing_order.id
    except Exception as e:
        messages.error(request, f'❌ خطا در ایجاد سفارش: {str(e)}')
        return redirect('core:products_landing')

    # Get working hours configuration for dynamic limit
    try:
        working_hours = WorkingHours.objects.first()
        max_selection_limit = working_hours.max_selection_limit if working_hours else 6
    except:
        max_selection_limit = 6

    # After rendering, clear the session value so it doesn't persist
    response = render(request, 'core/selected_products.html', {
        'products': products,
        'default_payment_method': default_payment_method,
        'max_selection_limit': max_selection_limit,

    })
    if 'default_payment_method' in request.session:
        del request.session['default_payment_method']
    return response

@check_working_hours_middleware
@login_required
@require_http_methods(["POST"])
def process_order_view(request):
    """🛒 پردازش سفارش از صفحه محصولات انتخاب‌شده"""
    try:
        # Get customer
        customer = request.user.customer
        if not customer:
            return JsonResponse({
                'success': False,
                'error': '❌ اطلاعات مشتری یافت نشد. لطفاً با پشتیبانی تماس بگیرید.'
            })
        
        # Check customer status
        if customer.status not in ['Active', 'Inactive']:
            return JsonResponse({
                'success': False,
                'error': '❌ حساب کاربری شما فعال نیست. لطفاً با پشتیبانی تماس بگیرید.'
            })
        
        # Get the processing order from session
        processing_order_id = request.session.get('processing_order_id')
        if not processing_order_id:
            return JsonResponse({
                'success': False,
                'error': '❌ سفارش در حال پردازش یافت نشد. لطفاً مجدداً تلاش کنید.'
            })
        
        try:
            processing_order = Order.objects.get(
                id=processing_order_id,
                customer=customer,
                status='Processing'
            )
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '❌ سفارش در حال پردازش یافت نشد. لطفاً مجدداً تلاش کنید.'
            })
        
        # Process form data
        cash_items = []
        terms_items = []
        total_cash = 0
        total_terms = 0
        
        # Extract product data from form
        for key, value in request.POST.items():
            if key.startswith('product_id_'):
                product_id = key.replace('product_id_', '')
                quantity_raw = request.POST.get(f'quantity_{product_id}', 0)
                try:
                    quantity = normalize_number_input(quantity_raw)
                    if not validate_number_input(quantity):
                        continue
                    quantity = int(quantity)
                except Exception:
                    continue
                payment_method = request.POST.get(f'payment_method_{product_id}', 'Cash')
                
                if quantity > 0:
                    try:
                        product = Product.objects.get(id=product_id, status='In-stock')
                        item_total = product.price * quantity
                        
                        if payment_method == 'Cash':
                            cash_items.append({
                                'product': product,
                                'quantity': quantity,
                                'total': item_total
                            })
                            total_cash += item_total
                        else:  # Terms
                            terms_items.append({
                                'product': product,
                                'quantity': quantity,
                                'total': item_total
                            })
                            total_terms += item_total
                            
                    except Product.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': f'محصول با شماره {product_id} یافت نشد یا موجود نیست.'
                        })
        
        # Check if any items selected
        if not cash_items and not terms_items:
            return JsonResponse({
                'success': False,
                'error': 'هیچ محصولی انتخاب نشده است.'
            })
        
        # Update the processing order based on payment types
        from django.db import transaction
        with transaction.atomic():
            orders_created = []
            
            # Handle cash items - update processing order to Pending for payment
            if cash_items:
                # Update the processing order for cash payment
                processing_order.payment_method = 'Cash'
                processing_order.status = 'Pending'  # Ready for payment
                processing_order.notes = f'سفارش نقدی - مجموع: {total_cash:,.0f} تومان - آماده برای پرداخت'
                processing_order.total_amount = total_cash
                processing_order.calculate_final_amount()
                processing_order.save()
                
                # Add cash items to the order
                for item in cash_items:
                    OrderItem.objects.create(
                        order=processing_order,
                        product=item['product'],
                        quantity=item['quantity'],
                        unit_price=item['product'].price,
                        total_price=item['total'],
                        payment_method='Cash'
                    )
                
                # Update product status to sold
                for item in cash_items:
                    item['product'].status = 'Sold'
                    item['product'].save()
                
                orders_created.append(processing_order)
                
                # Log activity for cash order
                ActivityLog.log_activity(
                    user=request.user,
                    action='ORDER',
                    description=f'سفارش نقدی {processing_order.order_number} آماده پرداخت شد - مبلغ: {processing_order.final_amount:,.0f} تومان',
                    content_object=processing_order,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='MEDIUM',
                    extra_data={
                        'order_number': processing_order.order_number,
                        'payment_type': 'cash',
                        'amount': str(processing_order.final_amount),
                        'items_count': len(cash_items)
                    }
                )
            
            # Handle terms items - create separate order with Pending status
            if terms_items:
                terms_order = Order.objects.create(
                    customer=customer,
                    payment_method='Terms',
                    status='Pending',  # Waiting for admin approval
                    notes=f'سفارش قسطی - مجموع: {total_terms:,.0f} تومان - در انتظار تایید ادمین',
                    created_by=request.user,
                    total_amount=total_terms
                )
                terms_order.calculate_final_amount()
                terms_order.save()
                
                for item in terms_items:
                    OrderItem.objects.create(
                        order=terms_order,
                        product=item['product'],
                        quantity=item['quantity'],
                        unit_price=item['product'].price,
                        total_price=item['total'],
                        payment_method='Terms'
                    )
                
                # Update product status to sold
                for item in terms_items:
                    item['product'].status = 'Sold'
                    item['product'].save()
                
                orders_created.append(terms_order)
                
                # Log activity for terms order
                ActivityLog.log_activity(
                    user=request.user,
                    action='ORDER',
                    description=f'سفارش قسطی {terms_order.order_number} ایجاد شد - مبلغ: {terms_order.final_amount:,.0f} تومان - در انتظار تایید',
                    content_object=terms_order,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='MEDIUM',
                    extra_data={
                        'order_number': terms_order.order_number,
                        'payment_type': 'terms',
                        'amount': str(terms_order.final_amount),
                        'items_count': len(terms_items)
                    }
                )
        
        # Clear selected products and processing order from session
        if 'selected_products' in request.session:
            del request.session['selected_products']
        if 'processing_order_id' in request.session:
            del request.session['processing_order_id']
        
        # Prepare response based on payment types
        if cash_items and terms_items:
            message = f'✅ سفارش شما با موفقیت ثبت شد!\n\n💵 سفارش نقدی: {total_cash:,.0f} تومان\n📅 سفارش قسطی: {total_terms:,.0f} تومان\n\nسفارش قسطی شما در انتظار تایید ادمین است.'
            redirect_url = f'/payments/summary/{processing_order.id}/'  # Redirect to payment summary for cash items
        elif cash_items:
            message = f'✅ سفارش نقدی شما با موفقیت ثبت شد!\n💰 مبلغ: {total_cash:,.0f} تومان\n\nبرای تکمیل خرید، به بخش پرداخت هدایت خواهید شد.'
            redirect_url = f'/payments/summary/{processing_order.id}/'  # Redirect to payment summary
        else:
            message = f'✅ سفارش قسطی شما با موفقیت ثبت شد!\n💰 مبلغ: {total_terms:,.0f} تومان\n\nسفارش شما در انتظار تایید ادمین است.'
            redirect_url = '/accounts/customer/dashboard/'  # Redirect to dashboard
        
        return JsonResponse({
            'success': True,
            'message': message,
            'has_cash_items': bool(cash_items),
            'cash_total': total_cash,
            'terms_total': total_terms,
            'orders_created': len(orders_created),
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'خطا در پردازش سفارش: {str(e)}'
        })


@login_required
def customer_orders_view(request):
    """📋 لیست سفارشات مشتری با جزئیات پرداخت"""
    # فقط کاربران با نقش مشتری می‌توانند دسترسی داشته باشند
    if request.user.role != User.UserRole.CUSTOMER:
        messages.error(request, '❌ دسترسی مجاز نیست')
        return redirect('core:admin_dashboard')

    # 📜 ثبت لاگ مشاهده سفارشات
    ActivityLog.log_activity(
        user=request.user,
        action='VIEW',
        description='مشاهده لیست سفارشات توسط مشتری',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='LOW'
    )

    user_name = request.user.get_full_name() or request.user.username
    user_phone = request.user.phone

    orders = Order.objects.select_related('customer', 'created_by').prefetch_related('order_items')

    # Debug: print user info
    print(f"[DEBUG] User: id={request.user.id}, username={request.user.username}, phone={user_phone}, name={user_name}")

    # Try to find a direct customer link (if exists)
    direct_customer_orders = Order.objects.none()
    customer_obj = None
    if hasattr(request.user, 'customer') and request.user.customer:
        customer_obj = request.user.customer
        direct_customer_orders = orders.filter(customer=customer_obj)
        print(f"[DEBUG] Found direct customer: id={customer_obj.id}, name={customer_obj.customer_name}, phone={customer_obj.phone}")
        print(f"[DEBUG] Orders by direct customer: {direct_customer_orders.count()}")
    else:
        print("[DEBUG] No direct customer linked to user.")

    # Also include orders by phone or name
    if user_phone:
        phone_name_orders = orders.filter(
            Q(customer__phone=user_phone) |
            Q(customer__customer_name__icontains=user_name.strip())
        )
        print(f"[DEBUG] Orders by phone or name: {phone_name_orders.count()}")
    else:
        phone_name_orders = orders.filter(customer__customer_name__icontains=user_name.strip())
        print(f"[DEBUG] Orders by name only: {phone_name_orders.count()}")

    # Combine both querysets, remove duplicates
    orders = (direct_customer_orders | phone_name_orders).distinct()
    print(f"[DEBUG] Total orders after union: {orders.count()}")

    # 🔒 SECURITY: Only exclude cancelled orders - show all other orders regardless of payment status
    orders = orders.exclude(status='Cancelled')  # Exclude cancelled orders only
    print(f"[DEBUG] Orders after excluding cancelled orders: {orders.count()}")

    # دریافت پارامترهای فیلتر از URL
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    payment_filter = request.GET.get('payment', '').strip()
    filter_by = request.GET.get('filter_by', 'date').strip()
    
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

    # مرتب‌سازی بر اساس فیلتر انتخاب شده
    if filter_by == 'last_changes':
        # مرتب‌سازی بر اساس آخرین تغییرات (updated_at)
        orders = orders.order_by('-updated_at')
    else:
        # مرتب‌سازی بر اساس تاریخ ایجاد (created_at) - پیش‌فرض
        orders = orders.order_by('-created_at')

    # 📄 صفحه‌بندی
    paginator = Paginator(orders, 10)  # کمتر برای مشتریان
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    # 💳 اضافه کردن اطلاعات پرداخت برای هر سفارش
    for order in page_obj:
        order.latest_payment = Payment.objects.filter(order=order).order_by('-created_at').first()
        order.all_payments = Payment.objects.filter(order=order).order_by('-created_at')
        order.has_cash_items = order.order_items.filter(payment_method='Cash').exists()

    context = {
        'title': '📋 سفارشات من',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'filter_by': filter_by,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_METHOD_CHOICES,
        'total_orders': orders.count(),
    }
    return render(request, 'core/customer_orders.html', context)

@login_required
@super_admin_permission_required('manage_customers')
def customer_detail_modal_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('modal'):
        html = render_to_string('core/partials/customer_detail_modal.html', {'customer': customer}, request=request)
        return HttpResponse(html)
    return redirect('core:customers_list')

@login_required
@super_admin_permission_required('manage_inventory')
def product_detail_modal_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_logs = ActivityLog.objects.filter(
        content_type__model='product',
        object_id=product.id
    ).select_related('user')[:20]
    context = {
        'product': product,
        'product_info': product.get_product_info(),
        'product_logs': product_logs,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('modal'):
        html = render_to_string('core/partials/product_detail_modal.html', context, request=request)
        return HttpResponse(html)
    from django.shortcuts import redirect
    return redirect('core:products_list')

@login_required
@super_admin_permission_required('manage_inventory')
@require_POST
def product_delete_api(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'message': 'No product ID provided.'}, status=400)
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        reel_number = product.reel_number
        product.delete()
        ActivityLog.log_activity(
            user=request.user,
            action='DELETE',
            description=f'Product {reel_number} deleted',
            severity='HIGH',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return JsonResponse({'success': True, 'message': f'Product {reel_number} deleted successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@super_admin_permission_required('manage_inventory')
@require_POST
def bulk_delete_products_api(request):
    """🗑️ حذف گروهی محصولات - فقط Super Admin"""
    try:
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return JsonResponse({
                'success': False, 
                'message': '❌ هیچ محصولی برای حذف انتخاب نشده است'
            }, status=400)
        
        # بررسی وجود محصولات
        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            return JsonResponse({
                'success': False, 
                'message': '❌ هیچ محصول معتبری یافت نشد'
            }, status=404)
        
        # ذخیره اطلاعات برای لاگ
        deleted_products = []
        for product in products:
            deleted_products.append({
                'id': product.id,
                'reel_number': product.reel_number,
                'location': product.get_location_display(),
                'status': product.get_status_display()
            })
        
        # حذف محصولات
        deleted_count = products.count()
        products.delete()
        
        # ثبت لاگ حذف گروهی
        ActivityLog.log_activity(
            user=request.user,
            action='DELETE',
            description=f'حذف گروهی {deleted_count} محصول',
            severity='HIGH',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            extra_data={
                'deleted_count': deleted_count,
                'deleted_products': deleted_products
            }
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'✅ {deleted_count} محصول با موفقیت حذف شد',
            'deleted_count': deleted_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': '❌ فرمت JSON نامعتبر است'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'❌ خطا در حذف محصولات: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_working_hours_config_api(request):
    """
    ⚙️ دریافت تنظیمات ساعات کاری برای فرانت‌اند
    
    🎯 این API برای دریافت تنظیمات ساعات کاری و محدودیت‌های انتخاب محصول استفاده می‌شود
    📱 فرانت‌اند از این اطلاعات برای اعمال محدودیت‌های انتخاب استفاده می‌کند
    """
    
    try:
        current_hours = WorkingHours.get_current_working_hours()
        
        if not current_hours:
            return JsonResponse({
                'success': False,
                'error': '⏰ ساعات کاری تنظیم نشده است'
            }, status=404)
        
        config = {
            'success': True,
            'max_selection_limit': current_hours.max_selection_limit,
            'is_shop_open': WorkingHours.is_shop_open(),
            'is_thursday_open': current_hours.is_thursday_open,
            'is_holiday': current_hours.is_holiday,
            'holiday_help_text': current_hours.holiday_help_text,
            'working_hours': current_hours.get_working_hours_info()
        }
        
        return JsonResponse(config)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'❌ خطا در دریافت تنظیمات: {str(e)}'
        }, status=500)


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
        is_thursday_open = data.get('is_thursday_open', False)
        is_holiday = data.get('is_holiday', False)
        holiday_help_text = data.get('holiday_help_text', '')
        max_selection_limit = data.get('max_selection_limit', 6)
        
        # 🧹 اعتبارسنجی داده‌ها
        if not start_time or not end_time:
            return JsonResponse({
                'success': False,
                'error': '⏰ زمان شروع و پایان کار الزامی است'
            }, status=400)
        
        # 🔢 اعتبارسنجی حداکثر انتخاب
        try:
            max_selection_limit = int(max_selection_limit)
            if max_selection_limit < 1 or max_selection_limit > 50:
                return JsonResponse({
                    'success': False,
                    'error': '🔢 حداکثر انتخاب باید بین 1 تا 50 باشد'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': '🔢 حداکثر انتخاب باید عدد معتبر باشد'
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
            is_thursday_open=is_thursday_open,
            is_holiday=is_holiday,
            holiday_help_text=holiday_help_text,
            max_selection_limit=max_selection_limit,
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


@login_required
@require_http_methods(["POST"])
def cancel_draft_order_view(request):
    """❌ لغو سفارش پیش‌نویس و بازگرداندن محصولات به انبار"""
    try:
        # Get customer
        customer = request.user.customer
        if not customer:
            return JsonResponse({
                'success': False,
                'error': '❌ اطلاعات مشتری یافت نشد.'
            })
        
        # Find the processing order for this customer
        processing_order = Order.objects.filter(
            customer=customer,
            status='Processing'
        ).first()
        
        if not processing_order:
            return JsonResponse({
                'success': False,
                'error': '❌ سفارش در حال پردازش یافت نشد.'
            })
        
        # Cancel the order and return products to stock
        from django.db import transaction
        with transaction.atomic():
            # Get all order items
            order_items = processing_order.order_items.all()
            
            # Return products to stock
            for item in order_items:
                product = item.product
                if product.status == 'Pre-order':
                    product.status = 'In-stock'
                    product.save()
                    print(f"[DEBUG] Product {product.reel_number} returned to stock")
            
            # Update order status to cancelled
            processing_order.status = 'Cancelled'
            processing_order.notes = f'سفارش لغو شده - مشتری از صفحه خارج شد - تاریخ لغو: {processing_order.updated_at}'
            processing_order.save()
            
            # Log the cancellation
            ActivityLog.log_activity(
                user=request.user,
                action='ORDER',
                description=f'سفارش {processing_order.order_number} لغو شد - مشتری از صفحه خارج شد',
                content_object=processing_order,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                severity='MEDIUM',
                extra_data={
                    'order_number': processing_order.order_number,
                    'cancellation_reason': 'page_exit',
                    'items_count': order_items.count(),
                    'total_amount': str(processing_order.final_amount)
                }
            )
            
            # Clear session data
            if 'processing_order_id' in request.session:
                del request.session['processing_order_id']
            if 'selected_products' in request.session:
                del request.session['selected_products']
        
        return JsonResponse({
            'success': True,
            'message': f'✅ سفارش {processing_order.order_number} لغو شد و محصولات به انبار بازگردانده شدند.',
            'cancelled_items': order_items.count()
        })
        
    except Exception as e:
        print(f"[DEBUG] Error cancelling draft order: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'خطا در لغو سفارش: {str(e)}'
        })


@login_required
@check_user_permission('is_super_admin')
@require_http_methods(["POST"])
def manual_cancel_expired_orders_view(request):
    """
    🚫 لغو دستی سفارشات Processing منقضی شده - فقط Super Admin
    
    🎯 این API برای اجرای دستی تابع لغو خودکار سفارشات استفاده می‌شود
    ✅ فقط Super Admin می‌تواند این عملیات را انجام دهد
    📊 نتیجه عملیات را برمی‌گرداند
    """
    
    try:
        # 📥 دریافت پارامترهای اختیاری
        data = json.loads(request.body) if request.body else {}
        timeout_minutes = data.get('timeout_minutes')
        dry_run = data.get('dry_run', False)
        
        # 🔍 بررسی دسترسی
        if not request.user.is_super_admin():
            return JsonResponse({
                'success': False,
                'error': '🚫 فقط Super Admin می‌تواند این عملیات را انجام دهد'
            }, status=403)
        
        # 📜 ثبت لاگ شروع عملیات
        ActivityLog.log_activity(
            user=request.user,
            action='INFO',
            description=f'شروع لغو دستی سفارشات منقضی شده - حالت تست: {dry_run}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='MEDIUM',
            extra_data={
                'operation': 'manual_cancel_expired_orders',
                'dry_run': dry_run,
                'timeout_minutes': timeout_minutes
            }
        )
        
        if dry_run:
            # 🔍 حالت تست - فقط نمایش سفارشات
            from datetime import timedelta
            
            current_timeout = timeout_minutes or getattr(settings, 'ORDER_CANCELLATION_TIMEOUT', 5)
            expiration_time = timezone.now() - timedelta(minutes=current_timeout)
            
            expired_orders = Order.objects.filter(
                status='Processing',
                updated_at__lt=expiration_time
            ).select_related('customer')
            
            orders_info = []
            for order in expired_orders:
                time_in_processing = timezone.now() - order.updated_at
                minutes_in_processing = int(time_in_processing.total_seconds() / 60)
                
                orders_info.append({
                    'order_number': order.order_number,
                    'customer_name': order.customer.customer_name,
                    'minutes_in_processing': minutes_in_processing,
                    'last_updated': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'final_amount': str(order.final_amount),
                    'items_count': order.order_items.count()
                })
            
            return JsonResponse({
                'success': True,
                'message': f'🔍 {len(orders_info)} سفارش Processing منقضی شده یافت شد',
                'dry_run': True,
                'timeout_minutes': current_timeout,
                'expired_orders': orders_info
            })
        
        else:
            # 🚫 اجرای واقعی لغو خودکار
            from core.signals import schedule_order_cancellation_check
            
            cancelled_count = schedule_order_cancellation_check()
            
            # 📜 ثبت لاگ نتیجه
            ActivityLog.log_activity(
                user=request.user,
                action='CANCEL',
                description=f'لغو دستی سفارشات منقضی شده - {cancelled_count} سفارش لغو شد',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                severity='HIGH',
                extra_data={
                    'operation': 'manual_cancel_expired_orders',
                    'cancelled_count': cancelled_count,
                    'timeout_minutes': timeout_minutes
                }
            )
            
            if cancelled_count > 0:
                return JsonResponse({
                    'success': True,
                    'message': f'✅ {cancelled_count} سفارش Processing به صورت خودکار لغو شد',
                    'cancelled_count': cancelled_count
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': '✅ هیچ سفارشی برای لغو یافت نشد',
                    'cancelled_count': 0
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
            description=f'خطا در لغو دستی سفارشات منقضی شده: {str(e)}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='HIGH'
        )
        
        return JsonResponse({
            'success': False,
            'error': f'❌ خطا در لغو دستی سفارشات: {str(e)}'
        }, status=500)


@login_required
@check_user_permission('is_super_admin')
@require_http_methods(["GET", "POST"])
def automation_control_view(request):
    """
    🤖 کنترل سیستم خودکار لغو سفارشات - فقط Super Admin
    
    🎯 این API برای کنترل سیستم خودکار استفاده می‌شود
    ✅ فقط Super Admin می‌تواند این عملیات را انجام دهد
    📊 وضعیت سیستم را نمایش می‌دهد
    """
    
    try:
        from core.signals import (
            start_automated_cancellation, 
            stop_automated_cancellation, 
            is_automation_running,
            set_automation_interval
        )
        
        if request.method == "GET":
            # 📊 نمایش وضعیت سیستم
            automation_status = is_automation_running()
            
            # 📈 آمار سفارشات
            processing_count = Order.objects.filter(status='Processing').count()
            cancelled_count = Order.objects.filter(status='Cancelled').count()
            
            # 📝 لاگ‌های اخیر
            recent_logs = ActivityLog.objects.filter(
                action__in=['CANCEL', 'UPDATE'],
                extra_data__automated=True
            ).order_by('-created_at')[:5]
            
            return JsonResponse({
                'success': True,
                'automation_running': automation_status,
                'processing_orders': processing_count,
                'cancelled_orders': cancelled_count,
                'recent_automated_actions': [
                    {
                        'time': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'action': log.action,
                        'description': log.description
                    } for log in recent_logs
                ]
            })
        
        elif request.method == "POST":
            # 🔧 کنترل سیستم
            data = json.loads(request.body) if request.body else {}
            action = data.get('action')
            
            if action == 'start':
                # 🚀 شروع سیستم خودکار
                thread = start_automated_cancellation()
                
                ActivityLog.log_activity(
                    user=request.user,
                    action='INFO',
                    description='سیستم خودکار لغو سفارشات شروع شد',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='HIGH'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': '🤖 سیستم خودکار شروع شد',
                    'thread_id': thread.ident if thread else None
                })
            
            elif action == 'stop':
                # 🛑 توقف سیستم خودکار
                stopped = stop_automated_cancellation()
                
                ActivityLog.log_activity(
                    user=request.user,
                    action='INFO',
                    description='سیستم خودکار لغو سفارشات متوقف شد',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='HIGH'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': '🛑 سیستم خودکار متوقف شد',
                    'stopped': stopped
                })
            
            elif action == 'set_interval':
                # ⏰ تنظیم فاصله زمانی
                interval = data.get('interval', 60)
                new_interval = set_automation_interval(interval)
                
                ActivityLog.log_activity(
                    user=request.user,
                    action='UPDATE',
                    description=f'فاصله بررسی خودکار به {new_interval} ثانیه تغییر کرد',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='MEDIUM'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'⏰ فاصله بررسی به {new_interval} ثانیه تنظیم شد',
                    'interval': new_interval
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': '❌ عملیات نامعتبر'
                }, status=400)
        
    except Exception as e:
        # 📜 ثبت خطا
        ActivityLog.log_activity(
            user=request.user,
            action='ERROR',
            description=f'خطا در کنترل سیستم خودکار: {str(e)}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='HIGH'
        )
        
        return JsonResponse({
            'success': False,
            'error': f'❌ خطا در کنترل سیستم خودکار: {str(e)}'
        }, status=500)






