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
    
    # شمارش مشتریان در انتظار تایید
    pending_customers_count = User.objects.filter(
        role=User.UserRole.CUSTOMER,
        status=User.UserStatus.PENDING
    ).count()
    
    # صفحه‌بندی
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,  # تغییر از page_obj به users برای سازگاری با template
        'page_obj': page_obj,
        'user_roles': User.UserRole.choices,
        'user_statuses': User.UserStatus.choices,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total_users': users.count(),
        'pending_customers_count': pending_customers_count,
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
            
            # بررسی فعال بودن کاربر
            if not user.is_active_user():
                print("❌ DEBUG: User is not active")
                if user.status == User.UserStatus.PENDING:
                    messages.error(request, '⏳ حساب کاربری شما در انتظار تایید است. لطفاً با پشتیبانی تماس بگیرید')
                else:
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
            print(f"❌ DEBUG: User.DoesNotExist for phone: {phone}")
            print("❌ DEBUG: This is where the error message comes from!")
            
            # بررسی اینکه آیا کاربر با این شماره وجود دارد اما نقش Customer نیست
            existing_user = User.objects.filter(phone=phone).first()
            if existing_user:
                messages.error(request, '❌ این شماره تلفن برای کاربر دیگری ثبت شده است. لطفاً با پشتیبانی تماس بگیرید')
            else:
                # کاربر جدید - نمایش پیام مناسب با لینک ثبت‌نام
                messages.error(request, '❌ شما عضو نیستید. لطفاً ابتدا ثبت‌نام کنید یا با پشتیبانی تماس بگیرید')
                # ذخیره شماره تلفن در session برای استفاده در صفحه ثبت‌نام
                request.session['registration_phone'] = phone
                return render(request, 'accounts/customer_sms_login.html', {
                    'show_signup_link': True,
                    'phone': phone
                })
            
            return render(request, 'accounts/customer_sms_login.html')
        
        except Exception as e:
            print(f"❌ DEBUG: Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, '❌ خطا در ارسال کد تایید. لطفاً مجدداً تلاش کنید')
            return render(request, 'accounts/customer_sms_login.html')
    
    print("🔍 DEBUG: Rendering SMS login form")
    return render(request, 'accounts/customer_sms_login.html')


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
        if User.objects.filter(phone=phone).exists():
            errors.append('📱 این شماره تلفن قبلاً ثبت شده است')
        
        # بررسی تکراری نبودن ایمیل (در صورت وارد کردن)
        if email and User.objects.filter(email=email).exists():
            errors.append('📧 این ایمیل قبلاً ثبت شده است')
        
        if errors:
            for error in errors:
                messages.error(request, error)
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
            
            # ایجاد نام منحصر به فرد برای مشتری
            base_customer_name = f"{first_name} {last_name}"
            customer_name = base_customer_name
            counter = 1
            
            # اگر نام تکراری است، شماره اضافه کن
            while Customer.objects.filter(customer_name=customer_name).exists():
                customer_name = f"{base_customer_name} ({counter})"
                counter += 1
            
            # ایجاد Customer object
            customer = Customer.objects.create(
                customer_name=customer_name,
                phone=phone,
                address=address,
                economic_code=economic_code,
                national_id=national_id,
                postcode=postcode,
                status='Inactive',  # غیرفعال تا تایید شود
                comments=f'🔵 ثبت‌نام جدید - در انتظار تایید Super Admin\n📅 تاریخ ثبت‌نام: {timezone.now().strftime("%Y/%m/%d %H:%M")}'
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
            
            # پاک کردن شماره تلفن از session
            if 'registration_phone' in request.session:
                del request.session['registration_phone']
            
            messages.success(request, 
                '✅ درخواست ثبت‌نام شما با موفقیت ارسال شد!\n'
                '⏳ پس از تایید توسط مدیریت، می‌توانید وارد شوید.\n'
                '📞 برای پیگیری با پشتیبانی تماس بگیرید.'
            )
            
            return redirect('accounts:customer_sms_login')
            
        except Exception as e:
            print(f"❌ Error in customer registration: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, '❌ خطا در ثبت‌نام. لطفاً مجدداً تلاش کنید')
            return render(request, 'accounts/customer_registration.html', {
                'form_data': request.POST
            })
    
    # GET request - نمایش فرم ثبت‌نام
    phone = request.session.get('registration_phone', '')
    return render(request, 'accounts/customer_registration.html', {
        'phone': phone,
        'form_data': {},
    })


def verify_customer_view(request, user_id):
    """
    ✅ تایید مشتری توسط Super Admin
    🔐 تغییر وضعیت کاربر از PENDING به ACTIVE
    """
    if not request.user.is_authenticated or not request.user.is_super_admin():
        messages.error(request, '❌ شما دسترسی به این بخش را ندارید')
        return redirect('accounts:dashboard')
    
    try:
        user = User.objects.get(id=user_id, role=User.UserRole.CUSTOMER)
        
        if user.status != User.UserStatus.PENDING:
            messages.error(request, '❌ این کاربر قبلاً تایید شده است')
            return redirect('accounts:user_list')
        
        # تغییر وضعیت کاربر
        user.status = User.UserStatus.ACTIVE
        user.is_active = True
        user.save()
        
        # تغییر وضعیت Customer object (جستجو بر اساس شماره تلفن)
        customer = Customer.objects.filter(phone=user.phone).first()
        
        if customer:
            customer.status = 'Active'
            customer.save()
        
        # ارسال SMS تایید (fake)
        fake_send_sms(user.phone, f"✅ حساب کاربری شما تایید شد. می‌توانید وارد شوید.")
        
        # ثبت لاگ تایید
        ActivityLog.log_activity(
            user=request.user,
            action='APPROVE',
            description=f'✅ مشتری تایید شد: {user.get_full_name()} - {user.phone}',
            content_object=user,
            severity='HIGH',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            approved_by=request.user.username,
            customer_phone=user.phone
        )
        
        messages.success(request, f'✅ مشتری {user.get_full_name()} با موفقیت تایید شد')
        
    except User.DoesNotExist:
        messages.error(request, '❌ کاربر مورد نظر یافت نشد')
    except Exception as e:
        print(f"❌ Error in customer verification: {e}")
        messages.error(request, '❌ خطا در تایید مشتری')
    
    return redirect('accounts:user_list')


def reject_customer_view(request, user_id):
    """
    ❌ رد درخواست مشتری توسط Super Admin
    🗑️ حذف کاربر و Customer object
    """
    if not request.user.is_authenticated or not request.user.is_super_admin():
        messages.error(request, '❌ شما دسترسی به این بخش را ندارید')
        return redirect('accounts:dashboard')
    
    try:
        user = User.objects.get(id=user_id, role=User.UserRole.CUSTOMER)
        
        if user.status != User.UserStatus.PENDING:
            messages.error(request, '❌ این کاربر قبلاً تایید شده است')
            return redirect('accounts:user_list')
        
        # حذف Customer object مرتبط (جستجو بر اساس شماره تلفن)
        customer = Customer.objects.filter(phone=user.phone).first()
        
        if customer:
            customer.delete()
        
        # ثبت لاگ رد درخواست
        ActivityLog.log_activity(
            user=request.user,
            action='REJECT',
            description=f'❌ درخواست مشتری رد شد: {user.get_full_name()} - {user.phone}',
            content_object=user,
            severity='HIGH',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            rejected_by=request.user.username,
            customer_phone=user.phone
        )
        
        # حذف کاربر
        user.delete()
        
        messages.success(request, f'❌ درخواست مشتری {user.get_full_name()} رد شد')
        
    except User.DoesNotExist:
        messages.error(request, '❌ کاربر مورد نظر یافت نشد')
    except Exception as e:
        print(f"❌ Error in customer rejection: {e}")
        messages.error(request, '❌ خطا در رد درخواست مشتری')
    
    return redirect('accounts:user_list')


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
@super_admin_permission_required('accounts.manage_all_users')
@require_http_methods(["POST"])
def delete_user_view(request, user_id):
    """🗑️ حذف کاربر (فقط Super Admin)"""
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # جلوگیری از حذف خود Super Admin
    if user_to_delete == request.user:
        messages.error(request, '❌ نمی‌توانید حساب کاربری خود را حذف کنید')
        return redirect('accounts:user_list')
    
    # جلوگیری از حذف آخرین Super Admin
    if user_to_delete.role == User.UserRole.SUPER_ADMIN:
        super_admin_count = User.objects.filter(role=User.UserRole.SUPER_ADMIN).count()
        if super_admin_count <= 1:
            messages.error(request, '❌ نمی‌توانید آخرین Super Admin را حذف کنید')
            return redirect('accounts:user_list')
    
    try:
        # حذف Customer مرتبط اگر وجود دارد
        if user_to_delete.role == User.UserRole.CUSTOMER:
            customer = Customer.objects.filter(
                customer_name=user_to_delete.get_full_name() or user_to_delete.username
            ).first()
            if customer:
                customer.delete()
        
        # حذف کاربر
        username = user_to_delete.username
        user_to_delete.delete()
        
        messages.success(request, f'✅ کاربر {username} با موفقیت حذف شد')
        
    except Exception as e:
        messages.error(request, f'❌ خطا در حذف کاربر: {str(e)}')
    
    return redirect('accounts:user_list')


@login_required
@super_admin_permission_required('accounts.manage_all_users')
def edit_user_view(request, user_id):
    """📝 ویرایش کاربر (فقط Super Admin)"""
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            # دریافت داده‌های فرم
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            role = request.POST.get('role', '').strip()
            status = request.POST.get('status', '').strip()
            department = request.POST.get('department', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            # اعتبارسنجی داده‌ها
            if not first_name:
                messages.error(request, '❌ نام الزامی است')
                return render(request, 'accounts/edit_user.html', {
                    'user_to_edit': user_to_edit,
                    'user_roles': User.UserRole.choices,
                    'user_statuses': User.UserStatus.choices,
                })
            
            if not phone:
                messages.error(request, '❌ شماره تلفن الزامی است')
                return render(request, 'accounts/edit_user.html', {
                    'user_to_edit': user_to_edit,
                    'user_roles': User.UserRole.choices,
                    'user_statuses': User.UserStatus.choices,
                })
            
            # بررسی یکتا بودن شماره تلفن
            if phone != user_to_edit.phone:
                if User.objects.filter(phone=phone).exists():
                    messages.error(request, '❌ این شماره تلفن قبلاً ثبت شده است')
                    return render(request, 'accounts/edit_user.html', {
                        'user_to_edit': user_to_edit,
                        'user_roles': User.UserRole.choices,
                        'user_statuses': User.UserStatus.choices,
                    })
            
            # بررسی یکتا بودن ایمیل
            if email and email != user_to_edit.email:
                if User.objects.filter(email=email).exists():
                    messages.error(request, '❌ این ایمیل قبلاً ثبت شده است')
                    return render(request, 'accounts/edit_user.html', {
                        'user_to_edit': user_to_edit,
                        'user_roles': User.UserRole.choices,
                        'user_statuses': User.UserStatus.choices,
                    })
            
            # اعتبارسنجی نقش
            if role not in [choice[0] for choice in User.UserRole.choices]:
                messages.error(request, '❌ نقش انتخاب شده نامعتبر است')
                return render(request, 'accounts/edit_user.html', {
                    'user_to_edit': user_to_edit,
                    'user_roles': User.UserRole.choices,
                    'user_statuses': User.UserStatus.choices,
                })
            
            # اعتبارسنجی وضعیت
            if status not in [choice[0] for choice in User.UserStatus.choices]:
                messages.error(request, '❌ وضعیت انتخاب شده نامعتبر است')
                return render(request, 'accounts/edit_user.html', {
                    'user_to_edit': user_to_edit,
                    'user_roles': User.UserRole.choices,
                    'user_statuses': User.UserStatus.choices,
                })
            
            # جلوگیری از تغییر نقش آخرین Super Admin
            if user_to_edit.role == User.UserRole.SUPER_ADMIN and role != User.UserRole.SUPER_ADMIN:
                super_admin_count = User.objects.filter(role=User.UserRole.SUPER_ADMIN).count()
                if super_admin_count <= 1:
                    messages.error(request, '❌ نمی‌توانید نقش آخرین Super Admin را تغییر دهید')
                    return render(request, 'accounts/edit_user.html', {
                        'user_to_edit': user_to_edit,
                        'user_roles': User.UserRole.choices,
                        'user_statuses': User.UserStatus.choices,
                    })
            
            # بروزرسانی اطلاعات کاربر
            user_to_edit.first_name = first_name
            user_to_edit.last_name = last_name
            user_to_edit.email = email
            user_to_edit.phone = phone
            user_to_edit.role = role
            user_to_edit.status = status
            user_to_edit.department = department
            user_to_edit.notes = notes
            
            user_to_edit.save()
            
            messages.success(request, f'✅ اطلاعات کاربر {user_to_edit.username} با موفقیت بروزرسانی شد')
            return redirect('accounts:user_list')
            
        except Exception as e:
            messages.error(request, f'❌ خطا در بروزرسانی اطلاعات: {str(e)}')
    
    context = {
        'user_to_edit': user_to_edit,
        'user_roles': User.UserRole.choices,
        'user_statuses': User.UserStatus.choices,
    }
def super_admin_or_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_super_admin() or request.user.is_admin()):
            messages.error(request, '❌ شما دسترسی به این بخش را ندارید')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@super_admin_or_admin_required
@require_http_methods(["GET", "POST"])
def create_user_view(request):
    """
    👤 ایجاد کاربر جدید توسط سوپرادمین یا ادمین
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', User.UserRole.CUSTOMER)
        status = request.POST.get('status', User.UserStatus.ACTIVE)

        errors = []
        if not username:
            errors.append('نام کاربری الزامی است')
        if not password:
            errors.append('رمز عبور الزامی است')
        if not phone:
            errors.append('شماره تلفن الزامی است')
        if User.objects.filter(username=username).exists():
            errors.append('نام کاربری تکراری است')
        if User.objects.filter(phone=phone).exists():
            errors.append('شماره تلفن تکراری است')
        if role not in [choice[0] for choice in User.UserRole.choices]:
            errors.append('نقش انتخاب شده نامعتبر است')
        if status not in [choice[0] for choice in User.UserStatus.choices]:
            errors.append('وضعیت انتخاب شده نامعتبر است')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/create_user.html', {'form_data': request.POST})

        user = User.objects.create(
            username=username,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            status=status,
            is_active=(status == User.UserStatus.ACTIVE)
        )
        messages.success(request, f'کاربر {username} با موفقیت ایجاد شد')
        return redirect('accounts:user_list')

    # GET: just show the form (template to be implemented)
    return render(request, 'accounts/create_user.html', {
        'user_roles': User.UserRole.choices,
        'user_statuses': User.UserStatus.choices,
        'form_data': {},
    })
