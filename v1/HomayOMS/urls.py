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
    """هدایت صفحه اصلی به لندینگ پیج محصولات"""
    return redirect('core:products_landing')

urlpatterns = [
    # 🎛️ پنل مدیریت جنگو (مسیر امنیتی)
    path('DJsecretAdmin/', admin.site.urls),
    
    # 🔐 اپلیکیشن حساب‌های کاربری
    path('accounts/', include('accounts.urls')),
    
    # 🏢 اپلیکیشن اصلی کسب‌وکار
    path('core/', include('core.urls')),
    
    # 💳 سیستم پرداخت
    path('payments/', include('payments.urls')),
    
    # 🏠 صفحه اصلی
    path('', home_redirect, name='home'),
]

# 📁 سرو فایل‌های رسانه‌ای در حالت توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 🚨 تعریف handler های خطا
handler404 = 'HomayOMS.views.handler404'
handler500 = 'HomayOMS.views.handler500'
handler403 = 'HomayOMS.views.handler403'
handler400 = 'HomayOMS.views.handler400'
