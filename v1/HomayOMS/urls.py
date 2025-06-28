"""
🌐 URL configuration برای پروژه HomayOMS
🔗 مسیریابی اصلی سیستم
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_redirect(request):
    """هدایت صفحه اصلی به داشبورد"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return redirect('accounts:login')

urlpatterns = [
    # 🎛️ پنل مدیریت جنگو
    path('admin/', admin.site.urls),
    
    # 🔐 اپلیکیشن حساب‌های کاربری
    path('accounts/', include('accounts.urls')),
    
    # 🏢 اپلیکیشن اصلی کسب‌وکار
    path('core/', include('core.urls')),
    
    # 🏠 صفحه اصلی
    path('', home_redirect, name='home'),
]

# 📁 سرو فایل‌های رسانه‌ای در حالت توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
