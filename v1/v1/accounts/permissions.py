"""
🔐 سیستم مجوزها و کنترل دسترسی - HomayOMS
🎯 دکوریتورها و میکسین‌های کنترل دسترسی بر اساس نقش کاربران
⚡ استفاده آسان در ویوها و APIها برای محدود کردن دسترسی
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import User


def check_user_permission(permission_type):
    """
    🔍 دکوریتور کنترل دسترسی بر اساس متد‌های User model
    
    👑 Super Admin همیشه دسترسی دارد
    
    🔧 استفاده:
        @check_user_permission('is_admin')
        def admin_view(request):
            # فقط adminها می‌توانند دسترسی داشته باشند
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # 👑 Super Admin همیشه دسترسی دارد
            if request.user.is_super_admin():
                return view_func(request, *args, **kwargs)
            
            # بررسی متد مورد نظر در user
            if hasattr(request.user, permission_type):
                check_method = getattr(request.user, permission_type)
                if callable(check_method) and check_method():
                    return view_func(request, *args, **kwargs)
            
            return render(request, 'accounts/permission_denied.html', {
                'message': f'🚫 شما دسترسی لازم برای این عملیات را ندارید'
            }, status=403)
        return wrapped_view
    return decorator


def role_required(*allowed_roles):
    """
    🎭 دکوریتور کنترل دسترسی بر اساس نقش کاربر
    
    🔧 استفاده:
        @role_required('super_admin', 'admin')
        def my_view(request):
            # این ویو فقط برای Super Admin و Admin قابل دسترسی است
            pass
    
    Args:
        allowed_roles: لیست نقش‌های مجاز ('super_admin', 'admin', 'finance')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # 🔍 بررسی احراز هویت کاربر
            if not request.user.is_authenticated:
                raise PermissionDenied("🔐 برای دسترسی به این صفحه باید وارد شوید")
            
            # 👑 Super Admin همیشه دسترسی دارد
            if request.user.is_super_admin():
                return view_func(request, *args, **kwargs)
            
            # 🎭 بررسی نقش کاربر
            if request.user.role not in allowed_roles:
                return render(request, 'accounts/permission_denied.html', {
                    'required_roles': allowed_roles,
                    'user_role': request.user.role,
                    'message': f'🚫 دسترسی محدود: این صفحه فقط برای {", ".join(str(role) for role in allowed_roles)} در دسترس است'
                }, status=403)
            
            # ✅ بررسی فعال بودن کاربر
            if not request.user.is_active_user():
                return render(request, 'accounts/account_inactive.html', {
                    'message': '❌ حساب کاربری شما غیرفعال است'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def super_admin_required(view_func):
    """
    🔴 دکوریتور دسترسی فقط برای Super Admin
    
    🔧 استفاده:
        @super_admin_required
        def sensitive_view(request):
            # فقط Super Admin می‌تواند این ویو را ببیند
            pass
    """
    return role_required(User.UserRole.SUPER_ADMIN)(view_func)


def admin_required(view_func):
    """
    🟡 دکوریتور دسترسی برای Admin و بالاتر
    
    🔧 استفاده:
        @admin_required
        def management_view(request):
            # Super Admin و Admin می‌توانند این ویو را ببینند
            pass
    """
    return role_required(User.UserRole.SUPER_ADMIN, User.UserRole.ADMIN)(view_func)


def finance_required(view_func):
    """
    🟢 دکوریتور دسترسی برای Finance و بالاتر
    
    🔧 استفاده:
        @finance_required
        def financial_view(request):
            # Super Admin و Finance می‌توانند این ویو را ببینند
            pass
    """
    return role_required(User.UserRole.SUPER_ADMIN, User.UserRole.FINANCE)(view_func)


def permission_required_custom(permission_codename):
    """
    🔐 دکوریتور کنترل دسترسی بر اساس مجوز خاص
    
    👑 Super Admin همیشه دسترسی دارد
    
    🔧 استفاده:
        @permission_required_custom('manage_customers')
        def customer_management(request):
            # فقط کاربرانی که مجوز manage_customers دارند
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # 👑 Super Admin همیشه دسترسی دارد
            if request.user.is_super_admin():
                return view_func(request, *args, **kwargs)
            
            if not request.user.has_perm(f'accounts.{permission_codename}'):
                return render(request, 'accounts/permission_denied.html', {
                    'required_permission': permission_codename,
                    'message': f'🚫 شما مجوز {permission_codename} ندارید'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


class RoleRequiredMixin(LoginRequiredMixin):
    """
    🎭 میکسین کنترل دسترسی بر اساس نقش برای کلاس‌های ویو
    
    🔧 استفاده:
        class MyView(RoleRequiredMixin, ListView):
            allowed_roles = ['super_admin', 'admin']
            model = SomeModel
    """
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        """
        🔍 بررسی دسترسی قبل از اجرای ویو
        """
        # 🔐 بررسی احراز هویت
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 👑 Super Admin همیشه دسترسی دارد
        if request.user.is_super_admin():
            return super().dispatch(request, *args, **kwargs)
        
        # 🎭 بررسی نقش کاربر
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            return render(request, 'accounts/permission_denied.html', {
                'required_roles': self.allowed_roles,
                'user_role': request.user.role,
                'message': f'🚫 دسترسی محدود: این صفحه فقط برای {", ".join(self.allowed_roles)} در دسترس است'
            }, status=403)
        
        # ✅ بررسی فعال بودن کاربر
        if not request.user.is_active_user():
            return render(request, 'accounts/account_inactive.html', {
                'message': '❌ حساب کاربری شما غیرفعال است'
            }, status=403)
        
        return super().dispatch(request, *args, **kwargs)


class SuperAdminRequiredMixin(RoleRequiredMixin):
    """
    🔴 میکسین دسترسی فقط برای Super Admin
    """
    allowed_roles = [User.UserRole.SUPER_ADMIN]


class AdminRequiredMixin(RoleRequiredMixin):
    """
    🟡 میکسین دسترسی برای Admin و بالاتر
    """
    allowed_roles = [User.UserRole.SUPER_ADMIN, User.UserRole.ADMIN]


class FinanceRequiredMixin(RoleRequiredMixin):
    """
    🟢 میکسین دسترسی برای Finance و بالاتر
    """
    allowed_roles = [User.UserRole.SUPER_ADMIN, User.UserRole.FINANCE]


class PermissionRequiredMixin(LoginRequiredMixin):
    """
    🔐 میکسین کنترل دسترسی بر اساس مجوز خاص
    
    🔧 استفاده:
        class MyView(PermissionRequiredMixin, ListView):
            permission_required = 'accounts.manage_customers'
            model = Customer
    """
    permission_required = None
    
    def dispatch(self, request, *args, **kwargs):
        """
        🔍 بررسی مجوز قبل از اجرای ویو
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 👑 Super Admin همیشه دسترسی دارد
        if request.user.is_super_admin():
            return super().dispatch(request, *args, **kwargs)
        
        if self.permission_required and not request.user.has_perm(self.permission_required):
            return render(request, 'accounts/permission_denied.html', {
                'required_permission': self.permission_required,
                'message': f'🚫 شما مجوز {self.permission_required} ندارید'
            }, status=403)
        
        return super().dispatch(request, *args, **kwargs)


# 🛠️ توابع کمکی برای بررسی دسترسی در تمپلیت‌ها

def user_can_manage_users(user):
    """
    👥 بررسی اجازه مدیریت کاربران
    """
    return user.is_authenticated and user.can_manage_users()


def user_can_access_financial_data(user):
    """
    💰 بررسی دسترسی به داده‌های مالی
    """
    return user.is_authenticated and user.can_access_financial_data()


def user_can_manage_inventory(user):
    """
    📦 بررسی اجازه مدیریت موجودی
    """
    return user.is_authenticated and user.can_manage_inventory()


def get_user_role_color(user):
    """
    🎨 دریافت رنگ مناسب برای نقش کاربر
    """
    colors = {
        User.UserRole.SUPER_ADMIN: '#dc3545',  # قرمز
        User.UserRole.ADMIN: '#ffc107',        # زرد  
        User.UserRole.FINANCE: '#28a745'       # سبز
    }
    return colors.get(user.role, '#6c757d')


# 🎯 Context processor برای دسترسی آسان در تمپلیت‌ها
def user_permissions_context(request):
    """
    📋 اضافه کردن اطلاعات دسترسی کاربر به context تمپلیت‌ها
    
    استفاده در تمپلیت:
    {% if user_permissions.can_manage_users %}
        <a href="/admin/users/">👥 مدیریت کاربران</a>
    {% endif %}
    """
    if not request.user.is_authenticated:
        return {}
    
    return {
        'user_permissions': {
            'can_manage_users': user_can_manage_users(request.user),
            'can_access_financial_data': user_can_access_financial_data(request.user),
            'can_manage_inventory': user_can_manage_inventory(request.user),
            'role_color': get_user_role_color(request.user),
            'accessible_features': request.user.get_accessible_features(),
            'role_display': request.user.get_role_display(),
            'is_super_admin': request.user.is_super_admin(),
            'is_admin': request.user.is_admin(),
            'is_finance': request.user.is_finance(),
        }
    }


def super_admin_permission_required(permission_codename):
    """
    🔐 دکوریتور کنترل دسترسی که Super Admin را همیشه راه می‌دهد
    
    👑 Super Admin همیشه دسترسی دارد
    
    🔧 استفاده:
        @super_admin_permission_required('accounts.manage_customers')
        def customer_management(request):
            # Super Admin یا کاربرانی که مجوز دارند
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # 👑 Super Admin همیشه دسترسی دارد
            if request.user.is_super_admin():
                return view_func(request, *args, **kwargs)
            
            # بررسی مجوز برای سایر کاربران
            if not request.user.has_perm(permission_codename):
                return render(request, 'accounts/permission_denied.html', {
                    'required_permission': permission_codename,
                    'message': f'🚫 شما مجوز {permission_codename} ندارید'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator 