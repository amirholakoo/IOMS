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


def login_view(request):
    """🔐 صفحه ورود اصلی با 4 گزینه مختلف"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    return render(request, 'accounts/login.html')


def staff_login_view(request):
    """👥 ورود کارمندان (Super Admin, Admin, Finance)"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
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
            return redirect('accounts:dashboard')
        else:
            messages.error(request, '❌ نام کاربری، رمز عبور یا نقش اشتباه است')
    
    return render(request, 'accounts/staff_login.html')


def customer_login_view(request):
    """🔵 ورود مشتریان - هدایت به صفحه SMS"""
    if request.user.is_authenticated:
        if request.user.is_customer():
            return redirect('accounts:customer_dashboard')
        else:
            return redirect('accounts:dashboard')
    
    # مستقیماً به صفحه SMS login هدایت می‌کنیم
    return redirect('accounts:customer_sms_login')


def customer_registration_view(request):
    """
    📝 ثبت‌نام مشتری جدید
    """
    phone = request.POST.get('phone', '').strip() if request.method == 'POST' else request.GET.get('phone', '').strip()
    disable_form = False
    form_data = request.POST if request.method == 'POST' else {}

    # جلوگیری قطعی از حلقه: اگر هر کاربری با این شماره وجود داشت، فرم غیرفعال و پیام مناسب نمایش داده شود
    if phone:
        from .models import User
        existing_user = User.objects.filter(phone=phone, role=User.UserRole.CUSTOMER).first()
        if existing_user:
            if existing_user.status == User.UserStatus.PENDING:
                messages.warning(request, 'درخواست ثبت‌نام شما قبلاً ثبت شده و در انتظار تایید مدیریت است. لطفاً صبور باشید، به زودی توسط مدیر بررسی خواهد شد.')
            else:
                messages.error(request, 'این شماره قبلاً ثبت شده است و امکان ثبت‌نام مجدد وجود ندارد.')
            disable_form = True
            return render(request, 'accounts/customer_registration.html', {
                'form_data': form_data,
                'phone': phone,
                'disable_form': disable_form
            })
    if request.method == 'POST' and not disable_form:
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        economic_code = request.POST.get('economic_code', '').strip()
        national_id = request.POST.get('national_id', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        errors = []
        if not phone:
            errors.append('📱 شماره تلفن الزامی است')
        elif not phone.startswith('09') or len(phone) != 11:
            errors.append('📱 شماره تلفن باید با 09 شروع شده و 11 رقم باشد')
        if not first_name:
            errors.append('👤 نام الزامی است')
        if not last_name:
            errors.append('👤 نام خانوادگی الزامی است')
        if Customer.objects.filter(phone=phone).exclude(status='Requested').exists():
            errors.append('👤 مشتری با این شماره قبلاً ثبت شده است و فعال است')
        if email and User.objects.filter(email=email).exists():
            errors.append('📧 این ایمیل قبلاً ثبت شده است')
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/customer_registration.html', {
                'form_data': request.POST,
                'phone': phone,
                'disable_form': False
            })
        try:
            customer = Customer.objects.filter(phone=phone, status='Requested').first()
            if customer:
                customer.customer_name = f"{first_name} {last_name}"
                customer.address = address
                customer.economic_code = economic_code
                customer.national_id = national_id
                customer.postcode = postcode
                customer.status = 'Active'
                customer.comments = 'ثبت‌نام تکمیل شد و فعال گردید.'
                customer.save()
            else:
                base_customer_name = f"{first_name} {last_name}"
                customer_name = base_customer_name
                counter = 1
                while Customer.objects.filter(customer_name=customer_name).exists():
                    customer_name = f"{base_customer_name} ({counter})"
                    counter += 1
                customer = Customer.objects.create(
                    customer_name=customer_name,
                    phone=phone,
                    address=address,
                    economic_code=economic_code,
                    national_id=national_id,
                    postcode=postcode,
                    status='Active',
                    comments='ثبت‌نام جدید و فعال'
                )
            base_username = f"{first_name}_{last_name}".lower().replace(' ', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=User.UserRole.CUSTOMER,
                status=User.UserStatus.ACTIVE,
                is_active=True,
                date_joined=timezone.now()
            )
            ActivityLog.log_activity(
                user=None,
                action='CREATE',
                description=f'📝 ثبت‌نام جدید مشتری: {first_name} {last_name} - {phone}',
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
            if request.user.is_authenticated and request.user.is_superuser:
                messages.success(request, '✅ مشتری جدید با موفقیت ثبت شد و فعال است.')
                request.session['show_success'] = True
                return redirect('core:customers_list')
            else:
                messages.success(request, '✅ ثبت‌نام شما با موفقیت انجام شد. منتظر تایید مدیریت باشید.')
                return redirect('accounts:customer_sms_login')
        except Exception as e:
            messages.error(request, f'❌ خطا در ثبت‌نام: {str(e)}')
            return render(request, 'accounts/customer_registration.html', {
                'form_data': request.POST,
                'phone': phone,
                'disable_form': False
            })
    # حالت GET یا فرم غیرفعال
    return render(request, 'accounts/customer_registration.html', {
        'form_data': form_data,
        'phone': phone,
        'disable_form': disable_form
    })


@login_required
def customer_dashboard_view(request):
    """🔵 داشبورد مخصوص مشتریان"""
    if not request.user.is_customer():
        messages.error(request, '❌ شما دسترسی به این بخش را ندارید')
        return redirect('accounts:dashboard')
    
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
    """👤 نمایش پروفایل کاربر"""
    return render(request, 'accounts/profile.html')


@login_required
def change_password_view(request):
    """🔐 تغییر رمز عبور"""
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
    if request.method == 'POST':
        # ثبت درخواست مشتری جدید با شماره موبایل
        from core.models import Customer
        if phone:
            # اگر قبلاً درخواست داده نشده باشد
            if not Customer.objects.filter(phone=phone, status='Requested').exists():
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

    # منطق جلوگیری از حلقه ثبت‌نام برای شماره‌هایی با وضعیت pending
    phone = request.POST.get('phone', '').strip() if request.method == 'POST' else request.GET.get('phone', '').strip()
    if phone:
        from .models import User
        pending_user = User.objects.filter(phone=phone, status=User.UserStatus.PENDING, role=User.UserRole.CUSTOMER).first()
        if pending_user:
            # فقط پیام نمایش داده شود و فرم غیرفعال باشد
            messages.warning(request, 'درخواست شما در حال بررسی است. لطفاً منتظر تأیید بمانید.')
            return render(request, 'accounts/customer_sms_login.html', {'phone': phone, 'disable_form': True})

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
            
            # بررسی فعال بودن کاربر
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
        del request.session['sms_verification']
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
            del request.session['sms_verification']
            messages.error(request, '🚫 تعداد تلاش‌های مجاز تمام شد. لطفاً مجدداً درخواست کنید')
            return redirect('accounts:customer_sms_login')
        
        # بررسی صحت کد
        if entered_code == sms_data['code']:
            try:
                # دریافت کاربر و ورود
                user = User.objects.get(id=sms_data['user_id'])
                login(request, user)
                
                # پاک کردن اطلاعات تایید از session
                del request.session['sms_verification']
                
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
                del request.session['sms_verification']
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
                del request.session['sms_verification']
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
        del request.session['sms_verification']
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
@super_admin_permission_required('manage_customers')
@require_http_methods(["GET", "POST"])
def edit_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == "POST":
        phone = request.POST.get('phone', customer.phone)
        # بررسی یکتایی شماره موبایل (غیر از مشتری فعلی و غیر از Requested)
        if Customer.objects.filter(phone=phone).exclude(id=customer.id).exclude(status='Requested').exists():
            messages.error(request, 'شماره موبایل تکراری است و قبلاً برای مشتری فعال ثبت شده است.')
            return redirect('core:edit_customer', customer_id=customer.id)
        customer.customer_name = request.POST.get('customer_name', customer.customer_name)
        customer.phone = phone
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
