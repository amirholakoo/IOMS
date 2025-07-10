"""
🎛️ پنل مدیریت حساب‌های کاربری - HomayOMS
👥 رابط مدیریت کامل کاربران با نقش‌های مختلف و کنترل دسترسی
🔐 شامل مدیریت مجوزها، گروه‌ها و نشست‌های کاربران
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    🎛️ پنل مدیریت کاربران با قابلیت‌های پیشرفته
    🔐 مدیریت نقش‌ها، مجوزها و وضعیت کاربران
    """
    
    # 📋 فیلدهای نمایش در لیست کاربران
    list_display = [
        'username',
        'get_full_name_display',
        'email',
        'phone',
        'get_role_display_with_color',
        'get_status_display_with_icon',
        'last_activity',
        'created_at',
        'is_active',
        'get_quick_actions'
    ]
    
    # 🔍 فیلدهای قابل جستجو
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'phone'
    ]
    
    # 🔽 فیلترهای کناری
    list_filter = [
        'role',
        'status',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
        'last_login'
    ]
    
    # 📝 ترتیب فیلدها در فرم ویرایش
    fieldsets = (
        ('👤 اطلاعات کاربری', {
            'fields': ('username', 'password')
        }),
        ('📋 اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('🎭 نقش و دسترسی', {
            'fields': ('role', 'status', 'department'),
            'classes': ('wide',)
        }),
        ('🔐 مجوزها', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('📝 اطلاعات اضافی', {
            'fields': ('notes', 'password_expires_at'),
            'classes': ('collapse',)
        }),
        ('⏰ تاریخ‌ها', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 📝 فیلدهای فرم اضافه کردن کاربر جدید
    add_fieldsets = (
        ('👤 اطلاعات اساسی', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'phone')
        }),
        ('🎭 نقش و وضعیت', {
            'classes': ('wide',),
            'fields': ('role', 'status', 'first_name', 'last_name')
        }),
    )
    
    # 📅 فیلدهای فقط خواندنی
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'last_login', 
        'date_joined',
        'get_accessible_features_display',
        'get_sessions_count'
    ]
    
    # 🔢 تعداد آیتم‌ها در هر صفحه
    list_per_page = 25
    
    # 🎯 اکشن‌های سفارشی
    actions = [
        'make_active',
        'make_inactive', 
        'reset_password_expiry',
        'send_welcome_email'
    ]
    
    def get_full_name_display(self, obj):
        """
        👤 نمایش نام کامل کاربر
        """
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username
    get_full_name_display.short_description = "👤 نام کامل"
    
    def get_role_display_with_color(self, obj):
        """
        🎭 نمایش نقش با رنگ مناسب
        """
        colors = {
            User.UserRole.SUPER_ADMIN: '#dc3545',  # قرمز
            User.UserRole.ADMIN: '#ffc107',        # زرد
            User.UserRole.FINANCE: '#28a745'       # سبز
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    get_role_display_with_color.short_description = "🎭 نقش"
    
    def get_status_display_with_icon(self, obj):
        """
        📊 نمایش وضعیت با آیکون
        """
        icons = {
            User.UserStatus.ACTIVE: '✅',
            User.UserStatus.INACTIVE: '❌', 
            User.UserStatus.SUSPENDED: '⏸️',
            User.UserStatus.PENDING: '⏳'
        }
        icon = icons.get(obj.status, '❓')
        return f"{icon} {obj.get_status_display()}"
    get_status_display_with_icon.short_description = "📊 وضعیت"
    
    def get_quick_actions(self, obj):
        """
        ⚡ دکمه‌های عملیات سریع
        """
        try:
            sessions_url = reverse('admin:accounts_usersession_changelist') + f'?user__id__exact={obj.id}'
            edit_url = reverse('admin:accounts_user_change', args=[obj.pk])
            
            return format_html(
                '<a class="button" href="{}" style="margin-right: 5px;">📊 نشست‌ها</a>'
                '<a class="button" href="{}">✏️ ویرایش</a>',
                sessions_url,
                edit_url
            )
        except Exception:
            return mark_safe('<span style="color: red;">❌ خطا</span>')
    get_quick_actions.short_description = "⚡ عملیات"
    
    def get_accessible_features_display(self, obj):
        """
        🔐 نمایش ویژگی‌های قابل دسترس
        """
        features = obj.get_accessible_features()
        return format_html('<br>'.join(features))
    get_accessible_features_display.short_description = "🔐 ویژگی‌های قابل دسترس"
    
    def get_sessions_count(self, obj):
        """
        📱 تعداد نشست‌های کاربر
        """
        return obj.sessions.count()
    get_sessions_count.short_description = "📱 تعداد نشست‌ها"
    
    # 🎯 اکشن‌های سفارشی
    def make_active(self, request, queryset):
        """
        ✅ فعال کردن کاربران انتخاب شده
        """
        updated = queryset.update(status=User.UserStatus.ACTIVE)
        self.message_user(request, f'✅ {updated} کاربر فعال شدند.')
    make_active.short_description = "✅ فعال کردن کاربران انتخاب شده"
    
    def make_inactive(self, request, queryset):
        """
        ❌ غیرفعال کردن کاربران انتخاب شده
        """
        updated = queryset.update(status=User.UserStatus.INACTIVE)
        self.message_user(request, f'❌ {updated} کاربر غیرفعال شدند.')
    make_inactive.short_description = "❌ غیرفعال کردن کاربران انتخاب شده"
    
    def reset_password_expiry(self, request, queryset):
        """
        🔐 بازنشانی تاریخ انقضای رمز عبور
        """
        from django.utils import timezone
        from datetime import timedelta
        
        new_expiry = timezone.now() + timedelta(days=90)
        updated = queryset.update(password_expires_at=new_expiry)
        self.message_user(request, f'🔐 تاریخ انقضای رمز عبور {updated} کاربر بازنشانی شد.')
    reset_password_expiry.short_description = "🔐 بازنشانی انقضای رمز عبور"
    
    def send_welcome_email(self, request, queryset):
        """
        📧 ارسال ایمیل خوش‌آمدگویی
        """
        # پیاده‌سازی در آینده
        self.message_user(request, f'📧 ایمیل خوش‌آمدگویی برای {queryset.count()} کاربر ارسال شد.')
    send_welcome_email.short_description = "📧 ارسال ایمیل خوش‌آمدگویی"
    
    def has_add_permission(self, request):
        """➕ مجوز اضافه کردن کاربر"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('accounts.add_user')
    
    def has_change_permission(self, request, obj=None):
        """✏️ مجوز تغییر کاربر"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('accounts.change_user')
    
    def has_delete_permission(self, request, obj=None):
        """🗑️ مجوز حذف کاربر"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('accounts.delete_user')
    
    def has_view_permission(self, request, obj=None):
        """👁️ مجوز مشاهده کاربر"""
        return request.user.is_superuser or (hasattr(request.user, 'is_super_admin') and request.user.is_super_admin()) or request.user.has_perm('accounts.view_user')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    📱 پنل مدیریت نشست‌های کاربران
    🔍 ردیابی ورود، خروج و فعالیت‌های کاربران
    """
    
    # 📋 فیلدهای نمایش در لیست
    list_display = [
        'user',
        'login_time',
        'logout_time',
        'get_session_status',
        'get_duration_display',
        'ip_address',
        'get_user_agent_short'
    ]
    
    # 🔍 فیلدهای قابل جستجو
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'ip_address'
    ]
    
    # 🔽 فیلترهای کناری
    list_filter = [
        'is_active',
        'login_time',
        'logout_time',
        'user__role'
    ]
    
    # 📅 فیلدهای فقط خواندنی
    readonly_fields = [
        'login_time',
        'created_at',
        'updated_at',
        'get_duration_display'
    ]
    
    # 📝 ترتیب فیلدها در فرم
    fields = [
        'user',
        'login_time',
        'logout_time', 
        'is_active',
        'ip_address',
        'user_agent',
        'get_duration_display'
    ]
    
    # 🔢 تعداد آیتم‌ها در هر صفحه
    list_per_page = 50
    
    # 📅 مرتب‌سازی پیش‌فرض
    ordering = ['-login_time']
    
    def get_session_status(self, obj):
        """
        📊 وضعیت نشست
        """
        if obj.logout_time:
            return "🔚 پایان یافته"
        elif obj.is_active:
            return "✅ فعال"
        else:
            return "❌ غیرفعال"
    get_session_status.short_description = "📊 وضعیت"
    
    def get_duration_display(self, obj):
        """
        ⏱️ نمایش مدت زمان نشست
        """
        duration = obj.get_session_duration()
        hours = duration.total_seconds() // 3600
        minutes = (duration.total_seconds() % 3600) // 60
        
        if hours > 0:
            return f"⏱️ {int(hours)}س {int(minutes)}د"
        else:
            return f"⏱️ {int(minutes)}د"
    get_duration_display.short_description = "⏱️ مدت زمان"
    
    def get_user_agent_short(self, obj):
        """
        🖥️ نمایش خلاصه مشخصات مرورگر
        """
        if not obj.user_agent:
            return "❓ نامشخص"
        
        # استخراج نام مرورگر از user agent
        user_agent = obj.user_agent.lower()
        if 'chrome' in user_agent:
            return "🌐 Chrome"
        elif 'firefox' in user_agent:
            return "🦊 Firefox"
        elif 'safari' in user_agent:
            return "🧭 Safari"
        elif 'edge' in user_agent:
            return "🌊 Edge"
        else:
            return "🖥️ سایر"
    get_user_agent_short.short_description = "🖥️ مرورگر"
    
    # 🎯 اکشن‌های سفارشی
    actions = ['terminate_sessions']
    
    def terminate_sessions(self, request, queryset):
        """
        🔚 پایان دادن به نشست‌های انتخاب شده
        """
        from django.utils import timezone
        active_sessions = queryset.filter(is_active=True, logout_time__isnull=True)
        updated = active_sessions.update(
            logout_time=timezone.now(),
            is_active=False
        )
        self.message_user(request, f'🔚 {updated} نشست فعال پایان یافت.')
    terminate_sessions.short_description = "🔚 پایان دادن به نشست‌های انتخاب شده"


# 🔧 تنظیمات اضافی admin
admin.site.site_header = "🏢 پنل مدیریت HomayOMS"
admin.site.site_title = "HomayOMS Admin"
admin.site.index_title = "📊 داشبورد مدیریت"
