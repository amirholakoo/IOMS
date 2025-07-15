"""
👥 ویوهای مدیریت کاربران و نقش‌ها - HomayOMS
🔐 شامل لاگین، خروج، مدیریت کاربران و کنترل دسترسی
🎯 با تأکید بر امنیت و تجربه کاربری بهینه
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.urls import reverse
from .models import User
from .permissions import check_user_permission, super_admin_permission_required
from core.models import Customer, ActivityLog
import string
import random
from datetime import timedelta
from django.db.models import Q
from django.db import IntegrityError, transaction


def login_view(request):
    """🔐 صفحه ورود اصلی با 4 گزینه مختلف"""
    if request.user.is_authenticated:
        if request.user.is_customer():
            return redirect('accounts:customer_dashboard')
        else:
            return redirect('core:admin_dashboard')
    
    return render(request, 'accounts/login.html')


def staff_login_view(request):
    """👥 ورود کارمندان (Super Admin, Admin, Finance)"""
    if request.user.is_authenticated:
        return redirect('core:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        # بررسی نقش انتخاب شده
        valid_staff_roles = [
            User.UserRole.SUPER_ADMIN,
            User.UserRole.ADMIN, 
            User.UserRole.FINANCE
        ]
        
        if role not in valid_staff_roles:
            messages.error(request, '❌ نقش انتخاب شده نامعتبر است')
            return render(request, 'accounts/staff_login.html')
        
        user = authenticate(request, username=username, password=password)
        if user and user.status == User.UserStatus.ACTIVE and user.role == role:
            login(request, user)
            role_names = {
                User.UserRole.SUPER_ADMIN: 'مدیر ارشد',
                User.UserRole.ADMIN: 'ادمین',
                User.UserRole.FINANCE: 'مالی'
            }
            messages.success(request, f'🎉 خوش آمدید {role_names[role]} {user.get_full_name() or user.username}!')
            return redirect('core:admin_dashboard')
        else:
            messages.error(request, '❌ نام کاربری، رمز عبور یا نقش اشتباه است')
    
    return render(request, 'accounts/staff_login.html')


def customer_login_view(request):
    """🔵 ورود مشتریان - هدایت به صفحه SMS"""
    if request.user.is_authenticated:
        if request.user.is_customer():
            return redirect('accounts:customer_dashboard')
        else:
            return redirect('core:admin_dashboard')
    
    # مستقیماً به صفحه SMS login هدایت می‌کنیم
    return redirect('accounts:customer_sms_login')


def customer_registration_view(request):
    """
    📝 ثبت‌نام مشتری جدید
    🔐 ایجاد حساب کاربری جدید با وضعیت PENDING
    """
    if request.method == 'POST':
        # دریافت اطلاعات فرم
        phone = request.POST.get('phone', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        economic_code = request.POST.get('economic_code', '').strip()
        national_id = request.POST.get('national_id', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        
        # اعتبارسنجی فیلدهای اجباری
        errors = []
        if not phone:
            errors.append('📱 شماره تلفن الزامی است')
        elif not phone.startswith('09') or len(phone) != 11:
            errors.append('📱 شماره تلفن باید با 09 شروع شده و 11 رقم باشد')
        
        if not first_name:
            errors.append('👤 نام الزامی است')
        
        if not last_name:
            errors.append('👤 نام خانوادگی الزامی است')
        
        # بررسی تکراری نبودن شماره تلفن
        user_exists = User.objects.filter(phone=phone).exists()
        print(f"[DEBUG] User exists for phone {phone}: {user_exists}")
        if user_exists:
            errors.append('📱 این شماره تلفن قبلاً ثبت شده است')
        
        # جلوگیری از ثبت مشتری تکراری با شماره موبایل
        customer_exists = Customer.objects.filter(phone=phone).exists()
        print(f"[DEBUG] Customer exists (any status) for phone {phone}: {customer_exists}")
        if customer_exists:
            errors.append('👤 مشتری با این شماره قبلاً ثبت شده است')
        
        # بررسی تکراری نبودن ایمیل (در صورت وارد کردن)
        if email and User.objects.filter(email=email).exists():
            errors.append('📧 این ایمیل قبلاً ثبت شده است')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            if request.user.is_authenticated and request.user.is_super_admin():
                return redirect('core:customers_list')
            else:
                return render(request, 'accounts/customer_registration.html', {
                    'form_data': request.POST
                })
        
        try:
            # تولید نام کاربری منحصر به فرد
            base_username = f"{first_name}_{last_name}".lower().replace(' ', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            # ایجاد کاربر جدید با وضعیت PENDING
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=None,  # کاربران Customer رمز عبور ندارند
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    role=User.UserRole.CUSTOMER,
                    status=User.UserStatus.PENDING,  # وضعیت در انتظار تایید
                    is_active=False,  # غیرفعال تا تایید شود
                    date_joined=timezone.now()
                )
                
                # ثبت لاگ ثبت‌نام جدید
                ActivityLog.log_activity(
                    user=None,  # کاربر هنوز تایید نشده
                    action='CREATE',
                    description=f'📝 درخواست ثبت‌نام جدید مشتری: {first_name} {last_name} - {phone}',
                    content_object=user,
                    severity='MEDIUM',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    registration_data={
                        'phone': phone,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'address': address,
                        'economic_code': economic_code,
                        'national_id': national_id,
                        'postcode': postcode
                    }
                )
                
                # فعال کردن کاربر نیز
                user.status = User.UserStatus.ACTIVE
                user.is_active = True
                user.save()
                
                # ثبت لاگ تغییر وضعیت
                ActivityLog.log_activity(
                    user=request.user,
                    action='APPROVE',
                    description=f'✅ تایید و فعال‌سازی مشتری جدید: {first_name} {last_name} ({phone})',
                    content_object=user,  # log on user, not customer
                    severity='MEDIUM',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    status_change={
                        'user_status': 'active',
                        'customer_status': 'Active',
                        'activated_by': request.user.username
                    }
                )
                
                messages.success(request, 
                    f'✅ مشتری جدید "{first_name} {last_name}" با موفقیت ثبت شد و فعال است! 📞 شماره: {phone}'
                )
                request.session['show_success'] = True
                return redirect('core:customers_list')
        except IntegrityError as e:
            print(f"[DEBUG] IntegrityError occurred: {e}")
            print(f"[DEBUG] Error details: {str(e)}")
            error_message = '❌ این شماره موبایل قبلاً ثبت شده است. اگر رمز عبور را فراموش کرده‌اید، از بازیابی رمز استفاده کنید.'
            if request.user.is_authenticated and request.user.is_super_admin():
                messages.error(request, error_message)
                return redirect('core:customers_list')
            else:
                messages.error(request, error_message)
                return render(request, 'accounts/customer_registration.html', {
                    'form_data': request.POST
                })
        except Exception as e:
            error_message = '❌ خطا در ثبت‌نام. لطفاً مجدداً تلاش کنید'
            if request.user.is_authenticated and request.user.is_super_admin():
                messages.error(request, f'{error_message} (جزئیات: {str(e)})')
                return redirect('core:customers_list')
            else:
                print(f"❌ Error in customer registration: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, error_message)
                return render(request, 'accounts/customer_registration.html', {
                    'form_data': request.POST
                })
    
    # GET request - نمایش فرم ثبت‌نام
    phone = request.GET.get('phone') or request.session.get('registration_phone', '')
    return render(request, 'accounts/customer_registration.html', {
        'phone': phone,
        'form_data': {},
    })


@login_required
def customer_dashboard_view(request):
    """🔵 داشبورد مخصوص مشتریان"""
    # Super Admin می‌تواند به تمام بخش‌ها دسترسی داشته باشد
    if not request.user.is_customer() and not request.user.is_super_admin():
        messages.error(request, '❌ شما دسترسی به این بخش را ندارید')
        return redirect('core:admin_dashboard')
    
    # دریافت اطلاعات مشتری مرتبط
    customer = Customer.objects.filter(
        customer_name=request.user.get_full_name() or request.user.username
    ).first()
    
    context = {
        'user': request.user,
        'customer': customer,
        'role_features': request.user.get_accessible_features(),
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required
def logout_view(request):
    """🚪 خروج کاربر از سیستم"""
    username = request.user.username
    logout(request)
    messages.success(request, f'👋 {username} با موفقیت خارج شدید')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """📊 داشبورد اصلی کاربران"""
    # اگر کاربر مشتری است، به داشبورد مشتری هدایت شود
    if request.user.is_customer():
        return redirect('accounts:customer_dashboard')
    
    context = {
        'user': request.user,
        'role_features': request.user.get_accessible_features(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    """👤 نمایش و ویرایش پروفایل کاربر"""
    if request.method == 'POST':
        # دریافت داده‌های فرم
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        # اعتبارسنجی داده‌ها
        errors = []
        if not first_name:
            errors.append('نام نمی‌تواند خالی باشد')
        if not last_name:
            errors.append('نام خانوادگی نمی‌تواند خالی باشد')
        if email and '@' not in email:
            errors.append('ایمیل وارد شده معتبر نیست')
        
        if errors:
            for error in errors:
                messages.error(request, f'❌ {error}')
        else:
            try:
                # بروزرسانی اطلاعات کاربر
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                
                messages.success(request, '✅ اطلاعات پروفایل با موفقیت بروزرسانی شد')
                
                # ثبت فعالیت
                ActivityLog.log_activity(
                    user=user,
                    action='profile_updated',
                    description=f'پروفایل کاربر {user.username} بروزرسانی شد',
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return redirect('accounts:profile')
                
            except Exception as e:
                messages.error(request, f'❌ خطا در بروزرسانی اطلاعات: {str(e)}')
    
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """🔐 تغییر رمز عبور"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # اعتبارسنجی رمز عبور فعلی
        if not request.user.check_password(old_password):
            messages.error(request, '❌ رمز عبور فعلی اشتباه است')
            return render(request, 'accounts/change_password.html')
        
        # بررسی تطابق رمزهای عبور جدید
        if new_password1 != new_password2:
            messages.error(request, '❌ رمزهای عبور جدید مطابقت ندارند')
            return render(request, 'accounts/change_password.html')
        
        # بررسی طول رمز عبور
        if len(new_password1) < 8:
            messages.error(request, '❌ رمز عبور جدید باید حداقل 8 کاراکتر باشد')
            return render(request, 'accounts/change_password.html')
        
        try:
            # تغییر رمز عبور
            user = request.user
            user.set_password(new_password1)
            user.save()
            
            # بروزرسانی نشست کاربر
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            
            messages.success(request, '✅ رمز عبور با موفقیت تغییر یافت')
            
            # ثبت فعالیت
            ActivityLog.log_activity(
                user=user,
                action='password_changed',
                description=f'رمز عبور کاربر {user.username} تغییر یافت',
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return redirect('accounts:change_password')
            
        except Exception as e:
            messages.error(request, f'❌ خطا در تغییر رمز عبور: {str(e)}')
    
    return render(request, 'accounts/change_password.html')


@login_required
@super_admin_permission_required('accounts.manage_all_users')
def user_list_view(request):
    """👥 لیست کاربران با فیلتر و جستجو"""
    
    # شروع با تمام کاربران
    users = User.objects.all()
    
    # دریافت پارامترهای فیلتر از URL
    search_query = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # اعمال فیلتر جستجو
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # اعمال فیلتر نقش
    if role_filter and role_filter in [choice[0] for choice in User.UserRole.choices]:
        users = users.filter(role=role_filter)
    
    # اعمال فیلتر وضعیت
    if status_filter and status_filter in [choice[0] for choice in User.UserStatus.choices]:
        users = users.filter(status=status_filter)
    
    # مرتب‌سازی
    users = users.order_by('-created_at')
    
    # صفحه‌بندی
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_roles': User.UserRole.choices,
        'user_statuses': User.UserStatus.choices,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total_users': users.count(),
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@super_admin_permission_required('accounts.manage_all_users')
def user_detail_view(request, user_id):
    """👤 جزئیات کاربر"""
    user_obj = get_object_or_404(User, id=user_id)
    context = {'user_obj': user_obj}
    return render(request, 'accounts/user_detail.html', context)


@login_required
@super_admin_permission_required('accounts.manage_all_users')
@require_http_methods(["POST"])
def update_user_status(request, user_id):
    """📊 تغییر وضعیت کاربر"""
    user_obj = get_object_or_404(User, id=user_id)
    new_status = request.POST.get('status')
    
    if new_status in [choice[0] for choice in User.UserStatus.choices]:
        user_obj.status = new_status
        user_obj.save()
        return JsonResponse({'success': True, 'message': 'وضعیت بروزرسانی شد'})
    
    return JsonResponse({'success': False, 'message': 'وضعیت نامعتبر'})


@login_required
@super_admin_permission_required('accounts.manage_all_users')
def add_user_view(request):
    """➕ اضافه کردن کاربر جدید"""
    if request.method == 'POST':
        # دریافت داده‌های فرم
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').strip()
        status = request.POST.get('status', '').strip()
        department = request.POST.get('department', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        # اعتبارسنجی داده‌ها
        errors = []
        
        # بررسی فیلدهای اجباری
        if not username:
            errors.append('نام کاربری اجباری است')
        elif User.objects.filter(username=username).exists():
            errors.append('نام کاربری قبلاً استفاده شده است')
        
        if not first_name:
            errors.append('نام اجباری است')
        
        if not last_name:
            errors.append('نام خانوادگی اجباری است')
        
        if not phone:
            errors.append('شماره تلفن اجباری است')
        elif User.objects.filter(phone=phone).exists():
            errors.append('شماره تلفن قبلاً استفاده شده است')
        elif not phone.startswith('09'):
            errors.append('شماره تلفن باید با 09 شروع شود')
        
        # برای نقش‌های غیر از Customer، رمز عبور اجباری است
        if role != 'customer':
            if not password:
                errors.append('رمز عبور اجباری است')
            elif len(password) < 6:
                errors.append('رمز عبور باید حداقل 6 کاراکتر باشد')
        # برای Customer، رمز عبور اختیاری است
        elif password and len(password) < 6:
            errors.append('رمز عبور باید حداقل 6 کاراکتر باشد')
        
        if role not in [choice[0] for choice in User.UserRole.choices]:
            errors.append('نقش انتخاب شده نامعتبر است')
        
        if status not in [choice[0] for choice in User.UserStatus.choices]:
            errors.append('وضعیت انتخاب شده نامعتبر است')
        
        if email and '@' not in email:
            errors.append('ایمیل وارد شده معتبر نیست')
        
        if errors:
            for error in errors:
                messages.error(request, f'❌ {error}')
        else:
            try:
                with transaction.atomic():
                    # ایجاد کاربر جدید
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password if password else None,  # برای Customer رمز عبور اختیاری است
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        role=role,
                        status=status,
                        department=department,
                        notes=notes,
                        is_active=True if status == User.UserStatus.ACTIVE else False
                    )
                    
                    # ثبت فعالیت
                    ActivityLog.log_activity(
                        user=request.user,
                        action='user_created',
                        description=f'کاربر جدید {username} با نقش {role} ایجاد شد',
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    messages.success(request, f'✅ کاربر {user.get_full_name() or username} با موفقیت ایجاد شد')
                    return redirect('accounts:user_list')
                    
            except Exception as e:
                messages.error(request, f'❌ خطا در ایجاد کاربر: {str(e)}')
    
    context = {
        'user_roles': User.UserRole.choices,
        'user_statuses': User.UserStatus.choices,
        'form_action': 'add',
        'form_title': 'اضافه کردن کاربر جدید'
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
@super_admin_permission_required('accounts.manage_all_users')
def edit_user_view(request, user_id):
    """✏️ ویرایش کاربر"""
    user_obj = get_object_or_404(User, id=user_id)
    
    # جلوگیری از ویرایش خودی توسط Super Admin
    if user_obj == request.user:
        messages.warning(request, '⚠️ شما نمی‌توانید اطلاعات خود را از اینجا ویرایش کنید. از بخش پروفایل استفاده کنید.')
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        # دریافت داده‌های فرم
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').strip()
        status = request.POST.get('status', '').strip()
        department = request.POST.get('department', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        # اعتبارسنجی داده‌ها
        errors = []
        
        # بررسی فیلدهای اجباری
        if not username:
            errors.append('نام کاربری اجباری است')
        elif User.objects.filter(username=username).exclude(id=user_id).exists():
            errors.append('نام کاربری قبلاً استفاده شده است')
        
        if not first_name:
            errors.append('نام اجباری است')
        
        if not last_name:
            errors.append('نام خانوادگی اجباری است')
        
        if not phone:
            errors.append('شماره تلفن اجباری است')
        elif User.objects.filter(phone=phone).exclude(id=user_id).exists():
            errors.append('شماره تلفن قبلاً استفاده شده است')
        elif not phone.startswith('09'):
            errors.append('شماره تلفن باید با 09 شروع شود')
        
        if password and len(password) < 6:
            errors.append('رمز عبور باید حداقل 6 کاراکتر باشد')
        
        if role not in [choice[0] for choice in User.UserRole.choices]:
            errors.append('نقش انتخاب شده نامعتبر است')
        
        if status not in [choice[0] for choice in User.UserStatus.choices]:
            errors.append('وضعیت انتخاب شده نامعتبر است')
        
        if email and '@' not in email:
            errors.append('ایمیل وارد شده معتبر نیست')
        
        if errors:
            for error in errors:
                messages.error(request, f'❌ {error}')
        else:
            try:
                with transaction.atomic():
                    # بروزرسانی اطلاعات کاربر
                    user_obj.username = username
                    user_obj.first_name = first_name
                    user_obj.last_name = last_name
                    user_obj.email = email
                    user_obj.phone = phone
                    user_obj.role = role
                    user_obj.status = status
                    user_obj.department = department
                    user_obj.notes = notes
                    user_obj.is_active = True if status == User.UserStatus.ACTIVE else False
                    
                    # اگر رمز عبور وارد شده، تغییر دهید
                    if password:
                        user_obj.set_password(password)
                    
                    user_obj.save()
                    
                    # ثبت فعالیت
                    ActivityLog.log_activity(
                        user=request.user,
                        action='user_updated',
                        description=f'کاربر {username} با نقش {role} به‌روزرسانی شد',
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    messages.success(request, f'✅ کاربر {user_obj.get_full_name() or username} با موفقیت به‌روزرسانی شد')
                    return redirect('accounts:user_list')
                    
            except Exception as e:
                messages.error(request, f'❌ خطا در به‌روزرسانی کاربر: {str(e)}')
    
    context = {
        'user_obj': user_obj,
        'user_roles': User.UserRole.choices,
        'user_statuses': User.UserStatus.choices,
        'form_action': 'edit',
        'form_title': f'ویرایش کاربر: {user_obj.get_full_name() or user_obj.username}'
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
@super_admin_permission_required('accounts.manage_all_users')
def delete_user_view(request, user_id):
    """🗑️ حذف کاربر"""
    user_obj = get_object_or_404(User, id=user_id)
    
    # جلوگیری از حذف خودی توسط Super Admin
    if user_obj == request.user:
        messages.error(request, '❌ شما نمی‌توانید حساب کاربری خود را حذف کنید')
        return redirect('accounts:user_list')
    
    # جلوگیری از حذف Super Admin توسط Super Admin دیگر
    if user_obj.is_super_admin():
        messages.error(request, '❌ امکان حذف Super Admin وجود ندارد')
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                username = user_obj.username
                full_name = user_obj.get_full_name() or username
                
                # ثبت فعالیت قبل از حذف
                ActivityLog.log_activity(
                    user=request.user,
                    action='user_deleted',
                    description=f'کاربر {username} با نقش {user_obj.role} حذف شد',
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # حذف کاربر
                user_obj.delete()
                
                messages.success(request, f'✅ کاربر {full_name} با موفقیت حذف شد')
                return redirect('accounts:user_list')
                
        except Exception as e:
            messages.error(request, f'❌ خطا در حذف کاربر: {str(e)}')
    
    context = {
        'user_obj': user_obj,
        'form_title': f'حذف کاربر: {user_obj.get_full_name() or user_obj.username}'
    }
    return render(request, 'accounts/user_delete.html', context)


@login_required
def user_permissions_api(request):
    """API مجوزهای کاربر"""
    return JsonResponse({
        'role': request.user.role,
        'is_super_admin': request.user.is_super_admin(),
        'is_admin': request.user.is_admin(),
        'is_finance': request.user.is_finance(),
        'is_customer': request.user.is_customer(),
    })


@login_required
def check_password_strength(request):
    """🔐 بررسی قوت رمز عبور"""
    password = request.POST.get('password', '')
    score = len(password) * 10  # Simple scoring
    return JsonResponse({'score': min(score, 100), 'level': 'خوب'})


def terms_and_request_view(request):
    """
    نمایش شرایط استفاده و ثبت درخواست مشتری جدید
    """
    phone = request.GET.get('phone') or request.session.get('registration_phone', '')
    
    # بررسی وجود مشتری با وضعیت Requested
    if phone:
        from core.models import Customer
        requested_customer = Customer.objects.filter(phone=phone, status='Requested').first()
        if requested_customer:
            messages.warning(request, '⏳ درخواست شما قبلاً ثبت شده و در حال بررسی توسط مدیریت است. به محض تایید با شما تماس خواهیم گرفت.')
            return redirect('accounts:customer_sms_login')
    if request.method == 'POST':
        # ثبت درخواست مشتری جدید با شماره موبایل
        from core.models import Customer
        if phone:
            # بررسی وجود مشتری با وضعیت Requested
            if Customer.objects.filter(phone=phone, status='Requested').exists():
                messages.warning(request, '⏳ درخواست شما قبلاً ثبت شده و در حال بررسی توسط مدیریت است. به محض تایید با شما تماس خواهیم گرفت.')
                return redirect('accounts:customer_sms_login')
            
            # بررسی وجود مشتری با وضعیت‌های دیگر
            existing_customer = Customer.objects.filter(phone=phone).exclude(status='Requested').first()
            if existing_customer:
                messages.error(request, '❌ مشتری با این شماره تلفن قبلاً در سیستم ثبت شده است.')
                return redirect('accounts:customer_sms_login')
            
            # ایجاد درخواست جدید
            Customer.objects.create(
                customer_name=f'درخواست جدید ({phone})',
                phone=phone,
                status='Requested',
                comments='🟢 درخواست ثبت‌نام جدید از طریق فرم شرایط استفاده'
            )
            messages.success(request, '✅ درخواست شما با موفقیت ثبت شد و پس از تایید مدیریت، ثبت‌نام تکمیل خواهد شد.')
            return redirect('accounts:customer_sms_login')
        else:
            messages.error(request, 'شماره موبایل معتبر نیست.')
    return render(request, 'accounts/terms_and_request.html', {'phone': phone})


def customer_sms_login_view(request):
    """
    📱 ورود مشتری با SMS - مرحله اول: ارسال شماره تلفن
    🔐 سیستم احراز هویت بر اساس شماره موبایل و کد تایید
    """
    print("\n" + "="*60)
    print("🚨 DEBUG: customer_sms_login_view called")
    print(f"🚨 DEBUG: Method: {request.method}")
    print(f"🚨 DEBUG: URL: {request.path}")
    print("="*60)
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        print(f"🚨 DEBUG: Phone from POST: '{phone}'")
        
        # اعتبارسنجی شماره تلفن
        if not phone:
            print("❌ DEBUG: No phone provided")
            messages.error(request, '📱 لطفاً شماره تلفن خود را وارد کنید')
            return render(request, 'accounts/customer_sms_login.html')
        
        # بررسی فرمت شماره تلفن ایرانی
        if not phone.startswith('09') or len(phone) != 11:
            print(f"❌ DEBUG: Invalid phone format: {phone}")
            messages.error(request, '📱 شماره تلفن باید با 09 شروع شده و 11 رقم باشد')
            return render(request, 'accounts/customer_sms_login.html')
        
        print(f"✅ DEBUG: Phone format is valid: {phone}")
        
        try:
            # جستجوی کاربر بر اساس شماره تلفن
            print(f"🔍 DEBUG: Searching for user with phone: {phone}")
            print(f"🔍 DEBUG: UserRole.CUSTOMER = {User.UserRole.CUSTOMER}")
            
            # Test the query step by step
            user_exists = User.objects.filter(phone=phone).exists()
            print(f"🔍 DEBUG: User with phone exists: {user_exists}")
            
            if user_exists:
                user = User.objects.get(phone=phone)
                print(f"🔍 DEBUG: Found user: {user.username}, role: {user.role}")
            
            user = User.objects.get(phone=phone, role=User.UserRole.CUSTOMER)
            print(f"✅ DEBUG: User found: {user.username}")
            
            # بررسی وضعیت کاربر
            if user.status == User.UserStatus.SUSPENDED:
                messages.error(request, '🚫 حساب کاربری شما معلق شده است. لطفاً با پشتیبانی تماس بگیرید.')
                return render(request, 'accounts/customer_sms_login.html')
            if not user.is_active_user():
                print("❌ DEBUG: User is not active")
                messages.error(request, '❌ حساب کاربری شما غیرفعال است. لطفاً با پشتیبانی تماس بگیرید')
                return render(request, 'accounts/customer_sms_login.html')
            
            print("✅ DEBUG: User is active, proceeding with SMS")
            
            # تولید کد تایید تصادفی
            verification_code = ''.join(random.choices(string.digits, k=6))
            
            # ذخیره کد تایید در session
            request.session['sms_verification'] = {
                'phone': phone,
                'code': verification_code,
                'user_id': user.id,
                'created_at': timezone.now().isoformat(),
                'attempts': 0
            }
            
            # 🚀 ارسال SMS (فعلاً fake برای تست)
            # TODO: اتصال به API واقعی SMS
            fake_send_sms(phone, verification_code)
            
            # ثبت لاگ ارسال کد تایید
            ActivityLog.log_activity(
                user=user,
                action='INFO',
                description=f'کد تایید SMS برای شماره {phone} ارسال شد',
                severity='LOW',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                phone=phone,
                verification_code_sent=True
            )
            
            messages.success(request, f'📱 کد تایید به شماره {phone} ارسال شد')
            return redirect('accounts:customer_sms_verify')
            
        except User.DoesNotExist:
            # بررسی وجود مشتری با وضعیت Requested
            from core.models import Customer
            requested_customer = Customer.objects.filter(phone=phone, status='Requested').first()
            
            if requested_customer:
                # اگر مشتری با وضعیت Requested وجود دارد، پیام مناسب نمایش دهید
                messages.warning(request, '⏳ صبور باشید، درخواست شما در حال بررسی توسط مدیریت است. به محض تایید با شما تماس خواهیم گرفت.')
                return render(request, 'accounts/customer_sms_login.html')
            else:
                # به جای پیام خطا، هدایت به صفحه شرایط استفاده
                request.session['registration_phone'] = phone
                return redirect(f"{reverse('accounts:terms_and_request')}?phone={phone}")
        
        except Exception as e:
            print(f"❌ DEBUG: Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, '❌ خطا در ارسال کد تایید. لطفاً مجدداً تلاش کنید')
            return render(request, 'accounts/customer_sms_login.html')
    
    print("🔍 DEBUG: Rendering SMS login form")
    return render(request, 'accounts/customer_sms_login.html')


def customer_sms_verify_view(request):
    """
    🔐 ورود مشتری با SMS - مرحله دوم: تایید کد
    ✅ بررسی کد تایید و ورود کاربر به سیستم
    """
    # بررسی وجود اطلاعات تایید در session
    sms_data = request.session.get('sms_verification')
    if not sms_data:
        messages.error(request, '⏰ جلسه منقضی شده است. لطفاً مجدداً وارد شوید')
        return redirect('accounts:customer_sms_login')
    
    # بررسی انقضای کد (5 دقیقه)
    created_at = timezone.datetime.fromisoformat(sms_data['created_at'])
    if timezone.now() - created_at > timedelta(minutes=5):
        request.session.pop('sms_verification', None)
        messages.error(request, '⏰ کد تایید منقضی شده است. لطفاً مجدداً درخواست کنید')
        return redirect('accounts:customer_sms_login')
    
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code', '').strip()
        
        if not entered_code:
            messages.error(request, '🔢 لطفاً کد تایید را وارد کنید')
            return render(request, 'accounts/customer_sms_verify.html', {
                'phone': sms_data['phone']
            })
        
        # بررسی تعداد تلاش‌ها
        if sms_data.get('attempts', 0) >= 3:
            request.session.pop('sms_verification', None)
            messages.error(request, '🚫 تعداد تلاش‌های مجاز تمام شد. لطفاً مجدداً درخواست کنید')
            return redirect('accounts:customer_sms_login')
        
        # بررسی صحت کد
        if entered_code == sms_data['code']:
            try:
                # دریافت کاربر و ورود
                user = User.objects.get(id=sms_data['user_id'])
                login(request, user)
                
                # پاک کردن اطلاعات تایید از session
                request.session.pop('sms_verification', None)
                
                # ثبت لاگ ورود موفق
                ActivityLog.log_activity(
                    user=user,
                    action='LOGIN',
                    description=f'ورود موفق مشتری با SMS - شماره: {sms_data["phone"]}',
                    severity='MEDIUM',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    login_method='SMS',
                    phone=sms_data['phone']
                )
                
                messages.success(request, f'🎉 خوش آمدید {user.get_full_name()}!')
                
                # بررسی next parameter برای redirect
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                
                return redirect('accounts:customer_dashboard')
                
            except User.DoesNotExist:
                request.session.pop('sms_verification', None)
                messages.error(request, '❌ خطا در ورود. لطفاً مجدداً تلاش کنید')
                return redirect('accounts:customer_sms_login')
        
        else:
            # افزایش تعداد تلاش‌های ناموفق
            sms_data['attempts'] = sms_data.get('attempts', 0) + 1
            request.session['sms_verification'] = sms_data
            
            remaining_attempts = 3 - sms_data['attempts']
            if remaining_attempts > 0:
                messages.error(request, f'❌ کد تایید اشتباه است. {remaining_attempts} تلاش باقی مانده')
            else:
                request.session.pop('sms_verification', None)
                messages.error(request, '🚫 تعداد تلاش‌های مجاز تمام شد. لطفاً مجدداً درخواست کنید')
                return redirect('accounts:customer_sms_login')
    
    return render(request, 'accounts/customer_sms_verify.html', {
        'phone': sms_data['phone'],
        'remaining_time': 300 - int((timezone.now() - timezone.datetime.fromisoformat(sms_data['created_at'])).total_seconds())
    })


def resend_sms_code_view(request):
    """
    🔄 ارسال مجدد کد تایید SMS
    📱 برای مواردی که کاربر کد را دریافت نکرده است
    """
    sms_data = request.session.get('sms_verification')
    if not sms_data:
        messages.error(request, '⏰ جلسه منقضی شده است. لطفاً مجدداً وارد شوید')
        return redirect('accounts:customer_sms_login')
    
    try:
        user = User.objects.get(id=sms_data['user_id'])
        
        # تولید کد جدید
        new_verification_code = ''.join(random.choices(string.digits, k=6))
        
        # بروزرسانی session
        sms_data.update({
            'code': new_verification_code,
            'created_at': timezone.now().isoformat(),
            'attempts': 0
        })
        request.session['sms_verification'] = sms_data
        
        # ارسال SMS جدید
        fake_send_sms(sms_data['phone'], new_verification_code)
        
        # ثبت لاگ
        ActivityLog.log_activity(
            user=user,
            action='INFO',
            description=f'ارسال مجدد کد تایید SMS برای شماره {sms_data["phone"]}',
            severity='LOW',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            phone=sms_data['phone'],
            resend_code=True
        )
        
        messages.success(request, '📱 کد تایید جدید ارسال شد')
        
    except User.DoesNotExist:
        request.session.pop('sms_verification', None)
        messages.error(request, '❌ خطا در ارسال مجدد. لطفاً از ابتدا شروع کنید')
        return redirect('accounts:customer_sms_login')
    
    return redirect('accounts:customer_sms_verify')


def fake_send_sms(phone, code):
    """
    📱 ارسال SMS فیک برای تست
    🚀 TODO: جایگزینی با API واقعی SMS
    """
    print("\n" + "="*60)
    print("📱 SMS VERIFICATION CODE (FAKE FOR TESTING)")
    print("="*60)
    print(f"📞 Phone: {phone}")
    print(f"🔢 Code: {code}")
    print(f"⏰ Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("💡 This is a FAKE SMS for testing purposes.")
    print("🔧 Replace with real SMS API when ready.")
    print("="*60 + "\n")
    
    # TODO: Real SMS implementation
    # Example:
    # import requests
    # response = requests.post('https://api.sms-provider.com/send', {
    #     'phone': phone,
    #     'message': f'کد تایید شما: {code}',
    #     'api_key': settings.SMS_API_KEY
    # })
    # return response.json()


def get_client_ip(request):
    """
    🌐 دریافت IP واقعی کاربر
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
@super_admin_permission_required('accounts.manage_all_users')
def register_requested_customer_view(request):
    """
    👑 ثبت‌نام مشتری درخواستی توسط Super Admin
    🔄 به‌روزرسانی مشتری موجود با وضعیت Requested به Active
    """
    if request.method == 'POST':
        print(f"[DEBUG] Starting register_requested_customer POST for phone: {request.POST.get('phone', '')}")
        
        # دریافت اطلاعات فرم
        phone = request.POST.get('phone', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        economic_code = request.POST.get('economic_code', '').strip()
        national_id = request.POST.get('national_id', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        
        print(f"[DEBUG] Form data - Phone: {phone}, Name: {first_name} {last_name}")
        
        # اعتبارسنجی فیلدهای اجباری
        errors = []
        if not phone:
            errors.append('📱 شماره تلفن الزامی است')
        elif not phone.startswith('09') or len(phone) != 11:
            errors.append('📱 شماره تلفن باید با 09 شروع شده و 11 رقم باشد')
        
        if not first_name:
            errors.append('👤 نام الزامی است')
        
        if not last_name:
            errors.append('👤 نام خانوادگی الزامی است')
        
        print(f"[DEBUG] Validation errors: {errors}")
        
        # بررسی وجود مشتری درخواستی
        requested_customer = Customer.objects.filter(phone=phone, status='Requested').first()
        print(f"[DEBUG] Requested customer found: {requested_customer is not None}")
        if not requested_customer:
            errors.append('❌ مشتری درخواستی با این شماره تلفن یافت نشد')
        
        # بررسی وجود مشتریان دیگر با این شماره تلفن
        other_customers = Customer.objects.filter(phone=phone).exclude(status='Requested')
        print(f"[DEBUG] Other customers with same phone: {other_customers.count()}")
        if other_customers.exists():
            print(f"[DEBUG] Found {other_customers.count()} other customers with phone {phone}:")
            for cust in other_customers:
                print(f"[DEBUG] - Customer ID: {cust.id}, Name: {cust.customer_name}, Status: {cust.status}")
            errors.append('❌ مشتری دیگری با این شماره تلفن وجود دارد')
        
        # بررسی وجود کاربر با این شماره تلفن
        existing_user = User.objects.filter(phone=phone).first()
        print(f"[DEBUG] Existing user found: {existing_user is not None}")
        if existing_user:
            print(f"[DEBUG] Found existing user with phone {phone}: ID={existing_user.id}, Username={existing_user.username}, Status={existing_user.status}")
        
        if errors:
            print(f"[DEBUG] Validation failed, returning with errors: {errors}")
            for error in errors:
                messages.error(request, error)
            return redirect('core:customers_list')
        
        print(f"[DEBUG] Starting transaction...")
        try:
            with transaction.atomic():
                # بررسی وجود کاربر با این شماره تلفن
                existing_user = User.objects.filter(phone=phone).first()
                
                if existing_user:
                    # اگر کاربر وجود دارد، آن را به‌روزرسانی کن
                    print(f"[DEBUG] Updating existing user ID {existing_user.id}")
                    existing_user.first_name = first_name
                    existing_user.last_name = last_name
                    existing_user.email = email
                    existing_user.status = User.UserStatus.ACTIVE
                    existing_user.is_active = True
                    existing_user.save()
                    print(f"[DEBUG] Existing user updated successfully")
                    user = existing_user
                else:
                    # تولید نام کاربری منحصر به فرد
                    print(f"[DEBUG] Creating new user")
                    base_username = f"{first_name}_{last_name}".lower().replace(' ', '_')
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}_{counter}"
                        counter += 1
                    
                    print(f"[DEBUG] Creating user with username: {username}, phone: {phone}")
                    
                    # ایجاد کاربر جدید
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=None,  # کاربران Customer رمز عبور ندارند
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        role=User.UserRole.CUSTOMER,
                        status=User.UserStatus.ACTIVE,  # فعال
                        is_active=True,  # فعال
                        date_joined=timezone.now()
                    )
                    print(f"[DEBUG] New user created successfully with ID: {user.id}")
                
                # به‌روزرسانی مشتری درخواستی
                print(f"[DEBUG] Updating customer ID {requested_customer.id} with phone {phone}")
                requested_customer.customer_name = f"{first_name} {last_name}"
                requested_customer.address = address
                requested_customer.economic_code = economic_code
                requested_customer.national_id = national_id
                requested_customer.postcode = postcode
                requested_customer.status = 'Active'  # فعال کردن
                requested_customer.comments = f'✅ تایید شده توسط Super Admin\n📅 تاریخ تایید: {timezone.now().strftime("%Y/%m/%d %H:%M")}\n👑 تایید کننده: {request.user.username}'
                print(f"[DEBUG] About to save customer with phone {phone}")
                requested_customer.save()
                print(f"[DEBUG] Customer saved successfully")
                
                # ثبت لاگ تایید مشتری
                ActivityLog.log_activity(
                    user=request.user,
                    action='APPROVE',
                    description=f'✅ تایید و فعال‌سازی مشتری درخواستی: {requested_customer.customer_name} ({phone})',
                    content_object=requested_customer,
                    severity='MEDIUM',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    status_change={
                        'user_status': 'active',
                        'customer_status': 'Active',
                        'activated_by': request.user.username,
                        'previous_status': 'Requested'
                    }
                )
                
                messages.success(request, 
                    f'✅ مشتری "{requested_customer.customer_name}" با موفقیت تایید و فعال شد! 📞 شماره: {phone}'
                )
                return redirect('core:customers_list')
                
        except IntegrityError as e:
            print(f"[DEBUG] IntegrityError in register_requested_customer: {e}")
            messages.error(request, '❌ خطا در ثبت‌نام. احتمالاً شماره تلفن یا ایمیل تکراری است.')
            return redirect('core:customers_list')
        except Exception as e:
            print(f"❌ Error in register_requested_customer: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'❌ خطا در ثبت‌نام: {str(e)}')
            return redirect('core:customers_list')
    
    # GET request - نمایش فرم ثبت‌نام
    phone = request.GET.get('phone', '')
    return render(request, 'accounts/register_requested_customer.html', {
        'phone': phone,
        'form_data': {},
    })
