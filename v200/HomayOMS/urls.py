"""
🌐 URL configuration برای پروژه HomayOMS
🔗 مسیریابی اصلی سیستم
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

# def home_redirect(request):
#     """هدایت صفحه اصلی به لندینگ پیج محصولات"""
#     return redirect('core:products_landing')

urlpatterns = [
    # 🎛️ پنل مدیریت جنگو (مسیر امنیتی)
    path('DJsecretAdmin/', admin.site.urls),
    
    # 🔐 اپلیکیشن حساب‌های کاربری
    path('accounts/', include('accounts.urls')),
    
    # 🏢 اپلیکیشن اصلی کسب‌وکار
    path('core/', include('core.urls')),
    
    # 💳 سیستم پرداخت
    path('payments/', include('payments.urls')),
    
    # 🔄 همگام‌سازی موجودی
    path('inventory-sync/', include('inventory_sync.urls')),
    
    # 🏠 صفحه اصلی
    # 🏠 صفحه اصلی کارخانه کاغذ و مقوای همایون
    path('', views.index_view, name='index'),
]

# 📁 سرو فایل‌های رسانه‌ای و استاتیک در حالت توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # تصحیح: استفاده از STATICFILES_DIRS برای development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# 🚨 تعریف handler های خطا
handler404 = 'HomayOMS.views.handler404'
handler500 = 'HomayOMS.views.handler500'
handler403 = 'HomayOMS.views.handler403'
handler400 = 'HomayOMS.views.handler400'
